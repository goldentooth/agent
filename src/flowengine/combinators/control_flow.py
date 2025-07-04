"""Control flow combinators for conditional and error handling operations.

This module provides combinators for conditional processing, error handling,
retry logic, circuit breakers, and other control flow patterns.
"""

from __future__ import annotations

import asyncio
import inspect
from collections.abc import AsyncGenerator, Awaitable, Callable
from typing import Any, TypeVar

from ..exceptions import FlowExecutionError
from ..flow import Flow
from .utils import get_function_name

Input = TypeVar("Input")
Output = TypeVar("Output")
Newput = TypeVar("Newput")

# Type alias
AnyValue = Any


async def maybe_await(func: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
    """Call a function and conditionally await its result if it returns a coroutine."""
    if not callable(func):
        raise ValueError(f"Expected a callable, got {type(func).__name__}")
    result = func(*args, **kwargs)
    if inspect.iscoroutine(result):
        awaited_result = await result
        return awaited_result
    return result


def if_then_stream(
    predicate: Callable[[Input], bool],
    then_flow: Flow[Input, Output],
    else_flow: Flow[Input, Output] | None = None,
) -> Flow[Input, Output]:
    """Create a flow that conditionally applies different flows based on a predicate.

    For each item in the stream, evaluates the predicate and applies either
    the then_flow or else_flow accordingly.

    Args:
        predicate: Function that determines which flow to apply
        then_flow: Flow to apply when predicate returns True
        else_flow: Flow to apply when predicate returns False (optional)

    Returns:
        A flow that conditionally processes items
    """

    async def _flow(
        stream: AsyncGenerator[Input, None]
    ) -> AsyncGenerator[Output, None]:
        """Apply conditional processing to each item."""
        async for item in stream:
            if predicate(item):
                # Apply then_flow to a single-item stream
                single_item_stream = _create_single_item_stream(item)
                async for result in then_flow(single_item_stream):
                    yield result
            elif else_flow is not None:
                # Apply else_flow to a single-item stream
                single_item_stream = _create_single_item_stream(item)
                async for result in else_flow(single_item_stream):
                    yield result
            # If no else_flow and predicate is False, item is filtered out

    async def _create_single_item_stream(item: Input) -> AsyncGenerator[Input, None]:
        """Create a single-item stream."""
        yield item

    predicate_name = get_function_name(predicate)
    if else_flow:
        return Flow(
            _flow, name=f"if_then({predicate_name}, {then_flow.name}, {else_flow.name})"
        )
    else:
        return Flow(_flow, name=f"if_then({predicate_name}, {then_flow.name})")


def retry_stream(n: int, flow: Flow[Input, Output]) -> Flow[Input, Output]:
    """Create a flow that retries processing items with another flow on failure."""

    async def _flow(
        stream: AsyncGenerator[Input, None]
    ) -> AsyncGenerator[Output, None]:
        """Retry processing items with the given flow on failure."""
        async for item in stream:
            last_exception = None

            for attempt in range(n + 1):  # n retries + initial attempt
                try:
                    # Apply flow to a single-item stream
                    single_item_stream = _create_single_item_stream(item)
                    async for result in flow(single_item_stream):
                        yield result
                    break  # Success, move to next item
                except Exception as e:
                    last_exception = e
                    if attempt < n:  # Still have retries left
                        await asyncio.sleep(0.1 * (attempt + 1))  # Backoff
                        continue
                    else:  # All retries exhausted
                        raise FlowExecutionError(
                            f"Failed after {n} retries: {last_exception}"
                        ) from last_exception

    async def _create_single_item_stream(item: Input) -> AsyncGenerator[Input, None]:
        """Create a single-item stream."""
        yield item

    return Flow(_flow, name=f"retry({n}, {flow.name})")


def recover_stream(
    handler: Callable[[Exception, Input], Awaitable[Input]],
) -> Flow[Input, Input]:
    """Create a flow that handles exceptions and provides fallback values.

    When an exception occurs during stream processing, the handler function
    is called with the exception and the current item to provide a fallback value.
    """

    async def _flow(stream: AsyncGenerator[Input, None]) -> AsyncGenerator[Input, None]:
        """Process stream with exception handling."""
        try:
            async for item in stream:
                yield item
        except Exception as e:
            # If we can determine what item caused the issue, call handler
            # For now, we'll pass None as the item since we can't determine it
            fallback = await handler(e, None)  # type: ignore[arg-type]
            yield fallback

    return Flow(_flow, name=f"recover({get_function_name(handler)})")
