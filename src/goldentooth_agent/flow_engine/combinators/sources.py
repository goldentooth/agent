"""Source flow combinators for creating flows from data sources.

This module provides combinators that create flows from various data sources
like ranges, repeated values, empty flows, and initial values.
"""

from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Any, TypeVar

from ..core.flow import Flow

Input = TypeVar("Input")
A = TypeVar("A")

# Type alias
AnyValue = Any


def range_flow(start: int, stop: int, step: int = 1) -> Flow[None, int]:
    """Create a flow that generates a range of integers."""

    async def _flow(_: AsyncIterator[None]) -> AsyncIterator[int]:
        """Generate range of integers."""
        for i in range(start, stop, step):
            yield i

    return Flow(_flow, name=f"range({start}, {stop}, {step})")


def repeat_flow(value: A, times: int | None = None) -> Flow[None, A]:
    """Create a flow that repeats a value a specified number of times (or infinitely)."""

    async def _flow(stream: AsyncIterator[None]) -> AsyncIterator[A]:
        """Repeat value specified number of times."""
        if times is None:
            while True:
                yield value
        else:
            # Type checker knows times is int here due to the else branch
            for _ in range(times):
                yield value

    times_str = str(times) if times is not None else "∞"
    return Flow(_flow, name=f"repeat({value}, {times_str})")


def empty_flow() -> Flow[None, AnyValue]:
    """Create a flow that produces no items."""

    async def _flow(_: AsyncIterator[None]) -> AsyncIterator[AnyValue]:
        """Produce no items."""
        # This is a generator that produces no items
        if False:  # This ensures it's a generator without unreachable code
            yield  # type: ignore[unreachable]
        return

    return Flow(_flow, name="empty")


def start_with_stream(*items: Input) -> Flow[Input, Input]:
    """Create a flow that prepends specified items to the beginning of the stream.

    Very useful for providing default values, initialization, or ensuring
    non-empty streams.

    Args:
        *items: Items to prepend to the stream

    Returns:
        A flow that starts with the specified items, then continues with stream items
    """

    async def _flow(stream: AsyncIterator[Input]) -> AsyncIterator[Input]:
        """Prepend items to the stream."""
        # First emit the start items
        for item in items:
            yield item

        # Then emit all items from the stream
        async for item in stream:
            yield item

    return Flow(_flow, name=f"start_with({len(items)} items)")
