"""Temporal combinators for time-based stream operations.

This module provides combinators that deal with timing, delays, throttling,
and time-based sampling of stream flows.
"""

from __future__ import annotations

import asyncio
from collections.abc import AsyncGenerator
from typing import Any, TypeVar

from flowengine.exceptions import FlowTimeoutError
from flowengine.flow import Flow

Input = TypeVar("Input")


def delay_stream(seconds: float) -> Flow[Input, Input]:
    """Create a flow that delays each item in the stream by a given number of seconds."""

    async def _flow(stream: AsyncGenerator[Input, None]) -> AsyncGenerator[Input, None]:
        """Delay each item by the specified number of seconds."""
        async for item in stream:
            await asyncio.sleep(seconds)
            yield item

    return Flow(_flow, name=f"delay({seconds})")


def debounce_stream(seconds: float) -> Flow[Input, Input]:
    """Create a flow that debounces stream items by waiting for a quiet period.

    True debouncing: emits the latest item only after the stream has been quiet
    for the specified duration. Handles infinite streams correctly.
    """

    async def _flow(stream: AsyncGenerator[Input, None]) -> AsyncGenerator[Input, None]:
        """Debounce stream items by waiting for quiet periods."""
        latest_item = None
        last_update_time = 0.0

        async def item_collector():
            """Collect items and track timing."""
            nonlocal latest_item, last_update_time
            async for item in stream:
                latest_item = item
                last_update_time = asyncio.get_event_loop().time()

        collector = asyncio.create_task(item_collector())

        try:
            while not collector.done():
                await asyncio.sleep(0.01)  # Check every 10ms

                if latest_item is not None:
                    current_time = asyncio.get_event_loop().time()
                    if current_time - last_update_time >= seconds:
                        yield latest_item
                        latest_item = None
        finally:
            if not collector.done():
                collector.cancel()
            # Emit final item
            if latest_item is not None:
                yield latest_item

    return Flow(_flow, name=f"debounce({seconds})")


def throttle_stream(rate_per_second: float) -> Flow[Input, Input]:
    """Create a flow that throttles the rate of item processing.

    Ensures that items are processed at most at the specified rate,
    introducing delays as necessary. The throttling state persists across
    all uses of this flow instance.

    Args:
        rate_per_second: Maximum items per second to process

    Returns:
        A flow that throttles processing rate
    """
    min_interval = 1.0 / rate_per_second
    # Persistent throttling state shared across all stream iterations
    last_yield_time = 0.0

    async def _flow(stream: AsyncGenerator[Input, None]) -> AsyncGenerator[Input, None]:
        """Throttle stream processing to specified rate."""
        nonlocal last_yield_time

        async for item in stream:
            current_time = asyncio.get_event_loop().time()
            time_since_last = current_time - last_yield_time

            if time_since_last < min_interval:
                await asyncio.sleep(min_interval - time_since_last)

            last_yield_time = asyncio.get_event_loop().time()
            yield item

    return Flow(_flow, name=f"throttle({rate_per_second}/s)")


def timeout_stream(seconds: float) -> Flow[Input, Input]:
    """Create a flow that adds a timeout to stream processing.

    If waiting for the next item takes longer than the specified timeout,
    the stream is terminated with a TimeoutError.

    Args:
        seconds: Maximum time to wait for each item

    Returns:
        A flow that enforces timeouts on stream processing
    """

    async def _flow(stream: AsyncGenerator[Input, None]) -> AsyncGenerator[Input, None]:
        """Process stream with timeout enforcement."""
        stream_iter = aiter(stream)

        while True:
            try:
                # Wait for next item with timeout
                item = await asyncio.wait_for(anext(stream_iter), timeout=seconds)
                yield item
            except StopAsyncIteration:
                break
            except TimeoutError as e:
                raise FlowTimeoutError(
                    f"Stream processing timed out after {seconds} seconds"
                ) from e

    return Flow(_flow, name=f"timeout({seconds})")


async def _sample_collector(
    stream: AsyncGenerator[Any, None], state: dict[str, Any]
) -> None:
    """Collect items from stream and update state."""
    async for item in stream:
        state["latest_item"] = item
        state["has_new_item"] = True


async def _sample_emit_at_intervals(
    collector_task: asyncio.Task[None], interval: float, state: dict[str, Any]
) -> AsyncGenerator[Any, None]:
    """Emit sampled items at regular intervals."""
    while not collector_task.done():
        await asyncio.sleep(interval)
        if state["has_new_item"] and state["latest_item"] is not None:
            yield state["latest_item"]
            state["has_new_item"] = False


async def _sample_cleanup_task(collector_task: asyncio.Task[None]) -> None:
    """Clean up the collector task."""
    if not collector_task.done():
        collector_task.cancel()
        try:
            await collector_task
        except asyncio.CancelledError:
            pass


def sample_stream(interval: float) -> Flow[Input, Input]:
    """Create a flow that samples the stream at regular intervals.

    Emits the most recent item at each interval. If no new items have arrived
    since the last sample, nothing is emitted. Essential for rate limiting
    and real-time applications.

    Args:
        interval: Sampling interval in seconds

    Returns:
        A flow that samples items at regular intervals
    """

    async def _flow(stream: AsyncGenerator[Input, None]) -> AsyncGenerator[Input, None]:
        """Sample stream at regular intervals."""
        state: dict[str, Any] = {"latest_item": None, "has_new_item": False}
        collector_task = asyncio.create_task(_sample_collector(stream, state))

        try:
            async for item in _sample_emit_at_intervals(
                collector_task, interval, state
            ):
                yield item
        finally:
            await _sample_cleanup_task(collector_task)

    return Flow(_flow, name=f"sample({interval})")
