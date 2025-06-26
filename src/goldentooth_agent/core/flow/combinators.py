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
    initial_stream: AsyncIterator[Input], 
    steps: list[Flow[Input, Input]]
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


def flat_map_stream(fn: Callable[[Input], AsyncIterator[Output]]) -> Flow[Input, Output]:
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
                done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
                
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
    return Flow(
        _flow, 
        name=f"race({', '.join(flow_names)})"
    )


def parallel_stream(flows: list[Flow[Input, Output]]) -> Flow[Input, list[Output]]:
    """Create a flow that runs multiple flows in parallel for each item and collects all results.
    
    For each input item, all flows are executed simultaneously, and all successful
    results are collected into a list. Failed flows contribute None to the result list.
    """
    
    async def _flow(stream: AsyncIterator[Input]) -> AsyncIterator[list[Output]]:
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
    return Flow(
        _flow,
        name=f"parallel({', '.join(flow_names)})"
    )


# Utility function for creating source flows
def range_flow(start: int, stop: int, step: int = 1) -> Flow[None, int]:
    """Create a flow that generates a range of integers."""
    
    async def _flow(_: AsyncIterator[None]) -> AsyncIterator[int]:
        """Generate range of integers."""
        for i in range(start, stop, step):
            yield i
    
    return Flow(_flow, name=f"range({start}, {stop}, {step})")


def repeat_flow(value: Input, times: int | None = None) -> Flow[None, Input]:
    """Create a flow that repeats a value a specified number of times (or infinitely)."""
    
    async def _flow(_: AsyncIterator[None]) -> AsyncIterator[Input]:
        """Repeat value specified number of times."""
        if times is None:
            while True:
                yield value
        else:
            for _ in range(times):
                yield value
    
    times_str = str(times) if times is not None else "∞"
    return Flow(_flow, name=f"repeat({value}, {times_str})")


def empty_flow() -> Flow[None, Input]:
    """Create a flow that produces no items."""
    
    async def _flow(_: AsyncIterator[None]) -> AsyncIterator[Input]:
        """Produce no items."""
        return
        yield  # unreachable
    
    return Flow(_flow, name="empty")