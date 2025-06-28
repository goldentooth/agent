"""Rate limiting and DoS protection system.

This module provides enterprise-grade rate limiting to protect against:
- Denial of Service (DoS) attacks
- Brute force attacks
- API abuse and resource exhaustion
- Excessive request patterns

Supports multiple algorithms and storage backends for flexible deployment.
"""

from __future__ import annotations

import asyncio
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Callable, Optional
from functools import wraps


class RateLimitError(Exception):
    """Exception raised when rate limit is exceeded."""
    
    def __init__(
        self,
        message: str,
        retry_after: Optional[float] = None,
        remaining: int = 0,
        reset_time: Optional[float] = None
    ):
        super().__init__(message)
        self.retry_after = retry_after
        self.remaining = remaining
        self.reset_time = reset_time


@dataclass
class RateLimitConfig:
    """Configuration for rate limiting system."""
    
    # Rate limits
    requests_per_minute: int = 100
    requests_per_hour: int = 1000
    burst_capacity: int = 10
    
    # Window configuration
    window_size_seconds: int = 60
    
    # Algorithm selection
    algorithm: str = "token_bucket"  # token_bucket, sliding_window, fixed_window
    
    # Per-user/IP limiting
    enable_per_ip_limiting: bool = True
    enable_per_user_limiting: bool = True
    
    # Storage backend
    store_type: str = "memory"  # memory, redis
    redis_url: Optional[str] = None


@dataclass
class RateLimitResult:
    """Result of a rate limit check."""
    
    allowed: bool
    remaining: int
    reset_time: float
    retry_after: Optional[float] = None


class RateLimitStore(ABC):
    """Abstract base class for rate limit storage backends."""
    
    @abstractmethod
    async def get(self, key: str) -> Optional[dict[str, Any]]:
        """Get data for a key."""
        pass
    
    @abstractmethod
    async def set(self, key: str, data: dict[str, Any], ttl: Optional[float] = None) -> None:
        """Set data for a key with optional TTL."""
        pass
    
    @abstractmethod
    async def increment(self, key: str, ttl: Optional[float] = None) -> int:
        """Increment a counter and return new value."""
        pass
    
    @abstractmethod
    async def delete(self, key: str) -> None:
        """Delete a key."""
        pass


class MemoryRateLimitStore(RateLimitStore):
    """In-memory rate limit store with TTL support."""
    
    def __init__(self, cleanup_interval: float = 60.0):
        self._data: dict[str, tuple[dict[str, Any], float]] = {}
        self._cleanup_interval = cleanup_interval
        self._last_cleanup = time.time()
    
    async def _cleanup_expired(self, force: bool = False) -> None:
        """Remove expired entries."""
        current_time = time.time()
        if not force and current_time - self._last_cleanup < self._cleanup_interval:
            return
        
        # Force cleanup of expired entries
        expired_keys = [
            key for key, (_, expiry) in self._data.items()
            if expiry > 0 and current_time > expiry
        ]
        
        for key in expired_keys:
            del self._data[key]
        
        self._last_cleanup = current_time
    
    async def force_cleanup(self) -> None:
        """Force cleanup of expired entries."""
        await self._cleanup_expired(force=True)
    
    async def get(self, key: str) -> Optional[dict[str, Any]]:
        """Get data for a key."""
        await self._cleanup_expired()
        
        if key not in self._data:
            return None
        
        data, expiry = self._data[key]
        if expiry > 0 and time.time() > expiry:
            del self._data[key]
            return None
        
        return data.copy()
    
    async def set(self, key: str, data: dict[str, Any], ttl: Optional[float] = None) -> None:
        """Set data for a key with optional TTL."""
        expiry = time.time() + ttl if ttl else 0
        self._data[key] = (data.copy(), expiry)
        # Always cleanup after setting to ensure TTL behavior
        await self._cleanup_expired()
    
    async def increment(self, key: str, ttl: Optional[float] = None) -> int:
        """Increment a counter and return new value."""
        current_data = await self.get(key)
        if current_data is None:
            new_value = 1
            await self.set(key, {"count": new_value}, ttl)
        else:
            new_value = current_data.get("count", 0) + 1
            current_data["count"] = new_value
            await self.set(key, current_data, ttl)
        
        return new_value
    
    async def delete(self, key: str) -> None:
        """Delete a key."""
        if key in self._data:
            del self._data[key]


class RateLimiter(ABC):
    """Abstract base class for rate limiting algorithms."""
    
    def __init__(self, config: RateLimitConfig, store: Optional[RateLimitStore] = None):
        self.config = config
        self.store = store or MemoryRateLimitStore()
    
    @abstractmethod
    async def check_rate_limit(self, key: str) -> RateLimitResult:
        """Check if request is allowed under rate limit."""
        pass


