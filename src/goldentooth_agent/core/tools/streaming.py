"""Advanced streaming patterns for memory-efficient processing."""

from __future__ import annotations

import asyncio
import gc
import sys
from collections.abc import AsyncIterator, Callable
from contextlib import asynccontextmanager
from typing import Any, TypeVar
from collections.abc import AsyncGenerator
from weakref import WeakSet

from ..flow_agent import FlowIOSchema

T = TypeVar("T")
R = TypeVar("R")


class StreamingConfig:
    """Configuration for streaming operations."""

    def __init__(
        self,
        chunk_size: int = 1000,
        buffer_size: int = 10000,
        memory_threshold_mb: int = 100,
        gc_interval: int = 1000,
        backpressure_threshold: float = 0.8,
    ):
        self.chunk_size = chunk_size
        self.buffer_size = buffer_size
        self.memory_threshold_bytes = memory_threshold_mb * 1024 * 1024
        self.gc_interval = gc_interval
        self.backpressure_threshold = backpressure_threshold


class MemoryMonitor:
    """Monitor memory usage and trigger cleanup when needed."""

    def __init__(self, config: StreamingConfig):
        self.config = config
        self.operation_count = 0
        self.peak_memory = 0
        self.current_memory = 0

    def check_memory(self) -> tuple[bool, int]:
        """Check current memory usage. Returns (should_gc, current_bytes)."""
        # Get current process memory usage (simplified)
        try:
            import psutil

            process = psutil.Process()
            memory_info = process.memory_info()
            self.current_memory = memory_info.rss
        except ImportError:
            # Fallback to sys.getsizeof approximation
            self.current_memory = sys.getsizeof(gc.get_objects())

        self.peak_memory = max(self.peak_memory, self.current_memory)
        should_gc = self.current_memory > self.config.memory_threshold_bytes

        return should_gc, self.current_memory

    def increment_operations(self) -> bool:
        """Increment operation count and check if GC should run."""
        self.operation_count += 1
        return self.operation_count % self.config.gc_interval == 0


class BackpressureController:
    """Control backpressure in streaming operations."""

    def __init__(self, config: StreamingConfig):
        self.config = config
        self.pending_operations = 0
        self.max_pending = int(config.buffer_size * config.backpressure_threshold)
        self._semaphore = asyncio.Semaphore(self.max_pending)

    @asynccontextmanager
    async def acquire(self) -> AsyncGenerator[None]:
        """Acquire a slot for processing with backpressure control."""
        await self._semaphore.acquire()
        self.pending_operations += 1
        try:
            yield
        finally:
            self.pending_operations -= 1
            self._semaphore.release()

    @property
    def is_under_pressure(self) -> bool:
        """Check if system is under backpressure."""
        return self.pending_operations >= self.max_pending


