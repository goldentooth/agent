"""Source flow combinators for creating flows from data sources."""

from __future__ import annotations

from collections.abc import AsyncIterator
from typing import TypeVar

from flowengine.flow import Flow

A = TypeVar("A")


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
