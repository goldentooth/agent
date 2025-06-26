"""Flow combinators for composing and transforming stream processing flows.

This module provides functional combinators that work with Flow objects,
enabling functional-style stream processing. These combinators are adapted
from the Thunk combinators but designed specifically for async stream operations.
"""

from __future__ import annotations
import asyncio
import logging
from typing import (
    AsyncIterator,
    Awaitable,
    Callable,
    TypeVar,
    Any,
)

from .main import Flow

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

    return Flow(_flow, name=f"filter({predicate.__name__})")


def map_stream(fn: Callable[[Input], Output]) -> Flow[Input, Output]:
    """Create a flow that maps a function over each item in the stream."""

    async def _flow(stream: AsyncIterator[Input]) -> AsyncIterator[Output]:
        """Map function over each item in the stream."""
        async for item in stream:
            yield fn(item)

    return Flow(_flow, name=f"map({fn.__name__})")


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


def log_stream(
    name: str, *, prefix: str = "", level: int = logging.DEBUG
) -> Flow[Input, Input]:
    """Create a flow that logs each stream item and passes it through unchanged.

    Useful for debugging flow pipelines by observing intermediate values
    without affecting the data flow.

    Args:
        name: Name for the flow (used in pipeline visualization)
        prefix: Optional prefix to add before the logged item
        level: Logging level (defaults to DEBUG)
    """

    async def _flow(stream: AsyncIterator[Input]) -> AsyncIterator[Input]:
        """Log each stream item and pass it through unchanged."""
        async for item in stream:
            # Use print for simplicity, in production you'd use proper logging
            if level >= logging.INFO:
                print(f"{prefix}{item}")
            yield item

    return Flow(
        _flow,
        name=f"log_stream({name})",
        metadata={
            "prefix": prefix,
            "level": level,
        },
    )


def identity_stream() -> Flow[Input, Input]:
    """Create a flow that passes the stream through unchanged."""

    async def _flow(stream: AsyncIterator[Input]) -> AsyncIterator[Input]:
        """Pass stream through unchanged."""
        async for item in stream:
            yield item

    return Flow(_flow, name="identity")


def if_then_stream(
    predicate: Callable[[Input], bool],
    if_flow: Flow[Input, Output],
    else_flow: Flow[Input, Output] | None = None,
) -> Flow[Input, Output]:
    """Create a flow that conditionally processes items based on a predicate.

    Items that match the predicate are processed by if_flow,
    items that don't match are processed by else_flow (or passed through if None).
    """

    async def _flow(stream: AsyncIterator[Input]) -> AsyncIterator[Output]:
        """Process items conditionally based on predicate."""
        async for item in stream:
            if predicate(item):
                # Create a single-item stream for the if_flow
                async def single_item_stream():
                    yield item

                async for result in if_flow(single_item_stream()):
                    yield result
            elif else_flow is not None:
                # Create a single-item stream for the else_flow
                async def single_item_stream():
                    yield item

                async for result in else_flow(single_item_stream()):
                    yield result
            else:
                # Pass through unchanged (assuming Input and Output are compatible)
                yield item  # type: ignore

    else_name = else_flow.name if else_flow else "identity"
    return Flow(
        _flow,
        name=f"if_then({predicate.__name__}, {if_flow.name}, {else_name})",
    )


def tap_stream(
    fn: Callable[[Input], Awaitable[None]] | Callable[[Input], None],
) -> Flow[Input, Input]:
    """Create a flow that applies a side-effect function to each item without changing the stream.

    Useful for logging, metrics collection, or other side effects that don't modify the data.
    """
    from goldentooth_agent.core.util import maybe_await

    async def _flow(stream: AsyncIterator[Input]) -> AsyncIterator[Input]:
        """Apply side-effect function to each item and pass it through."""
        async for item in stream:
            await maybe_await(fn, item)
            yield item

    return Flow(_flow, name=f"tap({getattr(fn, '__name__', 'function')})")


def delay_stream(seconds: float) -> Flow[Input, Input]:
    """Create a flow that delays each item in the stream by a given number of seconds."""

    async def _flow(stream: AsyncIterator[Input]) -> AsyncIterator[Input]:
        """Delay each item by the specified number of seconds."""
        async for item in stream:
            await asyncio.sleep(seconds)
            yield item

    return Flow(_flow, name=f"delay({seconds})")


