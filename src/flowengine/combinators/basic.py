"""Basic flow combinators for core operations.

This module provides fundamental operations like map, filter, compose, and other
essential stream processing combinators.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import AsyncGenerator, TypeVar

from flowengine.combinators.utils import get_function_name
from flowengine.exceptions import FlowValidationError
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


def map_stream(fn: Callable[[Input], Output]) -> Flow[Input, Output]:
    """Create a flow that maps a function over each item in the stream.

    Args:
        fn: Function to apply to each item in the stream

    Returns:
        A flow that yields the result of applying fn to each stream item

    Example:
        double = lambda x: x * 2
        doubler = map_stream(double)
        # Use: doubled_numbers = doubler(number_stream)
    """

    async def _flow(
        stream: AsyncGenerator[Input, None]
    ) -> AsyncGenerator[Output, None]:
        """Map function over each item in the stream."""
        async for item in stream:
            yield fn(item)

    return Flow(_flow, name=f"map({get_function_name(fn)})")


def flat_map_stream(
    fn: Callable[[Input], AsyncGenerator[Output, None]],
) -> Flow[Input, Output]:
    """Create a flow that flat-maps a function over each item in the stream.

    Args:
        fn: Function that takes an item and returns an AsyncGenerator of outputs

    Returns:
        A flow that yields all items from all the AsyncGenerators returned by fn

    Example:
        split_chars = lambda s: (c for c in s)
        char_splitter = flat_map_stream(split_chars)
        # Use: all_chars = char_splitter(word_stream)
    """

    async def _flow(
        stream: AsyncGenerator[Input, None]
    ) -> AsyncGenerator[Output, None]:
        """Flat-map function over each item in the stream."""
        async for item in stream:
            async for sub_item in fn(item):
                yield sub_item

    return Flow(_flow, name=f"flat_map({get_function_name(fn)})")


def identity_stream() -> Flow[Input, Input]:
    """Create a flow that passes the stream through unchanged.

    Returns:
        A flow that yields each input item unchanged

    Example:
        passthrough = identity_stream()
        # Use: same_values = passthrough(any_stream)
    """

    async def _flow(stream: AsyncGenerator[Input, None]) -> AsyncGenerator[Input, None]:
        """Pass stream through unchanged."""
        async for item in stream:
            yield item

    return Flow(_flow, name="identity")


def take_stream(n: int) -> Flow[Input, Input]:
    """Create a flow that takes the first n items from the stream.

    Args:
        n: Number of items to take from the stream

    Returns:
        A flow that yields only the first n items from the input stream

    Example:
        first_three = take_stream(3)
        # Use: limited_stream = first_three(number_stream)
    """

    async def _flow(stream: AsyncGenerator[Input, None]) -> AsyncGenerator[Input, None]:
        """Take the first n items from the stream."""
        count = 0
        async for item in stream:
            if count >= n:
                break
            yield item
            count += 1

    return Flow(_flow, name=f"take({n})")


def skip_stream(n: int) -> Flow[Input, Input]:
    """Create a flow that skips the first n items from the stream.

    Args:
        n: Number of items to skip from the stream

    Returns:
        A flow that yields items after skipping the first n items

    Example:
        skip_first_two = skip_stream(2)
        # Use: remaining_stream = skip_first_two(number_stream)
    """

    async def _flow(stream: AsyncGenerator[Input, None]) -> AsyncGenerator[Input, None]:
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

    Returns:
        A flow that yields items if they pass validation

    Raises:
        FlowValidationError: If any item fails the guard condition

    Example:
        is_positive = lambda x: x > 0
        positive_guard = guard_stream(is_positive, "Must be positive")
        # Use: validated_stream = positive_guard(number_stream)
    """

    async def _flow(stream: AsyncGenerator[Input, None]) -> AsyncGenerator[Input, None]:
        """Validate each item or raise an exception."""
        async for item in stream:
            if not predicate(item):
                raise FlowValidationError(f"{message}: {item}")
            yield item

    return Flow(_flow, name=f"guard({get_function_name(predicate)})")


def flatten_stream() -> Flow[AsyncGenerator[Input, None], Input]:
    """Create a flow that flattens nested async generators.

    Returns:
        A flow that takes a stream of AsyncGenerators and yields all their items

    Example:
        flattener = flatten_stream()
        # Use: flat_stream = flattener(nested_stream)
    """

    async def _flow(
        stream: AsyncGenerator[AsyncGenerator[Input, None], None],
    ) -> AsyncGenerator[Input, None]:
        """Flatten nested async generators."""
        async for sub_stream in stream:
            async for item in sub_stream:
                yield item

    return Flow(_flow, name="flatten")


def collect_stream() -> Flow[Input, list[Input]]:
    """Create a flow that collects all items into a single list.

    Returns:
        A flow that yields a single list containing all input items

    Example:
        collector = collect_stream()
        # Use: list_stream = collector(item_stream)
    """

    async def _flow(
        stream: AsyncGenerator[Input, None]
    ) -> AsyncGenerator[list[Input], None]:
        """Collect all items into a single list."""
        items: list[Input] = []
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

    Example:
        is_zero = lambda x: x == 0
        until_zero = until_stream(is_zero)
        # Use: limited_stream = until_zero(number_stream)
    """

    async def _flow(stream: AsyncGenerator[Input, None]) -> AsyncGenerator[Input, None]:
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
    """Create a flow that shares a single stream subscription among multiple subscribers.

    Returns:
        A flow that allows sharing of stream subscription

    Example:
        shared = share_stream()
        # Use: shared_stream = shared(input_stream)

    Note:
        This is a simplified implementation. A full implementation would need
        proper subscription management for multiple concurrent subscribers.
    """

    async def _flow(stream: AsyncGenerator[Input, None]) -> AsyncGenerator[Input, None]:
        """Share single stream subscription."""
        # Note: This is a simplified implementation
        # A full implementation would need proper subscription management
        async for item in stream:
            yield item

    return Flow(_flow, name="share")
