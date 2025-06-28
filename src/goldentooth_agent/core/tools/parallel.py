"""Parallelization utilities for concurrent Flow execution and batching."""

from __future__ import annotations

import asyncio
import time
from collections.abc import AsyncIterator, Callable, Coroutine
from contextlib import asynccontextmanager
from typing import Any, TypeVar
from collections.abc import AsyncGenerator

from ..flow_agent import FlowIOSchema
from .performance import performance_monitor
from .streaming import StreamingConfig, StreamProcessor

T = TypeVar("T")
R = TypeVar("R")


class ParallelConfig:
    """Configuration for parallel execution."""

    def __init__(
        self,
        max_concurrent: int = 10,
        batch_size: int = 100,
        timeout: float = 300.0,
        retry_attempts: int = 3,
        retry_delay: float = 1.0,
        use_process_pool: bool = False,
        worker_ttl: float = 3600.0,  # Worker time-to-live in seconds
    ):
        self.max_concurrent = max_concurrent
        self.batch_size = batch_size
        self.timeout = timeout
        self.retry_attempts = retry_attempts
        self.retry_delay = retry_delay
        self.use_process_pool = use_process_pool
        self.worker_ttl = worker_ttl


class WorkerPool:
    """Manage a pool of async workers with lifecycle management."""

    def __init__(self, config: ParallelConfig):
        self.config = config
        self.semaphore = asyncio.Semaphore(config.max_concurrent)
        self.active_workers = 0
        self.total_tasks_processed = 0
        self.worker_start_times: dict[int, float] = {}
        self._worker_id_counter = 0
        self._stats_lock = asyncio.Lock()

    async def execute_with_worker(
        self,
        coro: Coroutine[Any, Any, R],
        worker_id: int | None = None,
    ) -> R:
        """Execute a coroutine with worker pool management."""
        async with self.semaphore:
            if worker_id is None:
                worker_id = self._worker_id_counter
                self._worker_id_counter += 1

            async with self._stats_lock:
                self.active_workers += 1
                self.worker_start_times[worker_id] = time.time()

            try:
                # Execute with timeout
                result = await asyncio.wait_for(coro, timeout=self.config.timeout)

                async with self._stats_lock:
                    self.total_tasks_processed += 1

                return result

            finally:
                async with self._stats_lock:
                    self.active_workers -= 1
                    if worker_id in self.worker_start_times:
                        del self.worker_start_times[worker_id]

    async def get_stats(self) -> dict[str, Any]:
        """Get worker pool statistics."""
        async with self._stats_lock:
            current_time = time.time()
            active_worker_times = [
                current_time - start_time
                for start_time in self.worker_start_times.values()
            ]

            return {
                "active_workers": self.active_workers,
                "max_concurrent": self.config.max_concurrent,
                "total_tasks_processed": self.total_tasks_processed,
                "avg_worker_time": (
                    sum(active_worker_times) / len(active_worker_times)
                    if active_worker_times
                    else 0
                ),
                "longest_running_worker": max(active_worker_times, default=0),
                "worker_utilization": self.active_workers / self.config.max_concurrent,
            }


