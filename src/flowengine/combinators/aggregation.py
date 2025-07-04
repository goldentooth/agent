"""Aggregation combinators for collecting and grouping stream operations.

This module provides combinators for batching, chunking, scanning, grouping,
and other aggregation patterns for stream processing.
"""

from __future__ import annotations

import asyncio
from collections import deque
from collections.abc import AsyncGenerator, Callable, Hashable
from typing import Any, TypeVar

from flowengine.combinators.utils import get_function_name
from flowengine.flow import Flow

Input = TypeVar("Input")
Output = TypeVar("Output")
K = TypeVar("K", bound=Hashable)


def batch_stream(size: int) -> Flow[Input, list[Input]]:
    """Create a flow that batches stream items into lists of specified size.

    Args:
        size: Number of items per batch

    Returns:
        Flow that batches items into lists of the specified size
    """

    async def _flow(
        stream: AsyncGenerator[Input, None],
    ) -> AsyncGenerator[list[Input], None]:
        """Batch stream items into lists."""
        batch: list[Input] = []
        async for item in stream:
            batch.append(item)
            if len(batch) >= size:
                yield batch
                batch = []

        # Yield remaining items if any
        if batch:
            yield batch

    return Flow(_flow, name=f"batch({size})")


def chunk_stream(size: int) -> Flow[Input, list[Input]]:
    """Create a flow that groups items into fixed-size chunks.

    Similar to batch_stream but emphasizes the chunking concept.

    Args:
        size: Number of items per chunk

    Returns:
        A flow that yields lists of items
    """

    async def _flow(
        stream: AsyncGenerator[Input, None],
    ) -> AsyncGenerator[list[Input], None]:
        """Group items into fixed-size chunks."""
        chunk: list[Input] = []
        async for item in stream:
            chunk.append(item)
            if len(chunk) >= size:
                yield chunk
                chunk = []

        # Yield remaining items if any
        if chunk:
            yield chunk

    return Flow(_flow, name=f"chunk({size})")


def window_stream(size: int, step: int = 1) -> Flow[Input, list[Input]]:
    """Create a flow that generates sliding windows over the stream.

    Creates overlapping windows of items with specified size and step.

    Args:
        size: Window size
        step: Step size between windows (default 1)

    Returns:
        A flow that yields sliding windows
    """

    async def _flow(
        stream: AsyncGenerator[Input, None],
    ) -> AsyncGenerator[list[Input], None]:
        """Generate sliding windows over the stream."""
        window: deque[Input] = deque(maxlen=size)
        items_seen = 0

        async for item in stream:
            window.append(item)
            items_seen += 1

            # Emit window when we have enough items and at correct intervals
            if len(window) == size and (items_seen - size) % step == 0:
                yield list(window)

    return Flow(_flow, name=f"window({size}, step={step})")


def scan_stream(
    fn: Callable[[Output, Input], Output], initial: Output
) -> Flow[Input, Output]:
    """Create a flow that performs a running accumulation with intermediate results.

    Like a fold/reduce but emits all intermediate accumulator values.

    Args:
        fn: Accumulator function
        initial: Initial accumulator value

    Returns:
        A flow that yields intermediate accumulation results
    """

    async def _flow(
        stream: AsyncGenerator[Input, None],
    ) -> AsyncGenerator[Output, None]:
        """Perform running accumulation with intermediate results."""
        accumulator = initial
        yield accumulator  # Emit initial value

        async for item in stream:
            accumulator = fn(accumulator, item)
            yield accumulator

    return Flow(_flow, name=f"scan({get_function_name(fn)}, {initial})")


def group_by_stream(key_fn: Callable[[Input], K]) -> Flow[Input, tuple[K, list[Input]]]:
    """Create a flow that groups items by a key function.

    Collects all items with the same key and emits them as groups.

    Args:
        key_fn: Function that extracts grouping key from each item

    Returns:
        A flow that yields (key, items) tuples
    """

    async def _flow(
        stream: AsyncGenerator[Input, None],
    ) -> AsyncGenerator[tuple[K, list[Input]], None]:
        """Group items by key function."""
        groups: dict[K, list[Input]] = {}

        async for item in stream:
            key = key_fn(item)
            if key not in groups:
                groups[key] = []
            groups[key].append(item)

        # Emit all groups
        for key, items in groups.items():
            yield (key, items)

    return Flow(_flow, name=f"group_by({get_function_name(key_fn)})")


def distinct_stream(key_fn: Callable[[Input], K] | None = None) -> Flow[Input, Input]:
    """Create a flow that filters out duplicate items.

    Uses a key function to determine uniqueness, or the items themselves if no key function.

    Args:
        key_fn: Optional function to extract comparison key (defaults to item itself)

    Returns:
        A flow that yields only distinct items
    """

    async def _flow(stream: AsyncGenerator[Input, None]) -> AsyncGenerator[Input, None]:
        """Filter out duplicate items."""
        seen: set[K | Input] = set()

        async for item in stream:
            key = key_fn(item) if key_fn else item
            if key not in seen:
                seen.add(key)
                yield item

    key_name = f"({get_function_name(key_fn)})" if key_fn else ""
    return Flow(_flow, name=f"distinct{key_name}")


