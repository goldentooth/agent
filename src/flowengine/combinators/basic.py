"""Basic flow combinators for core operations.

This module provides fundamental operations like map, filter, compose, and other
essential stream processing combinators.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import AsyncGenerator, TypeVar

from flowengine.combinators.utils import get_function_name
from flowengine.flow import Flow

Input = TypeVar("Input")
Output = TypeVar("Output")
Newput = TypeVar("Newput")

A = TypeVar("A")
B = TypeVar("B")
C = TypeVar("C")


async def run_fold(
    initial_stream: AsyncGenerator[Input, None], steps: list[Flow[Input, Input]]
) -> AsyncGenerator[Input, None]:
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

    async def _flow(stream: AsyncGenerator[A, None]) -> AsyncGenerator[C, None]:
        """Pipe the stream through first flow, then through second flow."""
        intermediate_stream = first(stream)
        async for item in second(intermediate_stream):
            yield item

    return Flow(_flow, name=f"{first.name} ∘ {second.name}")


def filter_stream(predicate: Callable[[Input], bool]) -> Flow[Input, Input]:
    """Create a flow that filters stream items based on a predicate.

    Args:
        predicate: Function that returns True for items to keep

    Returns:
        A flow that yields only items where predicate returns True

    Example:
        is_even = lambda x: x % 2 == 0
        even_filter = filter_stream(is_even)
        # Use: even_numbers = even_filter(number_stream)
    """

    async def _flow(stream: AsyncGenerator[Input, None]) -> AsyncGenerator[Input, None]:
        """Filter stream items based on predicate."""
        async for item in stream:
            if predicate(item):
                yield item

    return Flow(_flow, name=f"filter({get_function_name(predicate)})")