class TokenBucketLimiter(RateLimiter):
    """Token bucket rate limiting algorithm."""
    
    def __init__(self, config: RateLimitConfig, store: Optional[RateLimitStore] = None):
        super().__init__(config, store)
        self.bucket_capacity = config.burst_capacity
        self.refill_rate = config.requests_per_minute / 60.0  # tokens per second
    
    async def check_rate_limit(self, key: str) -> RateLimitResult:
        """Check rate limit using token bucket algorithm."""
        try:
            current_time = time.time()
            bucket_key = f"bucket:{key}"
            
            # Get current bucket state
            bucket_data = await self.store.get(bucket_key)
            
            if bucket_data is None:
                # Initialize bucket
                tokens = self.bucket_capacity - 1  # Take one token
                last_refill = current_time
            else:
                tokens = bucket_data["tokens"]
                last_refill = bucket_data["last_refill"]
                
                # Calculate tokens to add based on time elapsed
                time_elapsed = current_time - last_refill
                tokens_to_add = time_elapsed * self.refill_rate
                tokens = min(self.bucket_capacity, tokens + tokens_to_add)
                
                # Try to consume a token
                if tokens >= 1:
                    tokens -= 1
                else:
                    # Rate limited
                    retry_after = (1 - tokens) / self.refill_rate
                    return RateLimitResult(
                        allowed=False,
                        remaining=0,
                        reset_time=current_time + retry_after,
                        retry_after=retry_after
                    )
            
            # Update bucket state
            await self.store.set(
                bucket_key,
                {"tokens": tokens, "last_refill": current_time},
                ttl=300  # 5 minute TTL
            )
            
            return RateLimitResult(
                allowed=True,
                remaining=int(tokens),
                reset_time=current_time + (self.bucket_capacity - tokens) / self.refill_rate
            )
            
        except Exception as e:
            # Fail open in case of store errors
            raise RateLimitError(f"Rate limiting error: {e}") from e


class SlidingWindowLimiter(RateLimiter):
    """Sliding window rate limiting algorithm."""
    
    async def check_rate_limit(self, key: str) -> RateLimitResult:
        """Check rate limit using sliding window algorithm."""
        try:
            current_time = time.time()
            window_key = f"window:{key}"
            window_start = current_time - self.config.window_size_seconds
            
            # Get current request timestamps
            window_data = await self.store.get(window_key)
            timestamps = window_data.get("timestamps", []) if window_data else []
            
            # Remove expired timestamps
            timestamps = [ts for ts in timestamps if ts > window_start]
            
            # Check if we can add another request
            if len(timestamps) >= self.config.requests_per_minute:
                # Rate limited
                oldest_timestamp = min(timestamps)
                retry_after = (oldest_timestamp + self.config.window_size_seconds) - current_time
                return RateLimitResult(
                    allowed=False,
                    remaining=0,
                    reset_time=oldest_timestamp + self.config.window_size_seconds,
                    retry_after=max(0, retry_after)
                )
            
            # Add current timestamp
            timestamps.append(current_time)
            
            # Update window
            await self.store.set(
                window_key,
                {"timestamps": timestamps},
                ttl=self.config.window_size_seconds * 2
            )
            
            return RateLimitResult(
                allowed=True,
                remaining=self.config.requests_per_minute - len(timestamps),
                reset_time=current_time + self.config.window_size_seconds
            )
            
        except Exception as e:
            raise RateLimitError(f"Rate limiting error: {e}") from e


class FixedWindowLimiter(RateLimiter):
    """Fixed window rate limiting algorithm."""
    
    async def check_rate_limit(self, key: str) -> RateLimitResult:
        """Check rate limit using fixed window algorithm."""
        try:
            current_time = time.time()
            window_start = int(current_time // self.config.window_size_seconds) * self.config.window_size_seconds
            window_key = f"fixed_window:{key}:{window_start}"
            
            # Get current count for this window
            count_data = await self.store.get(window_key)
            current_count = count_data.get("count", 0) if count_data else 0
            
            # Check if we're at the limit
            if current_count >= self.config.requests_per_minute:
                # Rate limited
                window_end = window_start + self.config.window_size_seconds
                retry_after = window_end - current_time
                return RateLimitResult(
                    allowed=False,
                    remaining=0,
                    reset_time=window_end,
                    retry_after=retry_after
                )
            
            # Increment counter
            new_count = current_count + 1
            await self.store.set(
                window_key,
                {"count": new_count},
                ttl=self.config.window_size_seconds * 2
            )
            
            return RateLimitResult(
                allowed=True,
                remaining=self.config.requests_per_minute - new_count,
                reset_time=window_start + self.config.window_size_seconds
            )
            
        except Exception as e:
            raise RateLimitError(f"Rate limiting error: {e}") from e


# Factory function
def create_rate_limiter(config: RateLimitConfig, store: Optional[RateLimitStore] = None) -> RateLimiter:
    """Create a rate limiter based on configuration."""
    if config.algorithm == "token_bucket":
        return TokenBucketLimiter(config, store)
    elif config.algorithm == "sliding_window":
        return SlidingWindowLimiter(config, store)
    elif config.algorithm == "fixed_window":
        return FixedWindowLimiter(config, store)
    else:
        raise ValueError(f"Unknown rate limiting algorithm: {config.algorithm}")


# Global rate limiter instance
_global_limiter: Optional[RateLimiter] = None


def get_global_limiter() -> RateLimiter:
    """Get or create the global rate limiter."""
    global _global_limiter
    if _global_limiter is None:
        config = RateLimitConfig()
        _global_limiter = create_rate_limiter(config)
    return _global_limiter


async def check_rate_limit(key: str) -> RateLimitResult:
    """Check rate limit using the global limiter."""
    return await get_global_limiter().check_rate_limit(key)


def rate_limit_decorator(
    config: RateLimitConfig,
    key_func: Optional[Callable[..., str]] = None
) -> Callable[[Callable], Callable]:
    """Decorator to apply rate limiting to async functions."""
    # Create limiter once per decorator instance
    limiter = create_rate_limiter(config)
    
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            # Generate rate limit key
            if key_func:
                key = key_func(*args, **kwargs)
            else:
                # Default key based on function name and first argument
                key = f"{func.__name__}:{args[0] if args else 'default'}"
            
            # Check rate limit
            result = await limiter.check_rate_limit(key)
            
            if not result.allowed:
                raise RateLimitError(
                    "Rate limit exceeded",
                    retry_after=result.retry_after,
                    remaining=result.remaining,
                    reset_time=result.reset_time
                )
            
            # Execute function if allowed
            return await func(*args, **kwargs)
        
        return wrapper
    return decorator