class StreamProcessor:
    """Memory-efficient stream processor with automatic resource management."""

    def __init__(self, config: StreamingConfig | None = None):
        self.config = config or StreamingConfig()
        self.memory_monitor = MemoryMonitor(self.config)
        self.backpressure = BackpressureController(self.config)
        self._active_streams: WeakSet[AsyncIterator[Any]] = WeakSet()

    async def chunk_stream(
        self, stream: AsyncIterator[T], chunk_size: int | None = None
    ) -> AsyncIterator[list[T]]:
        """Break stream into chunks for batch processing."""
        chunk_size = chunk_size or self.config.chunk_size
        chunk = []

        async for item in stream:
            chunk.append(item)

            if len(chunk) >= chunk_size:
                yield chunk
                chunk = []

                # Memory management
                if self.memory_monitor.increment_operations():
                    should_gc, memory_usage = self.memory_monitor.check_memory()
                    if should_gc:
                        gc.collect()

        # Yield remaining items
        if chunk:
            yield chunk

    async def buffer_stream(
        self, stream: AsyncIterator[T], buffer_size: int | None = None
    ) -> AsyncIterator[T]:
        """Buffer stream with memory-aware backpressure."""
        buffer_size = buffer_size or self.config.buffer_size
        buffer = []

        async for item in stream:
            async with self.backpressure.acquire():
                buffer.append(item)

                # Yield items when buffer is full or under memory pressure
                should_gc, _ = self.memory_monitor.check_memory()
                if len(buffer) >= buffer_size or should_gc:
                    for buffered_item in buffer:
                        yield buffered_item
                    buffer.clear()

                    if should_gc:
                        gc.collect()

        # Yield remaining buffered items
        for item in buffer:
            yield item

    async def map_stream(
        self,
        stream: AsyncIterator[T],
        mapper: Callable[[T], R] | Callable[[T], Callable[[], R]],
        chunk_size: int | None = None,
    ) -> AsyncIterator[R]:
        """Apply function to stream with chunked processing."""
        chunk_size = chunk_size or self.config.chunk_size

        async for chunk in self.chunk_stream(stream, chunk_size):
            # Process chunk
            results = []
            for item in chunk:
                try:
                    if asyncio.iscoroutinefunction(mapper):
                        result = await mapper(item)
                    else:
                        result = mapper(item)
                    results.append(result)
                except Exception:
                    # Skip failed items in streaming context
                    continue

            # Yield results
            for result in results:
                yield result

            # Memory cleanup
            del results, chunk

            if self.memory_monitor.increment_operations():
                should_gc, _ = self.memory_monitor.check_memory()
                if should_gc:
                    gc.collect()

    async def filter_stream(
        self,
        stream: AsyncIterator[T],
        predicate: Callable[[T], bool] | Callable[[T], Callable[[], bool]],
    ) -> AsyncIterator[T]:
        """Filter stream with memory management."""
        async for item in stream:
            try:
                if asyncio.iscoroutinefunction(predicate):
                    keep = await predicate(item)
                else:
                    keep = predicate(item)

                if keep:
                    yield item

            except Exception:
                # Skip items that cause filter errors
                continue

            if self.memory_monitor.increment_operations():
                should_gc, _ = self.memory_monitor.check_memory()
                if should_gc:
                    gc.collect()

    async def reduce_stream(
        self,
        stream: AsyncIterator[T],
        reducer: Callable[[R, T], R],
        initial: R,
        chunk_size: int | None = None,
    ) -> R:
        """Reduce stream with chunked processing to manage memory."""
        chunk_size = chunk_size or self.config.chunk_size
        accumulator = initial

        async for chunk in self.chunk_stream(stream, chunk_size):
            # Process chunk
            for item in chunk:
                try:
                    if asyncio.iscoroutinefunction(reducer):
                        accumulator = await reducer(accumulator, item)
                    else:
                        accumulator = reducer(accumulator, item)
                except Exception:
                    # Skip items that cause reducer errors
                    continue

            # Memory cleanup after each chunk
            del chunk

            if self.memory_monitor.increment_operations():
                should_gc, _ = self.memory_monitor.check_memory()
                if should_gc:
                    gc.collect()

        return accumulator

    @asynccontextmanager
    async def managed_stream(self, stream: AsyncIterator[T]):
        """Context manager for stream lifecycle with resource cleanup."""
        self._active_streams.add(stream)
        try:
            yield stream
        finally:
            try:
                self._active_streams.discard(stream)
                # Close stream if it has close method
                if hasattr(stream, "aclose"):
                    await stream.aclose()  # type: ignore[attr-defined]
                elif hasattr(stream, "close"):
                    stream.close()  # type: ignore[attr-defined]
            except Exception:
                # Ignore cleanup errors
                pass

    async def get_memory_stats(self) -> dict[str, Any]:
        """Get current memory and performance statistics."""
        should_gc, current_memory = self.memory_monitor.check_memory()

        return {
            "current_memory_bytes": current_memory,
            "peak_memory_bytes": self.memory_monitor.peak_memory,
            "memory_threshold_bytes": self.config.memory_threshold_bytes,
            "operation_count": self.memory_monitor.operation_count,
            "pending_operations": self.backpressure.pending_operations,
            "max_pending_operations": self.backpressure.max_pending,
            "under_backpressure": self.backpressure.is_under_pressure,
            "active_streams": len(self._active_streams),
            "should_gc": should_gc,
            "config": {
                "chunk_size": self.config.chunk_size,
                "buffer_size": self.config.buffer_size,
                "memory_threshold_mb": self.config.memory_threshold_bytes
                // (1024 * 1024),
                "gc_interval": self.config.gc_interval,
                "backpressure_threshold": self.config.backpressure_threshold,
            },
        }


# Global streaming processor
default_stream_processor = StreamProcessor()


async def create_memory_efficient_flow_stream(
    items: list[FlowIOSchema],
    chunk_size: int = 1000,
) -> AsyncIterator[FlowIOSchema]:
    """Create a memory-efficient stream from a list of FlowIOSchema items."""
    processor = StreamProcessor(StreamingConfig(chunk_size=chunk_size))

    async def item_generator() -> AsyncIterator[FlowIOSchema]:
        for item in items:
            yield item

    async with processor.managed_stream(item_generator()) as stream:
        async for item in processor.buffer_stream(stream):
            yield item


async def process_large_dataset(
    data_source: AsyncIterator[Any],
    processor_func: Callable[[Any], FlowIOSchema],
    chunk_size: int = 1000,
    max_memory_mb: int = 100,
) -> AsyncIterator[FlowIOSchema]:
    """Process large datasets with automatic memory management."""
    config = StreamingConfig(
        chunk_size=chunk_size,
        memory_threshold_mb=max_memory_mb,
    )
    stream_processor = StreamProcessor(config)

    async with stream_processor.managed_stream(data_source) as source:
        async for result in stream_processor.map_stream(source, processor_func):
            yield result
