"""Intelligent caching system for expensive operations with adaptive strategies."""

from __future__ import annotations

import asyncio
import hashlib
import json
import pickle
import time
from collections import OrderedDict, defaultdict
from collections.abc import Callable
from contextlib import asynccontextmanager
from dataclasses import dataclass
from enum import Enum
from typing import Any, TypeVar
from collections.abc import AsyncGenerator

from ..flow_agent import FlowIOSchema

T = TypeVar("T")
R = TypeVar("R")


class CacheStrategy(Enum):
    """Cache eviction strategies."""

    LRU = "lru"  # Least Recently Used
    LFU = "lfu"  # Least Frequently Used
    TTL = "ttl"  # Time To Live
    ADAPTIVE = "adaptive"  # Adaptive based on usage patterns


class CacheMetrics:
    """Track cache performance metrics."""

    def __init__(self):
        self.hits = 0
        self.misses = 0
        self.evictions = 0
        self.sets = 0
        self.errors = 0
        self.total_access_time = 0.0
        self.total_computation_time = 0.0
        self.key_access_count: defaultdict[str, int] = defaultdict(int)
        self.key_last_access: dict[str, float] = {}

    @property
    def hit_rate(self) -> float:
        total = self.hits + self.misses
        return self.hits / total if total > 0 else 0.0

    @property
    def avg_access_time(self) -> float:
        total_ops = self.hits + self.misses
        return self.total_access_time / total_ops if total_ops > 0 else 0.0

    def record_hit(self, key: str, access_time: float) -> None:
        self.hits += 1
        self.total_access_time += access_time
        self.key_access_count[key] += 1
        self.key_last_access[key] = time.time()

    def record_miss(self, key: str, computation_time: float) -> None:
        self.misses += 1
        self.total_computation_time += computation_time
        self.key_access_count[key] += 1
        self.key_last_access[key] = time.time()

    def record_set(self, key: str) -> None:
        self.sets += 1
        self.key_last_access[key] = time.time()

    def record_eviction(self, key: str) -> None:
        self.evictions += 1
        self.key_access_count.pop(key, None)
        self.key_last_access.pop(key, None)

    def record_error(self) -> None:
        self.errors += 1

    def get_stats(self) -> dict[str, Any]:
        return {
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate": self.hit_rate,
            "evictions": self.evictions,
            "sets": self.sets,
            "errors": self.errors,
            "avg_access_time_ms": self.avg_access_time * 1000,
            "total_keys": len(self.key_access_count),
            "most_accessed_keys": dict(
                sorted(self.key_access_count.items(), key=lambda x: x[1], reverse=True)[
                    :10
                ]
            ),
        }


@dataclass
class CacheEntry:
    """Cache entry with metadata."""

    value: Any
    created_at: float
    last_accessed: float
    access_count: int
    ttl: float | None = None
    size_bytes: int = 0

    @property
    def is_expired(self) -> bool:
        if self.ttl is None:
            return False
        return time.time() - self.created_at > self.ttl

    @property
    def age(self) -> float:
        return time.time() - self.created_at

    def touch(self) -> None:
        self.last_accessed = time.time()
        self.access_count += 1