def pairwise_stream() -> Flow[Input, tuple[Input, Input]]:
    """Create a flow that emits consecutive pairs of items.

    Emits tuples of (previous_item, current_item) for each item after the first.

    Returns:
        A flow that yields consecutive pairs
    """

    async def _flow(
        stream: AsyncGenerator[Input, None],
    ) -> AsyncGenerator[tuple[Input, Input], None]:
        """Emit consecutive pairs of items."""
        previous: Input | None = None
        first = True

        async for item in stream:
            if not first and previous is not None:
                yield (previous, item)
            previous = item
            first = False

    return Flow(_flow, name="pairwise")


def memoize_stream(key_fn: Callable[[Input], K]) -> Flow[Input, Input]:
    """Create a flow that caches items based on a key function.

    Items with the same key are only processed once; subsequent items
    with the same key yield the cached result.

    Args:
        key_fn: Function that extracts caching key from each item

    Returns:
        A flow that caches items by key
    """

    async def _flow(stream: AsyncGenerator[Input, None]) -> AsyncGenerator[Input, None]:
        """Cache items based on key function."""
        cache: dict[K, Input] = {}

        async for item in stream:
            key = key_fn(item)
            if key in cache:
                yield cache[key]
            else:
                cache[key] = item
                yield item

    return Flow(_flow, name=f"memoize({get_function_name(key_fn)})")


async def _buffer_collect_items(
    stream: AsyncGenerator[Input, None], buffer: list[Input]
) -> None:
    """Collect items from stream into buffer."""
    async for item in stream:
        buffer.append(item)


async def _buffer_emit_on_trigger(
    trigger: AsyncGenerator[Any, None], buffer: list[Input]
) -> AsyncGenerator[list[Input], None]:
    """Emit buffer contents when trigger fires."""
    async for _ in trigger:
        if buffer:
            yield list(buffer)
            buffer.clear()


async def _buffer_cleanup_collection_task(collect_task: asyncio.Task[None]) -> None:
    """Cancel and await collection task cleanup."""
    if not collect_task.done():
        collect_task.cancel()
        try:
            await collect_task
        except asyncio.CancelledError:
            pass


def buffer_stream(
    trigger: AsyncGenerator[Any, None],
) -> Flow[Input, list[Input]]:
    """Create a flow that buffers items until a trigger emits.

    Collects items in a buffer and emits the buffer contents when
    the trigger stream produces a value.

    Args:
        trigger: Stream that triggers buffer emission

    Returns:
        A flow that buffers items until triggered
    """

    async def _flow(
        stream: AsyncGenerator[Input, None],
    ) -> AsyncGenerator[list[Input], None]:
        """Buffer items until trigger emits."""
        buffer: list[Input] = []
        collect_task = asyncio.create_task(_buffer_collect_items(stream, buffer))

        try:
            async for buffered_items in _buffer_emit_on_trigger(trigger, buffer):
                yield buffered_items

            await collect_task

            if buffer:
                yield buffer

        except Exception:
            await _buffer_cleanup_collection_task(collect_task)
            raise

    return Flow(_flow, name="buffer")


def expand_stream(
    expander: Callable[[Input], AsyncGenerator[Input, None]], max_depth: int = 10
) -> Flow[Input, Input]:
    """Create a flow that recursively expands items using an expander function.

    Applies the expander function to each item and recursively processes
    the results until no more expansions are possible or max depth is reached.

    Args:
        expander: Function that expands an item into multiple items
        max_depth: Maximum recursion depth

    Returns:
        A flow that recursively expands items
    """

    async def _flow(
        stream: AsyncGenerator[Input, None],
    ) -> AsyncGenerator[Input, None]:
        """Recursively expand items."""
        queue: deque[tuple[Input, int]] = deque()

        # Initialize queue with stream items
        async for item in stream:
            queue.append((item, 0))  # (item, depth)

        while queue:
            item, depth = queue.popleft()
            yield item

            if depth < max_depth:
                # Expand the item and add results to queue
                async for expanded in expander(item):
                    queue.append((expanded, depth + 1))

    return Flow(_flow, name=f"expand({get_function_name(expander)}, depth={max_depth})")


def finalize_stream(
    finalizer: Callable[[], Any],
) -> Flow[Input, Input]:
    """Create a flow that executes a finalizer function when the stream completes.

    The finalizer is called whether the stream completes normally or with an error.

    Args:
        finalizer: Function to call when stream processing finishes

    Returns:
        A flow that executes cleanup on completion
    """

    async def _flow(
        stream: AsyncGenerator[Input, None],
    ) -> AsyncGenerator[Input, None]:
        """Execute finalizer on stream completion."""

        try:
            async for item in stream:
                yield item
        finally:
            if asyncio.iscoroutinefunction(finalizer):
                await finalizer()
            else:
                finalizer()

    return Flow(_flow, name=f"finalize({get_function_name(finalizer)})")
