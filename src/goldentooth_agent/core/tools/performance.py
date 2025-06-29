"""Performance optimization utilities for tools and workflows."""

from __future__ import annotations

import asyncio
import functools
import time
from collections import defaultdict
from collections.abc import AsyncGenerator, Callable, Coroutine
from contextlib import asynccontextmanager
from typing import Any, TypeVar

import httpx

# Type variables for generic caching
T = TypeVar("T")
R = TypeVar("R")

# Enhanced HTTP client management with multiple pools
_http_clients: dict[str, httpx.AsyncClient] = {}
_http_client_lock = asyncio.Lock()
_default_pool_config = {
    "timeout": 30.0,
    "max_keepalive_connections": 20,
    "max_connections": 100,
    "keepalive_expiry": 30.0,
}
_pool_configs: dict[str, dict[str, Any]] = {}

# Simple memory cache
_cache: dict[str, tuple[Any, float, float]] = {}  # key -> (value, timestamp, ttl)
_cache_stats: defaultdict[str, int] = defaultdict(int)
_cache_lock = asyncio.Lock()


async def get_http_client(pool_name: str = "default") -> httpx.AsyncClient:
    """Get a shared HTTP client with connection pooling for a specific pool."""
    async with _http_client_lock:
        if pool_name not in _http_clients:
            # Get pool configuration
            pool_config = _pool_configs.get(pool_name, _default_pool_config)

            # Create client with pool-specific settings
            _http_clients[pool_name] = httpx.AsyncClient(
                timeout=pool_config["timeout"],
                limits=httpx.Limits(
                    max_keepalive_connections=pool_config["max_keepalive_connections"],
                    max_connections=pool_config["max_connections"],
                    keepalive_expiry=pool_config["keepalive_expiry"],
                ),
                follow_redirects=True,
                # Note: http2=True requires h2 package, disabled for now
            )

    return _http_clients[pool_name]


async def close_http_client(pool_name: str | None = None) -> None:
    """Close HTTP clients for a specific pool or all pools."""
    async with _http_client_lock:
        if pool_name:
            # Close specific pool
            if pool_name in _http_clients:
                await _http_clients[pool_name].aclose()
                del _http_clients[pool_name]
        else:
            # Close all pools
            for client in _http_clients.values():
                await client.aclose()
            _http_clients.clear()


def cache_key(*args: Any, **kwargs: Any) -> str:
    """Generate a cache key from function arguments."""
    # Simple cache key generation - in production, use more robust hashing
    key_parts = []

    for arg in args:
        if hasattr(arg, "model_dump"):
            # Pydantic models
            key_parts.append(str(arg.model_dump()))
        else:
            key_parts.append(str(arg))

    for k, v in sorted(kwargs.items()):
        key_parts.append(f"{k}={v}")

    return "|".join(key_parts)


async def get_from_cache(key: str) -> tuple[bool, Any]:
    """Get value from cache, returning (found, value)."""
    async with _cache_lock:
        _cache_stats["requests"] += 1

        if key in _cache:
            value, timestamp, ttl = _cache[key]

            # Check if expired
            if time.time() - timestamp <= ttl:
                _cache_stats["hits"] += 1
                return True, value
            else:
                # Remove expired entry
                del _cache[key]
                _cache_stats["expired"] += 1

        _cache_stats["misses"] += 1
        return False, None


async def set_in_cache(key: str, value: Any, ttl: float = 300.0) -> None:
    """Set value in cache with TTL in seconds."""
    async with _cache_lock:
        _cache[key] = (value, time.time(), ttl)
        _cache_stats["sets"] += 1

        # Simple cache size management
        if len(_cache) > 1000:  # Max 1000 entries
            # Remove oldest 20% of entries
            sorted_keys = sorted(_cache.keys(), key=lambda k: _cache[k][1])
            for old_key in sorted_keys[:200]:
                del _cache[old_key]
            _cache_stats["evictions"] += 200


async def clear_cache() -> None:
    """Clear the entire cache."""
    async with _cache_lock:
        _cache.clear()
        _cache_stats["clears"] += 1