class IntelligentCache:
    """Intelligent cache with adaptive strategies and performance optimization."""

    def __init__(
        self,
        max_size: int = 1000,
        default_ttl: float | None = 3600.0,  # 1 hour
        strategy: CacheStrategy = CacheStrategy.ADAPTIVE,
        max_memory_mb: int = 100,
    ):
        self.max_size = max_size
        self.default_ttl = default_ttl
        self.strategy = strategy
        self.max_memory_bytes = max_memory_mb * 1024 * 1024

        self._cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self._lock = asyncio.Lock()
        self.metrics = CacheMetrics()

        # Adaptive strategy parameters
        self._strategy_scores: dict[CacheStrategy, float] = {
            strategy: 1.0
            for strategy in CacheStrategy
            if strategy != CacheStrategy.ADAPTIVE
        }
        self._current_strategy = CacheStrategy.LRU
        self._strategy_switch_interval = 100  # operations
        self._operations_since_switch = 0

    async def get(self, key: str) -> tuple[bool, Any]:
        """Get value from cache."""
        start_time = time.time()

        async with self._lock:
            if key in self._cache:
                entry = self._cache[key]

                # Check expiration
                if entry.is_expired:
                    del self._cache[key]
                    self.metrics.record_eviction(key)
                    self.metrics.record_miss(key, 0.0)
                    return False, None

                # Update access info
                entry.touch()

                # Move to end for LRU
                self._cache.move_to_end(key)

                access_time = time.time() - start_time
                self.metrics.record_hit(key, access_time)

                return True, entry.value

            miss_time = time.time() - start_time
            self.metrics.record_miss(key, miss_time)
            return False, None

    async def set(
        self,
        key: str,
        value: Any,
        ttl: float | None = None,
    ) -> None:
        """Set value in cache with intelligent eviction."""
        async with self._lock:
            # Calculate size
            try:
                size_bytes = len(pickle.dumps(value))
            except Exception:
                size_bytes = 0

            # Create entry
            entry = CacheEntry(
                value=value,
                created_at=time.time(),
                last_accessed=time.time(),
                access_count=1,
                ttl=ttl or self.default_ttl,
                size_bytes=size_bytes,
            )

            # Add to cache
            self._cache[key] = entry
            self.metrics.record_set(key)

            # Evict if necessary
            await self._evict_if_needed()

            # Update adaptive strategy
            self._operations_since_switch += 1
            if self._operations_since_switch >= self._strategy_switch_interval:
                await self._update_adaptive_strategy()

    async def delete(self, key: str) -> bool:
        """Delete key from cache."""
        async with self._lock:
            if key in self._cache:
                del self._cache[key]
                self.metrics.record_eviction(key)
                return True
            return False

    async def clear(self) -> None:
        """Clear entire cache."""
        async with self._lock:
            self._cache.clear()
            # Reset metrics except for historical data
            self.metrics.key_access_count.clear()
            self.metrics.key_last_access.clear()

    async def _evict_if_needed(self) -> None:
        """Evict entries based on current strategy."""
        # Check size limits
        while (
            len(self._cache) > self.max_size
            or self._get_total_memory_usage() > self.max_memory_bytes
        ):
            if not self._cache:
                break

            # Choose eviction strategy
            if self.strategy == CacheStrategy.ADAPTIVE:
                strategy = self._current_strategy
            else:
                strategy = self.strategy

            # Evict based on strategy
            if strategy == CacheStrategy.LRU:
                key_to_evict = next(iter(self._cache))
            elif strategy == CacheStrategy.LFU:
                key_to_evict = min(
                    self._cache.keys(), key=lambda k: self._cache[k].access_count
                )
            elif strategy == CacheStrategy.TTL:
                # Evict expired first, then oldest
                now = time.time()
                expired_keys = [
                    k
                    for k, entry in self._cache.items()
                    if entry.ttl and now - entry.created_at > entry.ttl
                ]
                if expired_keys:
                    key_to_evict = expired_keys[0]
                else:
                    key_to_evict = min(
                        self._cache.keys(), key=lambda k: self._cache[k].created_at
                    )
            else:
                # Default to LRU
                key_to_evict = next(iter(self._cache))

            del self._cache[key_to_evict]
            self.metrics.record_eviction(key_to_evict)

    def _get_total_memory_usage(self) -> int:
        """Calculate total memory usage of cache."""
        return sum(entry.size_bytes for entry in self._cache.values())

    async def _update_adaptive_strategy(self) -> None:
        """Update adaptive strategy based on performance."""
        if self.strategy != CacheStrategy.ADAPTIVE:
            return

        current_hit_rate = self.metrics.hit_rate

        # Update score for current strategy
        self._strategy_scores[self._current_strategy] = (
            self._strategy_scores[self._current_strategy] * 0.9 + current_hit_rate * 0.1
        )

        # Choose best strategy
        best_strategy = max(
            self._strategy_scores.keys(), key=lambda s: self._strategy_scores[s]
        )

        if best_strategy != self._current_strategy:
            self._current_strategy = best_strategy

        self._operations_since_switch = 0

    async def get_stats(self) -> dict[str, Any]:
        """Get comprehensive cache statistics."""
        async with self._lock:
            stats = self.metrics.get_stats()

            # Convert strategy scores to serializable format
            strategy_scores = None
            if self.strategy == CacheStrategy.ADAPTIVE:
                strategy_scores = {
                    s.value: score for s, score in self._strategy_scores.items()
                }

            stats.update(
                {
                    "size": len(self._cache),
                    "max_size": self.max_size,
                    "memory_usage_bytes": self._get_total_memory_usage(),
                    "max_memory_bytes": self.max_memory_bytes,
                    "memory_utilization": self._get_total_memory_usage()
                    / self.max_memory_bytes,
                    "strategy": self.strategy.value,
                    "current_adaptive_strategy": (
                        self._current_strategy.value
                        if self.strategy == CacheStrategy.ADAPTIVE
                        else None
                    ),
                    "strategy_scores": strategy_scores,
                }
            )
            return stats