def recover_stream(
    handler: Callable[[Exception, Input], Awaitable[Output]],
) -> Flow[Input, Output]:
    """Create a flow that handles exceptions and provides fallback values.

    When an exception occurs during stream processing, the handler function
    is called with the exception and the current item to provide a fallback value.
    """

    async def _flow(stream: AsyncIterator[Input]) -> AsyncIterator[Output]:
        """Process stream with exception handling."""
        async for item in stream:
            try:
                yield item  # type: ignore  # Assume Input and Output are compatible
            except Exception as e:
                fallback = await handler(e, item)
                yield fallback

    return Flow(
        _flow,
        name=f"recover({getattr(handler, '__name__', 'handler')})",
    )


def take_stream(n: int) -> Flow[Input, Input]:
    """Create a flow that takes only the first n items from the stream."""

    async def _flow(stream: AsyncIterator[Input]) -> AsyncIterator[Input]:
        """Take only the first n items from the stream."""
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


def batch_stream(size: int) -> Flow[Input, list[Input]]:
    """Create a flow that batches stream items into lists of specified size."""

    async def _flow(stream: AsyncIterator[Input]) -> AsyncIterator[list[Input]]:
        """Batch stream items into lists of specified size."""
        batch = []
        async for item in stream:
            batch.append(item)
            if len(batch) >= size:
                yield batch
                batch = []
        # Yield remaining items if any
        if batch:
            yield batch

    return Flow(_flow, name=f"batch({size})")


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


def retry_stream(n: int, flow: Flow[Input, Output]) -> Flow[Input, Output]:
    """Create a flow that retries processing items with another flow on failure."""

    async def _flow(stream: AsyncIterator[Input]) -> AsyncIterator[Output]:
        """Retry processing items with the given flow on failure."""
        async for item in stream:
            last_exception = None
            success = False

            for attempt in range(n):
                try:
                    # Create a single-item stream for the retry flow
                    async def single_item_stream():
                        yield item

                    result_stream = flow(single_item_stream())
                    async for result in result_stream:
                        yield result
                        success = True

                    if success:
                        break  # Success, move to next item

                except Exception as e:
                    last_exception = e
                    if attempt == n - 1:  # Last attempt
                        raise last_exception

    return Flow(_flow, name=f"retry({n}, {flow.name})")


def switch_stream(
    selector: Callable[[Input], str],
    cases: dict[str, Flow[Input, Output]],
    default: Flow[Input, Output] | None = None,
) -> Flow[Input, Output]:
    """Create a flow that routes items to different flows based on a selector function."""

    async def _flow(stream: AsyncIterator[Input]) -> AsyncIterator[Output]:
        """Route items to different flows based on selector function."""
        async for item in stream:
            key = selector(item)
            selected_flow = None

            if key in cases:
                selected_flow = cases[key]
            elif default:
                selected_flow = default
            else:
                raise KeyError(f"No case for key: {key}")

            # Create a single-item stream for the selected flow
            async def single_item_stream():
                yield item

            async for result in selected_flow(single_item_stream()):
                yield result

    default_name = default.name if default else "None"
    return Flow(
        _flow,
        name=f"switch({selector.__name__}, {list(cases.keys())}, {default_name})",
    )


def race_stream(flows: list[Flow[Input, Output]]) -> Flow[Input, Output]:
    """Create a flow that races multiple flows for each item and yields the first successful result.

    For each input item, all flows are tried simultaneously, and the first one to
    produce a result wins. If all flows fail, the last exception is raised.
    """

    async def _flow(stream: AsyncIterator[Input]) -> AsyncIterator[Output]:
        """Race multiple flows for each item."""
        if not flows:
            # Empty list of flows - pass through nothing
            return

        async for item in stream:
            # Create tasks for each flow
            async def run_flow(flow: Flow[Input, Output]) -> Output:
                async def single_item_stream():
                    yield item

                result_stream = flow(single_item_stream())
                async for result in result_stream:
                    return result
                raise RuntimeError(f"Flow {flow.name} produced no output")

            tasks = [asyncio.create_task(run_flow(flow)) for flow in flows]

            try:
                # Wait for the first successful result
                done, pending = await asyncio.wait(
                    tasks, return_when=asyncio.FIRST_COMPLETED
                )

                # Cancel remaining tasks
                for task in pending:
                    task.cancel()

                # Get the first successful result
                for task in done:
                    try:
                        result = await task
                        yield result
                        break
                    except Exception:
                        continue
                else:
                    # All completed tasks failed
                    raise RuntimeError("All flows failed")

            except Exception as e:
                # Cancel all tasks if something goes wrong
                for task in tasks:
                    if not task.done():
                        task.cancel()
                raise e

    flow_names = [flow.name for flow in flows]
    return Flow(_flow, name=f"race({', '.join(flow_names)})")


