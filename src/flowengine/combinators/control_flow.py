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


def switch_stream(
    selector: Callable[[Input], str],
    cases: dict[str, Flow[Input, Output]],
    default: Flow[Input, Output] | None = None,
) -> Flow[Input, Output]:
    """Create a flow that routes items to different flows based on a selector function.

    For each item, applies the selector function to determine which case flow
    to use for processing.

    Args:
        selector: Function that returns a case key for each item
        cases: Dictionary mapping case keys to flows
        default: Optional default flow for unmatched cases

    Returns:
        A flow that routes items based on selector
    """

    async def _flow(
        stream: AsyncGenerator[Input, None]
    ) -> AsyncGenerator[Output, None]:
        """Route items to appropriate flows based on selector."""
        async for item in stream:
            case_key = selector(item)
            target_flow = cases.get(case_key, default)

            if target_flow is not None:
                # Apply target flow to a single-item stream
                single_item_stream = _create_single_item_stream(item)
                async for result in target_flow(single_item_stream):
                    yield result
            # If no matching case and no default, item is filtered out

    async def _create_single_item_stream(item: Input) -> AsyncGenerator[Input, None]:
        """Create a single-item stream."""
        yield item

    selector_name = get_function_name(selector)
    cases_count = len(cases)
    default_name = f", default={default.name}" if default else ""
    return Flow(
        _flow, name=f"switch({selector_name}, {cases_count} cases{default_name})"
    )


def tap_stream(side_effect: Callable[[Input], AnyValue]) -> Flow[Input, Input]:
    """Create a flow that applies a side effect to each item without changing the stream.

    Useful for logging, debugging, or triggering side effects while preserving
    the original stream data.

    Args:
        side_effect: Function to call for each item (can be sync or async)

    Returns:
        A flow that applies side effects and passes items through
    """

    async def _flow(stream: AsyncGenerator[Input, None]) -> AsyncGenerator[Input, None]:
        """Apply side effect to each item and pass through."""
        async for item in stream:
            await maybe_await(side_effect, item)
            yield item

    return Flow(_flow, name=f"tap({get_function_name(side_effect)})")


def while_condition_stream(
    condition: Callable[[Input], bool], transform: Flow[Input, Output]
) -> Flow[Input, Output]:
    """Create a flow that applies a transformation while a condition is true.

    Continues processing items with the transform flow as long as the condition
    returns True for each item.

    Args:
        condition: Function that determines whether to continue processing
        transform: Flow to apply while condition is true

    Returns:
        A flow that processes while condition holds
    """

    async def _flow(
        stream: AsyncGenerator[Input, None]
    ) -> AsyncGenerator[Output, None]:
        """Apply transformation while condition is true."""
        async for item in stream:
            if not condition(item):
                break

            # Apply transform to a single-item stream
            single_item_stream = _create_single_item_stream(item)
            async for result in transform(single_item_stream):
                yield result

    async def _create_single_item_stream(item: Input) -> AsyncGenerator[Input, None]:
        """Create a single-item stream."""
        yield item

    condition_name = get_function_name(condition)
    return Flow(_flow, name=f"while({condition_name}, {transform.name})")


def then_stream(side_effect: Callable[[Input], AnyValue]) -> Flow[Input, Input]:
    """Create a flow that applies a side effect sequentially after each item.

    Similar to tap_stream but emphasizes sequential execution.

    Args:
        side_effect: Function to call for each item (can be sync or async)

    Returns:
        A flow that applies side effects sequentially
    """

    async def _flow(stream: AsyncGenerator[Input, None]) -> AsyncGenerator[Input, None]:
        """Apply side effect sequentially after each item."""
        async for item in stream:
            yield item
            await maybe_await(side_effect, item)

    return Flow(_flow, name=f"then({get_function_name(side_effect)})")


def catch_and_continue_stream(
    handler: Callable[[Exception], AnyValue] | None = None,
) -> Flow[Input, Input]:
    """Create a flow that catches exceptions and continues processing.

    When an exception occurs, optionally calls a handler function and
    continues with the next item instead of propagating the exception.

    Args:
        handler: Optional function to handle exceptions

    Returns:
        A flow that catches exceptions and continues processing
    """

    async def _flow(stream: AsyncGenerator[Input, None]) -> AsyncGenerator[Input, None]:
        """Process stream with exception catching."""
        async for item in stream:
            try:
                yield item
            except Exception as e:
                if handler:
                    await maybe_await(handler, e)
                # Continue processing without yielding anything for this item

    handler_name = f"({get_function_name(handler)})" if handler else ""
    return Flow(_flow, name=f"catch_and_continue{handler_name}")


def circuit_breaker_stream(
    failure_threshold: int = 5, recovery_timeout: float = 60.0
) -> Flow[Input, Input]:
    """Create a flow that implements the circuit breaker pattern.

    Tracks failures and "opens" the circuit after too many failures,
    preventing further processing until a recovery timeout elapses.

    Args:
        failure_threshold: Number of failures before opening circuit
        recovery_timeout: Seconds to wait before attempting recovery

    Returns:
        A flow that implements circuit breaker behavior
    """
    failure_count = 0
    circuit_open = False
    last_failure_time = 0.0

    async def _flow(stream: AsyncGenerator[Input, None]) -> AsyncGenerator[Input, None]:
        """Process stream with circuit breaker protection."""
        nonlocal failure_count, circuit_open, last_failure_time

        async for item in stream:
            current_time = asyncio.get_event_loop().time()

            # Check if we can close the circuit
            if circuit_open and (current_time - last_failure_time) > recovery_timeout:
                circuit_open = False
                failure_count = 0

            # If circuit is open, reject the item
            if circuit_open:
                raise FlowExecutionError(
                    f"Circuit breaker open. Too many failures (threshold: {failure_threshold})"
                )

            try:
                yield item
                # Reset failure count on success
                failure_count = 0
            except Exception as e:
                failure_count += 1
                last_failure_time = current_time

                if failure_count >= failure_threshold:
                    circuit_open = True

                raise e

    return Flow(_flow, name=f"circuit_breaker({failure_threshold}, {recovery_timeout})")