async def get_cache_stats() -> dict[str, Any]:
    """Get cache statistics."""
    async with _cache_lock:
        stats = dict(_cache_stats)
        stats["size"] = len(_cache)
        stats["hit_rate"] = (
            stats["hits"] / stats["requests"] if stats["requests"] > 0 else 0.0
        )
        return stats


def async_cache(
    ttl: float = 300.0, use_args: bool = True, use_kwargs: bool = True
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Decorator for caching async function results."""

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            # Generate cache key
            if use_args and use_kwargs:
                key = f"{func.__name__}:{cache_key(*args, **kwargs)}"
            elif use_args:
                key = f"{func.__name__}:{cache_key(*args)}"
            elif use_kwargs:
                key = f"{func.__name__}:{cache_key(**kwargs)}"
            else:
                key = func.__name__

            # Try to get from cache
            found, cached_value = await get_from_cache(key)
            if found:
                return cached_value

            # Execute function and cache result
            result = await func(*args, **kwargs)
            await set_in_cache(key, result, ttl)

            return result

        return wrapper

    return decorator


def batch_processor(
    batch_size: int = 10, timeout: float = 1.0
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Decorator for batching async operations."""

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        pending_items: list[tuple[Any, asyncio.Future[Any]]] = []
        process_lock = asyncio.Lock()

        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            future: asyncio.Future[Any] = asyncio.Future()

            async with process_lock:
                pending_items.append((args, future))

                # Process batch if we have enough items or this is the first item
                should_process = (
                    len(pending_items) >= batch_size or len(pending_items) == 1
                )

            if should_process:
                # Start batch processing
                asyncio.create_task(_process_batch(func, pending_items.copy(), timeout))
                pending_items.clear()

            return await future

        async def _process_batch(
            batch_func: Callable[..., Any],
            items: list[tuple[Any, asyncio.Future[Any]]],
            batch_timeout: float,
        ) -> None:
            """Process a batch of items."""
            try:
                # Wait for all items with timeout
                tasks = [batch_func(*item_args) for item_args, _ in items]
                results = await asyncio.wait_for(
                    asyncio.gather(*tasks, return_exceptions=True),
                    timeout=batch_timeout,
                )

                # Set results
                for (_, future), result in zip(items, results, strict=False):
                    if isinstance(result, Exception):
                        future.set_exception(result)
                    else:
                        future.set_result(result)

            except TimeoutError:
                # Set timeout exceptions for all items
                for _, future in items:
                    future.set_exception(TimeoutError("Batch processing timeout"))
            except Exception as e:
                # Set exception for all items
                for _, future in items:
                    future.set_exception(e)

        return wrapper

    return decorator


class PerformanceMonitor:
    """Monitor performance metrics for tools and operations."""

    def __init__(self) -> None:
        self.metrics: dict[str, list[float]] = defaultdict(list)
        self.counters: dict[str, int] = defaultdict(int)
        self.lock = asyncio.Lock()

    async def record_execution_time(self, operation: str, duration: float) -> None:
        """Record execution time for an operation."""
        async with self.lock:
            self.metrics[f"{operation}_duration"].append(duration)
            self.counters[f"{operation}_count"] += 1

            # Keep only last 1000 measurements per operation
            if len(self.metrics[f"{operation}_duration"]) > 1000:
                self.metrics[f"{operation}_duration"] = self.metrics[
                    f"{operation}_duration"
                ][-1000:]

    async def increment_counter(self, counter: str, value: int = 1) -> None:
        """Increment a counter."""
        async with self.lock:
            self.counters[counter] += value

    async def get_stats(self) -> dict[str, Any]:
        """Get performance statistics."""
        async with self.lock:
            stats = {}

            # Calculate duration statistics
            for key, durations in self.metrics.items():
                if durations:
                    stats[key] = {
                        "count": len(durations),
                        "avg": sum(durations) / len(durations),
                        "min": min(durations),
                        "max": max(durations),
                        "total": sum(durations),
                    }

            # Add counters
            stats["counters"] = dict(self.counters)

            return stats

    def timed(
        self, operation: str
    ) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        """Decorator for timing operations."""

        def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
            @functools.wraps(func)
            async def wrapper(*args: Any, **kwargs: Any) -> Any:
                start_time = time.time()
                try:
                    result = await func(*args, **kwargs)
                    return result
                finally:
                    duration = time.time() - start_time
                    await self.record_execution_time(operation, duration)

            return wrapper

        return decorator


# Global performance monitor
performance_monitor = PerformanceMonitor()


def parallel_execute(
    max_concurrent: int = 10,
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Decorator for limiting concurrent executions."""
    semaphore = asyncio.Semaphore(max_concurrent)

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            async with semaphore:
                return await func(*args, **kwargs)

        return wrapper

    return decorator


async def warmup_http_client() -> None:
    """Warm up the HTTP client connection pool."""
    client = await get_http_client()

    # Make a few test requests to establish connections
    test_urls = [
        "https://httpbin.org/status/200",
        "https://jsonplaceholder.typicode.com/posts/1",
    ]

    tasks = []
    for url in test_urls:
        try:
            task = client.get(url, timeout=5.0)
            tasks.append(task)
        except Exception:
            # Ignore warmup failures
            pass

    if tasks:
        try:
            await asyncio.gather(*tasks, return_exceptions=True)
        except Exception:
            # Ignore warmup failures
            pass


def configure_http_pool(
    pool_name: str,
    timeout: float = 30.0,
    max_keepalive_connections: int = 20,
    max_connections: int = 100,
    keepalive_expiry: float = 30.0,
) -> None:
    """Configure HTTP client pool settings."""
    _pool_configs[pool_name] = {
        "timeout": timeout,
        "max_keepalive_connections": max_keepalive_connections,
        "max_connections": max_connections,
        "keepalive_expiry": keepalive_expiry,
    }


@asynccontextmanager
async def http_client_context(
    pool_name: str = "default",
) -> AsyncGenerator[httpx.AsyncClient]:
    """Context manager for HTTP client lifecycle."""
    client = await get_http_client(pool_name)
    try:
        yield client
    finally:
        # Client cleanup is handled by the global pool manager
        pass


class ResourcePool:
    """Generic resource pool with lifecycle management."""

    def __init__(self, max_size: int = 10, idle_timeout: float = 300.0):
        self.max_size = max_size
        self.idle_timeout = idle_timeout
        self._pool: list[tuple[Any, float]] = []  # (resource, last_used)
        self._lock = asyncio.Lock()
        self._created_count = 0

    async def acquire(self, factory: Callable[[], Coroutine[Any, Any, Any]]) -> Any:
        """Acquire a resource from the pool or create new one."""
        async with self._lock:
            now = time.time()

            # Remove expired resources
            self._pool = [
                (resource, last_used)
                for resource, last_used in self._pool
                if now - last_used < self.idle_timeout
            ]

            # Try to get existing resource
            if self._pool:
                resource, _ = self._pool.pop(0)
                return resource

            # Create new resource if under limit
            if self._created_count < self.max_size:
                self._created_count += 1
                return await factory()

            # Wait and retry if pool is full
            await asyncio.sleep(0.1)
            return await self.acquire(factory)

    async def release(self, resource: Any) -> None:
        """Release a resource back to the pool."""
        async with self._lock:
            self._pool.append((resource, time.time()))

    async def close(self) -> None:
        """Close all resources in the pool."""
        async with self._lock:
            for resource, _ in self._pool:
                if hasattr(resource, "aclose"):
                    await resource.aclose()
                elif hasattr(resource, "close"):
                    resource.close()
            self._pool.clear()
            self._created_count = 0


# Global resource pools
_resource_pools: dict[str, ResourcePool] = {}
_resource_pool_lock = asyncio.Lock()


async def get_resource_pool(
    name: str, max_size: int = 10, idle_timeout: float = 300.0
) -> ResourcePool:
    """Get or create a resource pool."""
    async with _resource_pool_lock:
        if name not in _resource_pools:
            _resource_pools[name] = ResourcePool(max_size, idle_timeout)
        return _resource_pools[name]


async def cleanup_performance_resources() -> None:
    """Clean up performance-related resources."""
    await close_http_client()
    await clear_cache()

    # Clean up resource pools
    async with _resource_pool_lock:
        for pool in _resource_pools.values():
            await pool.close()
        _resource_pools.clear()