def parallel_stream(
    flows: list[Flow[Input, Output]],
) -> Flow[Input, list[Output | None]]:
    """Create a flow that runs multiple flows in parallel for each item and collects all results.

    For each input item, all flows are executed simultaneously, and all successful
    results are collected into a list. Failed flows contribute None to the result list.

    Note: If you want only successful results (filtering out None values),
    use parallel_stream_successful() instead.
    """

    async def _flow(stream: AsyncIterator[Input]) -> AsyncIterator[list[Output | None]]:
        """Run multiple flows in parallel for each item."""
        async for item in stream:
            # Create tasks for each flow
            async def run_flow(flow: Flow[Input, Output]) -> Output | None:
                try:

                    async def single_item_stream():
                        yield item

                    result_stream = flow(single_item_stream())
                    async for result in result_stream:
                        return result
                    return None  # Flow produced no output
                except Exception:
                    return None  # Flow failed

            tasks = [asyncio.create_task(run_flow(flow)) for flow in flows]
            results = await asyncio.gather(*tasks, return_exceptions=False)
            yield list(results)

    flow_names = [flow.name for flow in flows]
    return Flow(_flow, name=f"parallel({', '.join(flow_names)})")


def parallel_stream_successful(
    flows: list[Flow[Input, Output]],
) -> Flow[Input, list[Output]]:
    """Create a flow that runs multiple flows in parallel and collects only successful results.

    For each input item, all flows are executed simultaneously, and only successful
    results are collected into a list. Failed flows are ignored.
    """

    async def _flow(stream: AsyncIterator[Input]) -> AsyncIterator[list[Output]]:
        """Run multiple flows in parallel for each item, keeping only successful results."""
        async for item in stream:
            # Create tasks for each flow
            async def run_flow(flow: Flow[Input, Output]) -> Output | None:
                try:

                    async def single_item_stream():
                        yield item

                    result_stream = flow(single_item_stream())
                    async for result in result_stream:
                        return result
                    return None  # Flow produced no output
                except Exception:
                    return None  # Flow failed

            tasks = [asyncio.create_task(run_flow(flow)) for flow in flows]
            results = await asyncio.gather(*tasks, return_exceptions=False)
            # Filter out None values
            successful_results = [r for r in results if r is not None]
            yield successful_results

    flow_names = [flow.name for flow in flows]
    return Flow(_flow, name=f"parallel_successful({', '.join(flow_names)})")


# Utility function for creating source flows
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


def empty_flow() -> Flow[None, A]:
    """Create a flow that produces no items."""

    async def _flow(_: AsyncIterator[None]) -> AsyncIterator[A]:
        """Produce no items."""
        return
        yield  # unreachable

    return Flow(_flow, name="empty")


def flat_map_ctx_stream(
    fn: Callable[[Output, Input], AsyncIterator[Newput]],
) -> Flow[Input, Newput]:
    """Create a flow that flat-maps with access to both the item and original stream context.

    Unlike flat_map_stream which only gets the current item, this passes both the current
    item and the original stream input to the mapping function. This enables context-aware
    transformations that need information from the original stream.

    Args:
        fn: Function that takes (current_item, original_input) and returns an async iterator

    Returns:
        A flow that applies the context-aware flat mapping

    Note: This combinator requires caching original inputs, which may use significant memory
    for large streams. Consider using flat_map_stream if context access isn't needed.
    """

    async def _flow(stream: AsyncIterator[Input]) -> AsyncIterator[Newput]:
        """Apply context-aware flat mapping to the stream."""
        # Collect stream items with their original context
        items_with_context = []
        async for item in stream:
            items_with_context.append(item)

        # Process each item with access to all original context
        for original_item in items_with_context:
            # For each original item, apply it as context to the function
            async for mapped_item in fn(original_item, original_item):
                yield mapped_item

    return Flow(_flow, name=f"flat_map_ctx({getattr(fn, '__name__', 'function')})")