class SmartCacheDecorator:
    """Smart caching decorator with automatic key generation."""

    def __init__(
        self,
        cache: IntelligentCache | None = None,
        ttl: float | None = None,
        key_func: Callable[..., str] | None = None,
    ):
        self.cache = cache or IntelligentCache()
        self.ttl = ttl
        self.key_func = key_func

    def __call__(self, func: Callable[..., Any]) -> Callable[..., Any]:
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            # Generate cache key
            if self.key_func:
                cache_key = self.key_func(*args, **kwargs)
            else:
                cache_key = self._generate_key(func, args, kwargs)

            # Try to get from cache
            found, cached_value = await self.cache.get(cache_key)
            if found:
                return cached_value

            # Execute function
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                computation_time = time.time() - start_time

                # Cache result
                await self.cache.set(cache_key, result, self.ttl)

                return result

            except Exception as e:
                self.cache.metrics.record_error()
                raise e

        return wrapper

    def _generate_key(self, func: Callable, args: tuple, kwargs: dict) -> str:
        """Generate cache key from function and arguments."""
        key_parts = [func.__name__]

        # Add args
        for arg in args:
            if hasattr(arg, "model_dump"):
                # Pydantic models
                key_parts.append(json.dumps(arg.model_dump(), sort_keys=True))
            elif isinstance(arg, (str, int, float, bool)):
                key_parts.append(str(arg))
            else:
                # Use hash for complex objects
                key_parts.append(str(hash(str(arg))))

        # Add kwargs
        for k, v in sorted(kwargs.items()):
            if hasattr(v, "model_dump"):
                key_parts.append(f"{k}={json.dumps(v.model_dump(), sort_keys=True)}")
            else:
                key_parts.append(f"{k}={v}")

        # Create hash of combined key
        key_string = "|".join(key_parts)
        return hashlib.sha256(key_string.encode()).hexdigest()


# Global cache instances
flow_cache = IntelligentCache(
    max_size=1000,
    default_ttl=3600.0,
    strategy=CacheStrategy.ADAPTIVE,
    max_memory_mb=50,
)

tool_cache = IntelligentCache(
    max_size=500,
    default_ttl=1800.0,  # 30 minutes
    strategy=CacheStrategy.LRU,
    max_memory_mb=25,
)

llm_cache = IntelligentCache(
    max_size=200,
    default_ttl=7200.0,  # 2 hours - LLM responses are expensive
    strategy=CacheStrategy.TTL,
    max_memory_mb=100,
)


# Convenience decorators
def cached_flow(ttl: float | None = None, cache: IntelligentCache | None = None):
    """Decorator for caching Flow operations."""
    return SmartCacheDecorator(cache or flow_cache, ttl)


def cached_tool(ttl: float | None = None, cache: IntelligentCache | None = None):
    """Decorator for caching tool operations."""
    return SmartCacheDecorator(cache or tool_cache, ttl)


def cached_llm(ttl: float | None = None, cache: IntelligentCache | None = None):
    """Decorator for caching LLM operations."""
    return SmartCacheDecorator(cache or llm_cache, ttl)


# Cache management utilities
@asynccontextmanager
async def cache_context(
    cache: IntelligentCache,
) -> AsyncGenerator[IntelligentCache]:
    """Context manager for cache lifecycle."""
    try:
        yield cache
    finally:
        # Optional cleanup - caches are persistent by design
        pass


async def get_all_cache_stats() -> dict[str, Any]:
    """Get statistics from all global caches."""
    return {
        "flow_cache": await flow_cache.get_stats(),
        "tool_cache": await tool_cache.get_stats(),
        "llm_cache": await llm_cache.get_stats(),
    }


async def clear_all_caches() -> None:
    """Clear all global caches."""
    await flow_cache.clear()
    await tool_cache.clear()
    await llm_cache.clear()


# Flow-specific caching utilities
class FlowCacheManager:
    """Specialized cache manager for Flow operations."""

    def __init__(self, cache: IntelligentCache | None = None):
        self.cache = cache or flow_cache

    async def cache_flow_result(
        self,
        flow_input: FlowIOSchema,
        flow_output: FlowIOSchema,
        flow_name: str,
        ttl: float | None = None,
    ) -> None:
        """Cache a flow execution result."""
        key = self._generate_flow_key(flow_name, flow_input)
        await self.cache.set(key, flow_output, ttl)

    async def get_cached_flow_result(
        self,
        flow_input: FlowIOSchema,
        flow_name: str,
    ) -> tuple[bool, FlowIOSchema | None]:
        """Get cached flow result."""
        key = self._generate_flow_key(flow_name, flow_input)
        found, result = await self.cache.get(key)
        return found, result

    def _generate_flow_key(self, flow_name: str, flow_input: FlowIOSchema) -> str:
        """Generate cache key for flow operation."""
        input_data = flow_input.model_dump()
        input_json = json.dumps(input_data, sort_keys=True)
        key_string = f"flow:{flow_name}:{input_json}"
        return hashlib.sha256(key_string.encode()).hexdigest()


# Global flow cache manager
flow_cache_manager = FlowCacheManager()
