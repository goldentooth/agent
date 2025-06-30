"""Basic flow combinators for core operations.

This module provides fundamental operations like map, filter, compose, and other
essential stream processing combinators.
"""

from __future__ import annotations

from collections.abc import AsyncIterator, Callable
from typing import TypeVar

from ..core.exceptions import FlowValidationError
from ..core.flow import Flow
from .utils import get_function_name

Input = TypeVar("Input")
Output = TypeVar("Output")
Newput = TypeVar("Newput")

A = TypeVar("A")
B = TypeVar("B")
C = TypeVar("C")


async def run_fold(
    initial_stream: AsyncIterator[Input], steps: list[Flow[Input, Input]]
) -> AsyncIterator[Input]:
    """Execute a list of flows sequentially, piping the stream through each step.

    This is a fold/reduce operation where each flow receives the output stream of the
    previous flow as its input. Useful for building sequential processing pipelines.

    Args:
        initial_stream: The initial input stream
        steps: List of flows to execute in order

    Returns:
        The final output stream after all steps have been executed

    Example:
        increment_flow = Flow.from_sync_fn(lambda x: x + 1)
        double_flow = Flow.from_sync_fn(lambda x: x * 2)
        input_stream = async_range(3)  # [0, 1, 2]
        result_stream = run_fold(input_stream, [increment_flow, double_flow])
        # Result: [2, 4, 6] -> (0+1)*2, (1+1)*2, (2+1)*2
    """
    current_stream = initial_stream
    for step in steps:
        current_stream = step(current_stream)
    return current_stream


def compose(first: Flow[A, B], second: Flow[B, C]) -> Flow[A, C]:
    """Compose two flows, where the output of the first is the input to the second."""

    async def _flow(stream: AsyncIterator[A]) -> AsyncIterator[C]:
        """Pipe the stream through first flow, then through second flow."""
        intermediate_stream = first(stream)
        async for item in second(intermediate_stream):
            yield item

    return Flow(_flow, name=f"{first.name} ∘ {second.name}")


def filter_stream(predicate: Callable[[Input], bool]) -> Flow[Input, Input]:
    """Create a flow that filters stream items based on a predicate."""

    async def _flow(stream: AsyncIterator[Input]) -> AsyncIterator[Input]:
        """Filter stream items based on predicate."""
        async for item in stream:
            if predicate(item):
                yield item

    return Flow(_flow, name=f"filter({get_function_name(predicate)})")


def map_stream(fn: Callable[[Input], Output]) -> Flow[Input, Output]:
    """Create a flow that maps a function over each item in the stream."""

    async def _flow(stream: AsyncIterator[Input]) -> AsyncIterator[Output]:
        """Map function over each item in the stream."""
        async for item in stream:
            yield fn(item)

    return Flow(_flow, name=f"map({get_function_name(fn)})")


def flat_map_stream(
    fn: Callable[[Input], AsyncIterator[Output]],
) -> Flow[Input, Output]:
    """Create a flow that flat-maps a function over each item in the stream."""

    async def _flow(stream: AsyncIterator[Input]) -> AsyncIterator[Output]:
        """Flat-map function over each item in the stream."""
        async for item in stream:
            async for sub_item in fn(item):
                yield sub_item

    return Flow(_flow, name=f"flat_map({fn.__name__})")


def identity_stream() -> Flow[Input, Input]:
    """Create a flow that passes the stream through unchanged."""

    async def _flow(stream: AsyncIterator[Input]) -> AsyncIterator[Input]:
        """Pass stream through unchanged."""
        async for item in stream:
            yield item

    return Flow(_flow, name="identity")


def take_stream(n: int) -> Flow[Input, Input]:
    """Create a flow that takes the first n items from the stream."""

    async def _flow(stream: AsyncIterator[Input]) -> AsyncIterator[Input]:
        """Take the first n items from the stream."""
        count = 0
        async for item in stream:
            if count >= n:
                break
            yield item
            count += 1

    return Flow(_flow, name=f"take({n})")


def skip_stream(n: int) -> Flow[Input, Input]:
    """Create a flow that skips the first n items from the stream."""

    async def _flow(stream: AsyncIterator[Input]) -> AsyncIterator[Input]:
        """Skip the first n items from the stream."""
        count = 0
        async for item in stream:
            if count < n:
                count += 1
                continue
            yield item

    return Flow(_flow, name=f"skip({n})")


def guard_stream(
    predicate: Callable[[Input], bool], message: str = "Guard condition failed"
) -> Flow[Input, Input]:
    """Create a flow that validates items or raises an exception.

    Args:
        predicate: Function that returns True for valid items
        message: Error message if validation fails

    Raises:
        FlowValidationError: If any item fails the guard condition
    """

    async def _flow(stream: AsyncIterator[Input]) -> AsyncIterator[Input]:
        """Validate each item or raise an exception."""
        async for item in stream:
            if not predicate(item):
                raise FlowValidationError(f"{message}: {item}")
            yield item

    return Flow(_flow, name=f"guard({get_function_name(predicate)})")


def flatten_stream() -> Flow[AsyncIterator[Input], Input]:
    """Create a flow that flattens nested async iterators."""

    async def _flow(
        stream: AsyncIterator[AsyncIterator[Input]],
    ) -> AsyncIterator[Input]:
        """Flatten nested async iterators."""
        async for sub_stream in stream:
            async for item in sub_stream:
                yield item

    return Flow(_flow, name="flatten")


def collect_stream() -> Flow[Input, list[Input]]:
    """Create a flow that collects all items into a single list."""

    async def _flow(stream: AsyncIterator[Input]) -> AsyncIterator[list[Input]]:
        """Collect all items into a single list."""
        items = []
        async for item in stream:
            items.append(item)
        yield items

    return Flow(_flow, name="collect")


def until_stream(predicate: Callable[[Input], bool]) -> Flow[Input, Input]:
    """Create a flow that processes items until a predicate becomes true.

    Once the predicate returns True for an item, that item is yielded
    and processing stops (the predicate item is included in output).

    Args:
        predicate: Function that determines when to stop processing

    Returns:
        A flow that processes until predicate is satisfied
    """

    async def _flow(stream: AsyncIterator[Input]) -> AsyncIterator[Input]:
        """Process items until predicate becomes true."""
        try:
            async for item in stream:
                yield item
                if predicate(item):
                    break  # Stop processing after yielding the matching item
        finally:
            # Ensure the stream is properly closed when we break early
            if hasattr(stream, "aclose"):
                await stream.aclose()

    return Flow(_flow, name=f"until({get_function_name(predicate)})")


def share_stream() -> Flow[Input, Input]:
    """Create a flow that shares a single stream subscription among multiple subscribers."""

    async def _flow(stream: AsyncIterator[Input]) -> AsyncIterator[Input]:
        """Share single stream subscription."""
        # Note: This is a simplified implementation
        # A full implementation would need proper subscription management
        async for item in stream:
            yield item

    return Flow(_flow, name="share")