def guard_stream(
    predicate: Callable[[Input], bool], error_msg: str = "Guard condition failed"
) -> Flow[Input, Input]:
    """Create a flow that raises an exception if the predicate fails for any item.

    Unlike filter_stream which skips items that don't match the predicate,
    guard_stream raises an exception, stopping the entire stream processing.
    This is useful for validation and assertion-style checks.

    Args:
        predicate: Function that must return True for all items
        error_msg: Error message to include in the exception

    Returns:
        A flow that validates all items or raises an exception
    """

    async def _flow(stream: AsyncIterator[Input]) -> AsyncIterator[Input]:
        """Validate all stream items with the guard predicate."""
        async for item in stream:
            if not predicate(item):
                raise ValueError(f"{error_msg}: {item}")
            yield item

    return Flow(_flow, name=f"guard({predicate.__name__})")


def then_stream(
    side_effect: Callable[[Input], Awaitable[None]] | Callable[[Input], None],
) -> Flow[Input, Input]:
    """Create a flow that executes a side effect for each item and passes the item through unchanged.

    This is similar to tap_stream but with different semantics - 'then' suggests
    sequential execution after processing, while 'tap' suggests observation.

    Args:
        side_effect: Function to execute for each item (sync or async)

    Returns:
        A flow that executes side effects and passes items through
    """
    from goldentooth_agent.core.util import maybe_await

    async def _flow(stream: AsyncIterator[Input]) -> AsyncIterator[Input]:
        """Execute side effect for each item and pass through."""
        async for item in stream:
            await maybe_await(side_effect, item)
            yield item

    return Flow(_flow, name=f"then({getattr(side_effect, '__name__', 'function')})")


def memoize_stream(key_fn: Callable[[Input], str] = str) -> Flow[Input, Input]:
    """Create a flow that memoizes stream processing based on input keys.

    Items with the same key (as determined by key_fn) are only processed once.
    Subsequent items with the same key are returned from cache.

    Args:
        key_fn: Function to generate cache keys from input items

    Returns:
        A flow that caches items based on keys

    Warning: Cache grows unbounded and may cause memory leaks for long-running
    processes. Consider size limits for production use.
    """
    cache: dict[str, Input] = {}

    async def _flow(stream: AsyncIterator[Input]) -> AsyncIterator[Input]:
        """Memoize stream items based on key function."""
        async for item in stream:
            key = key_fn(item)
            if key in cache:
                yield cache[key]
            else:
                cache[key] = item
                yield item

    return Flow(_flow, name=f"memoize({getattr(key_fn, '__name__', 'function')})")


def while_condition_stream(
    condition: Callable[[Input], bool], transform: Flow[Input, Input]
) -> Flow[Input, Input]:
    """Create a flow that applies a transformation while a condition is true.

    For each item, if the condition is true, the item is processed by the transform flow.
    If the condition is false, the item passes through unchanged.
    Processing continues until the condition becomes false for an item.

    Args:
        condition: Predicate that determines whether to apply transformation
        transform: Flow to apply when condition is true

    Returns:
        A flow that conditionally transforms items while condition holds
    """

    async def _flow(stream: AsyncIterator[Input]) -> AsyncIterator[Input]:
        """Apply transformation while condition is true."""
        async for item in stream:
            if condition(item):
                # Create single-item stream for transform
                async def single_item():
                    yield item

                # Apply transform and yield result
                transform_stream = transform(single_item())
                async for transformed in transform_stream:
                    yield transformed
            else:
                # Condition failed, stop processing and yield remaining items unchanged
                yield item
                async for remaining in stream:
                    yield remaining
                break

    return Flow(_flow, name=f"while({condition.__name__}, {transform.name})")


def flatten_stream() -> Flow[AsyncIterator[Input], Input]:
    """Create a flow that flattens streams of streams into a single stream.

    Takes a stream where each item is itself an AsyncIterator, and flattens
    all the nested streams into a single output stream.

    Returns:
        A flow that flattens nested async iterators
    """

    async def _flow(
        stream: AsyncIterator[AsyncIterator[Input]],
    ) -> AsyncIterator[Input]:
        """Flatten nested async iterators into a single stream."""
        async for inner_stream in stream:
            async for item in inner_stream:
                yield item

    return Flow(_flow, name="flatten")