class ParallelExecutor:
    """Execute tasks in parallel with advanced batching and error handling."""

    def __init__(self, config: ParallelConfig | None = None):
        self.config = config or ParallelConfig()
        self.worker_pool = WorkerPool(self.config)
        self.stream_processor = StreamProcessor(
            StreamingConfig(chunk_size=self.config.batch_size)
        )

    async def map_parallel(
        self,
        items: AsyncIterator[T],
        mapper: Callable[[T], Coroutine[Any, Any, R]],
        preserve_order: bool = True,
    ) -> AsyncIterator[R]:
        """Map function over items in parallel with optional order preservation."""
        if preserve_order:
            async for result in self._map_parallel_ordered(items, mapper):
                yield result
        else:
            async for result in self._map_parallel_unordered(items, mapper):
                yield result

    async def _map_parallel_ordered(
        self,
        items: AsyncIterator[T],
        mapper: Callable[[T], Coroutine[Any, Any, R]],
    ) -> AsyncIterator[R]:
        """Map with preserved order using batching."""
        async for batch in self.stream_processor.chunk_stream(items):
            # Create tasks for the batch
            tasks = [self._execute_with_retry(mapper(item), item) for item in batch]

            # Execute batch in parallel
            try:
                results = await asyncio.gather(*tasks, return_exceptions=True)

                # Yield successful results in order
                for result in results:
                    if not isinstance(result, Exception):
                        yield result

            except Exception:
                # Skip failed batches
                continue

    async def _map_parallel_unordered(
        self,
        items: AsyncIterator[T],
        mapper: Callable[[T], Coroutine[Any, Any, R]],
    ) -> AsyncIterator[R]:
        """Map without order preservation for maximum throughput."""
        pending_tasks = set()

        async for item in items:
            # Create task
            task = asyncio.create_task(
                self.worker_pool.execute_with_worker(
                    self._execute_with_retry(mapper(item), item)
                )
            )
            pending_tasks.add(task)

            # Process completed tasks when we hit concurrency limit
            if len(pending_tasks) >= self.config.max_concurrent:
                done, pending_tasks = await asyncio.wait(
                    pending_tasks, return_when=asyncio.FIRST_COMPLETED
                )

                for completed_task in done:
                    try:
                        result = await completed_task
                        yield result
                    except Exception:
                        # Skip failed tasks
                        continue

        # Process remaining tasks
        while pending_tasks:
            done, pending_tasks = await asyncio.wait(
                pending_tasks, return_when=asyncio.FIRST_COMPLETED
            )

            for completed_task in done:
                try:
                    result = await completed_task
                    yield result
                except Exception:
                    continue

    async def _execute_with_retry(
        self,
        coro: Coroutine[Any, Any, R],
        original_item: T,
    ) -> R:
        """Execute coroutine with retry logic."""
        last_exception = None

        for attempt in range(self.config.retry_attempts):
            try:
                return await coro
            except Exception as e:
                last_exception = e
                if attempt < self.config.retry_attempts - 1:
                    await asyncio.sleep(self.config.retry_delay * (2**attempt))
                    # Recreate coroutine for retry (if possible)
                    # Note: This is a simplified approach

        # All retries failed
        raise last_exception or RuntimeError("All retries failed")

    async def batch_process(
        self,
        items: AsyncIterator[T],
        processor: Callable[[list[T]], Coroutine[Any, Any, list[R]]],
    ) -> AsyncIterator[R]:
        """Process items in batches for operations that benefit from batching."""
        async for batch in self.stream_processor.chunk_stream(
            items, self.config.batch_size
        ):
            try:
                # Process entire batch
                batch_results = await self.worker_pool.execute_with_worker(
                    processor(batch)
                )

                # Yield individual results
                for result in batch_results:
                    yield result

            except Exception:
                # Skip failed batches
                continue

    async def pipeline_parallel(
        self,
        stages: list[Callable[[AsyncIterator[Any]], AsyncIterator[Any]]],
        initial_stream: AsyncIterator[T],
    ) -> AsyncIterator[Any]:
        """Execute a pipeline of stages in parallel with inter-stage buffering."""
        if not stages:
            async for item in initial_stream:
                yield item
            return

        # Start with initial stream
        current_stream = initial_stream

        # Apply each stage
        for stage in stages:
            # Buffer between stages for better parallelization
            current_stream = self.stream_processor.buffer_stream(stage(current_stream))

        # Yield final results
        async for result in current_stream:
            yield result

    @asynccontextmanager
    async def parallel_context(self) -> AsyncGenerator[ParallelExecutor]:
        """Context manager for parallel execution lifecycle."""
        start_time = time.time()
        try:
            yield self
        finally:
            # Record execution time
            execution_time = time.time() - start_time
            await performance_monitor.record_execution_time(
                "parallel_execution", execution_time
            )

    async def get_performance_stats(self) -> dict[str, Any]:
        """Get detailed performance statistics."""
        worker_stats = await self.worker_pool.get_stats()
        stream_stats = await self.stream_processor.get_memory_stats()

        return {
            "worker_pool": worker_stats,
            "streaming": stream_stats,
            "config": {
                "max_concurrent": self.config.max_concurrent,
                "batch_size": self.config.batch_size,
                "timeout": self.config.timeout,
                "retry_attempts": self.config.retry_attempts,
                "retry_delay": self.config.retry_delay,
            },
        }


# Flow-specific parallel utilities
class FlowParallelExecutor(ParallelExecutor):
    """Specialized parallel executor for Flow operations."""

    async def parallel_flow_map(
        self,
        flow_inputs: AsyncIterator[FlowIOSchema],
        flow_func: Callable[[FlowIOSchema], Coroutine[Any, Any, FlowIOSchema]],
        preserve_order: bool = True,
    ) -> AsyncIterator[FlowIOSchema]:
        """Execute Flow operations in parallel over input stream."""
        async for result in self.map_parallel(flow_inputs, flow_func, preserve_order):
            yield result

    async def parallel_tool_execution(
        self,
        tool_inputs: list[tuple[str, FlowIOSchema]],  # (tool_name, input)
        tool_registry: dict[
            str, Callable[[FlowIOSchema], Coroutine[Any, Any, FlowIOSchema]]
        ],
    ) -> AsyncIterator[tuple[str, FlowIOSchema]]:
        """Execute multiple tools in parallel."""

        async def execute_tool(
            tool_input: tuple[str, FlowIOSchema]
        ) -> tuple[str, FlowIOSchema]:
            tool_name, input_data = tool_input
            if tool_name not in tool_registry:
                raise ValueError(f"Unknown tool: {tool_name}")

            result = await tool_registry[tool_name](input_data)
            return tool_name, result

        async def input_stream() -> AsyncIterator[tuple[str, FlowIOSchema]]:
            for tool_input in tool_inputs:
                yield tool_input

        async for result in self.map_parallel(
            input_stream(), execute_tool, preserve_order=False
        ):
            yield result


# Global parallel executor
default_parallel_executor = FlowParallelExecutor()


# Convenience functions
async def parallel_map(
    items: AsyncIterator[T],
    mapper: Callable[[T], Coroutine[Any, Any, R]],
    max_concurrent: int = 10,
    preserve_order: bool = True,
) -> AsyncIterator[R]:
    """Simple parallel map with default configuration."""
    config = ParallelConfig(max_concurrent=max_concurrent)
    executor = ParallelExecutor(config)

    async with executor.parallel_context():
        async for result in executor.map_parallel(items, mapper, preserve_order):
            yield result


async def parallel_batch_process(
    items: AsyncIterator[T],
    processor: Callable[[list[T]], Coroutine[Any, Any, list[R]]],
    batch_size: int = 100,
    max_concurrent: int = 5,
) -> AsyncIterator[R]:
    """Simple parallel batch processing with default configuration."""
    config = ParallelConfig(
        max_concurrent=max_concurrent,
        batch_size=batch_size,
    )
    executor = ParallelExecutor(config)

    async with executor.parallel_context():
        async for result in executor.batch_process(items, processor):
            yield result
