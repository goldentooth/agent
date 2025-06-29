"""Temporal combinators for time-based stream operations.

This module provides combinators that deal with timing, delays, throttling,
and time-based sampling of stream flows.
"""

from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator
from typing import TypeVar

from ..exceptions import FlowTimeoutError
from ..main import Flow

Input = TypeVar("Input")


def delay_stream(seconds: float) -> Flow[Input, Input]:
    """Create a flow that delays each item in the stream by a given number of seconds."""

    async def _flow(stream: AsyncIterator[Input]) -> AsyncIterator[Input]:
        """Delay each item by the specified number of seconds."""
        async for item in stream:
            await asyncio.sleep(seconds)
            yield item

    return Flow(_flow, name=f"delay({seconds})")


def debounce_stream(seconds: float) -> Flow[Input, Input]:
    """Create a flow that debounces stream items by waiting for a quiet period."""

    async def _flow(stream: AsyncIterator[Input]) -> AsyncIterator[Input]:
        """Debounce stream items by waiting for quiet periods."""
        last_item = None
        last_time = 0.0

        async for item in stream:
            current_time = asyncio.get_event_loop().time()
            last_item = item
            last_time = current_time

            # Wait for the debounce period
            await asyncio.sleep(seconds)

            # Only yield if this is still the latest item
            if asyncio.get_event_loop().time() - last_time >= seconds:
                yield last_item

    return Flow(_flow, name=f"debounce({seconds})")


def throttle_stream(rate_per_second: float) -> Flow[Input, Input]:
    """Create a flow that throttles the rate of item processing.

    Ensures that items are processed at most at the specified rate,
    introducing delays as necessary.

    Args:
        rate_per_second: Maximum items per second to process

    Returns:
        A flow that throttles processing rate
    """
    last_yield_time = 0.0
    min_interval = 1.0 / rate_per_second

    async def _flow(stream: AsyncIterator[Input]) -> AsyncIterator[Input]:
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
    """Create a flow that adds a timeout to each item's processing.

    If processing an item takes longer than the specified timeout,
    a TimeoutError is raised.

    Args:
        seconds: Maximum time to wait for each item

    Returns:
        A flow that enforces timeouts on item processing
    """

    async def _flow(stream: AsyncIterator[Input]) -> AsyncIterator[Input]:
        """Process each item with timeout enforcement."""
        async for item in stream:
            try:
                # Use asyncio.wait_for to enforce timeout
                yield await asyncio.wait_for(_identity_async(item), timeout=seconds)
            except TimeoutError as e:
                raise FlowTimeoutError(
                    f"Processing timed out after {seconds} seconds for item: {item}"
                ) from e

    async def _identity_async(item: Input) -> Input:
        """Identity function that can be awaited."""
        return item

    return Flow(_flow, name=f"timeout({seconds})")


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

    async def _flow(stream: AsyncIterator[Input]) -> AsyncIterator[Input]:
        """Sample stream at regular intervals."""
        latest_item = None
        has_new_item = False

        async def item_collector() -> None:
            """Collect items from the stream."""
            nonlocal latest_item, has_new_item
            async for item in stream:
                latest_item = item
                has_new_item = True

        # Start the collector task
        collector_task = asyncio.create_task(item_collector())

        try:
            while not collector_task.done():
                # Wait for the interval
                await asyncio.sleep(interval)

                # Emit the latest item if we have a new one
                if has_new_item and latest_item is not None:
                    yield latest_item
                    has_new_item = False
        finally:
            # Clean up the collector task
            if not collector_task.done():
                collector_task.cancel()
                try:
                    await collector_task
                except asyncio.CancelledError:
                    pass

    return Flow(_flow, name=f"sample({interval})")