def collect_stream() -> Flow[Input, list[Input]]:
    """Create a flow that collects all stream items into a single list.

    This is a terminal operation that consumes the entire stream and
    yields a single list containing all items. Similar to to_list() but
    as a combinator that can be composed with other flows.

    Returns:
        A flow that collects stream items into a list
    """

    async def _flow(stream: AsyncIterator[Input]) -> AsyncIterator[list[Input]]:
        """Collect all stream items into a single list."""
        items = []
        async for item in stream:
            items.append(item)
        yield items

    return Flow(_flow, name="collect")


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
            except asyncio.TimeoutError:
                raise TimeoutError(
                    f"Processing timed out after {seconds} seconds for item: {item}"
                )

    async def _identity_async(item: Input) -> Input:
        """Identity function that can be awaited."""
        return item

    return Flow(_flow, name=f"timeout({seconds})")


def circuit_breaker_stream(
    failure_threshold: int, reset_timeout: float
) -> Flow[Input, Input]:
    """Create a flow that implements circuit breaker pattern for stream processing.

    The circuit breaker opens after a specified number of consecutive failures,
    preventing further processing until a reset timeout period has elapsed.

    Args:
        failure_threshold: Number of consecutive failures before opening circuit
        reset_timeout: Time to wait before attempting to close circuit again

    Returns:
        A flow that implements circuit breaker pattern
    """
    failure_count = 0
    circuit_open = False
    last_failure_time = 0.0

    async def _flow(stream: AsyncIterator[Input]) -> AsyncIterator[Input]:
        """Process stream with circuit breaker protection."""
        nonlocal failure_count, circuit_open, last_failure_time

        async for item in stream:
            current_time = asyncio.get_event_loop().time()

            # Check if circuit should be reset
            if circuit_open and (current_time - last_failure_time) >= reset_timeout:
                circuit_open = False
                failure_count = 0

            # If circuit is open, reject all items
            if circuit_open:
                raise RuntimeError(
                    f"Circuit breaker is open. Reset in {reset_timeout - (current_time - last_failure_time):.1f}s"
                )

            try:
                yield item
                failure_count = 0  # Reset on success
            except Exception as e:
                failure_count += 1
                last_failure_time = current_time

                if failure_count >= failure_threshold:
                    circuit_open = True

                raise e

    return Flow(_flow, name=f"circuit_breaker({failure_threshold}, {reset_timeout})")


def catch_and_continue_stream(
    handler: Callable[[Exception, Input], Output | None] = lambda e, x: None
) -> Flow[Input, Output]:
    """Create a flow that catches exceptions and continues processing with fallback values.

    When an exception occurs, the handler is called to provide a fallback value.
    If the handler returns None, the item is skipped. Otherwise, the fallback
    value is yielded and processing continues.

    Args:
        handler: Function to handle exceptions and provide fallback values

    Returns:
        A flow that handles exceptions gracefully
    """

    async def _flow(stream: AsyncIterator[Input]) -> AsyncIterator[Output]:
        """Process stream with exception handling and continuation."""
        async for item in stream:
            try:
                yield item  # type: ignore  # Assume Input and Output are compatible
            except Exception as e:
                fallback = handler(e, item)
                if fallback is not None:
                    yield fallback
                # If fallback is None, skip this item and continue

    return Flow(
        _flow, name=f"catch_and_continue({getattr(handler, '__name__', 'handler')})"
    )


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

    return Flow(_flow, name=f"until({predicate.__name__})")


def scan_stream(
    fn: Callable[[Output, Input], Output], initial: Output
) -> Flow[Input, Output]:
    """Create a flow that performs a running accumulation (scan/fold) over the stream.

    Similar to reduce, but yields intermediate results. The accumulator
    function receives the current accumulated value and the next item,
    returning the new accumulated value.

    Args:
        fn: Function that combines accumulator and current item
        initial: Initial value for the accumulator

    Returns:
        A flow that yields running accumulation results
    """

    async def _flow(stream: AsyncIterator[Input]) -> AsyncIterator[Output]:
        """Perform running accumulation over the stream."""
        accumulator = initial
        yield accumulator  # Yield initial value

        async for item in stream:
            accumulator = fn(accumulator, item)
            yield accumulator

    return Flow(_flow, name=f"scan({getattr(fn, '__name__', 'function')}, {initial})")


def zip_stream(other_stream: AsyncIterator[B]) -> Flow[A, tuple[A, B]]:
    """Create a flow that zips items with another stream.

    Combines items from two streams pairwise. Processing stops when
    either stream is exhausted.

    Args:
        other_stream: The stream to zip with

    Returns:
        A flow that yields tuples of paired items
    """

    async def _flow(stream: AsyncIterator[A]) -> AsyncIterator[tuple[A, B]]:
        """Zip two streams together."""
        other_iter = other_stream.__aiter__()

        async for item in stream:
            try:
                other_item = await other_iter.__anext__()
                yield (item, other_item)
            except StopAsyncIteration:
                break  # Other stream exhausted

    return Flow(_flow, name="zip")


def chain_stream(*streams: AsyncIterator[Input]) -> Flow[None, Input]:
    """Create a flow that chains multiple streams sequentially.

    Processes all items from the first stream, then all items from
    the second stream, and so on.

    Args:
        *streams: Variable number of streams to chain

    Returns:
        A flow that yields items from all streams in sequence
    """

    async def _flow(_: AsyncIterator[None]) -> AsyncIterator[Input]:
        """Chain multiple streams sequentially."""
        for stream in streams:
            async for item in stream:
                yield item

    return Flow(_flow, name=f"chain({len(streams)} streams)")


def merge_stream(*flows: Flow[Input, Output]) -> Flow[Input, Output]:
    """Create a flow that merges multiple flows concurrently.

    Unlike chain_stream which processes sequentially, merge_stream
    processes all flows concurrently and yields items as they arrive.

    Args:
        *flows: Variable number of flows to merge

    Returns:
        A flow that yields items from all flows concurrently
    """

    async def _flow(stream: AsyncIterator[Input]) -> AsyncIterator[Output]:
        """Merge multiple flows concurrently."""
        if not flows:
            return

        # Create iterator from input stream that can be shared
        stream_items = []
        async for item in stream:
            stream_items.append(item)

        # Create tasks for each flow
        async def run_flow(flow: Flow[Input, Output]) -> AsyncIterator[Output]:
            async def item_stream():
                for item in stream_items:
                    yield item

            return flow(item_stream())

        # Collect all results concurrently
        tasks = [asyncio.create_task(run_flow(flow)) for flow in flows]

        # Yield results as they become available
        for task in asyncio.as_completed(tasks):
            result_stream = await task
            async for item in result_stream:
                yield item

    flow_names = [flow.name for flow in flows]
    return Flow(_flow, name=f"merge({', '.join(flow_names)})")


def distinct_stream(key_fn: Callable[[Input], str] = str) -> Flow[Input, Input]:
    """Create a flow that filters out duplicate items based on a key function.

    Only the first occurrence of each unique key is yielded.

    Args:
        key_fn: Function to generate keys for uniqueness checking

    Returns:
        A flow that yields only unique items
    """
    seen_keys: set[str] = set()

    async def _flow(stream: AsyncIterator[Input]) -> AsyncIterator[Input]:
        """Filter out duplicate items based on key function."""
        async for item in stream:
            key = key_fn(item)
            if key not in seen_keys:
                seen_keys.add(key)
                yield item

    return Flow(_flow, name=f"distinct({getattr(key_fn, '__name__', 'function')})")


def chunk_stream(size: int) -> Flow[Input, list[Input]]:
    """Create a flow that groups items into chunks of specified size.

    Similar to batch_stream but with different semantics - chunk implies
    fixed-size groups for processing efficiency.

    Args:
        size: Number of items per chunk

    Returns:
        A flow that yields chunks of items
    """

    async def _flow(stream: AsyncIterator[Input]) -> AsyncIterator[list[Input]]:
        """Group items into fixed-size chunks."""
        chunk = []
        async for item in stream:
            chunk.append(item)
            if len(chunk) >= size:
                yield chunk
                chunk = []
        # Yield remaining items as final chunk
        if chunk:
            yield chunk

    return Flow(_flow, name=f"chunk({size})")


def window_stream(size: int, step: int = 1) -> Flow[Input, list[Input]]:
    """Create a flow that generates sliding windows over the stream.

    Creates overlapping windows of items, useful for time-series analysis
    or pattern detection.

    Args:
        size: Number of items in each window
        step: Number of items to advance between windows (default 1)

    Returns:
        A flow that yields sliding windows of items
    """

    async def _flow(stream: AsyncIterator[Input]) -> AsyncIterator[list[Input]]:
        """Generate sliding windows over the stream."""
        window = []

        async for item in stream:
            window.append(item)

            # If window is full, yield it and advance by step
            if len(window) == size:
                yield list(window)  # Copy the window
                # Remove step items from the beginning
                for _ in range(min(step, len(window))):
                    window.pop(0)

    return Flow(_flow, name=f"window({size}, {step})")
