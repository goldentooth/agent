"""Advanced combinators for complex stream operations.

This module provides combinators for parallel processing, merging, racing,
zipping, and other advanced stream composition patterns.
"""

from __future__ import annotations

import asyncio
from collections.abc import Callable
from typing import Any, AsyncGenerator, TypeVar, cast

from ..exceptions import FlowExecutionError
from ..flow import Flow
from .utils import create_single_item_stream, get_function_name

Input = TypeVar("Input")
Output = TypeVar("Output")
Newput = TypeVar("Newput")
OtherInput = TypeVar("OtherInput")

# Type aliases
AnyValue = Any
AnyTask = asyncio.Task[Any]
AnyQueue = asyncio.Queue[Any]


async def _run_single_flow(flow: Flow[Input, Output], item: Input) -> Output:
    """Run a flow on a single item and return first result."""
    single_stream = create_single_item_stream(item)
    async for result in flow(single_stream):
        return result
    raise FlowExecutionError("Flow produced no results")


def _create_race_tasks(
    flows: tuple[Flow[Input, Output], ...], item: Input
) -> list[AnyTask]:
    """Create racing tasks for all flows with the given item."""
    return [asyncio.create_task(_run_single_flow(flow, item)) for flow in flows]


async def _get_first_successful_result(done_tasks: set[AnyTask]) -> object:
    """Get the first successful result from completed tasks."""
    for task in done_tasks:
        try:
            result = await task
            return result
        except Exception:
            continue
    raise FlowExecutionError("All racing flows failed")


async def _cancel_pending_tasks(pending_tasks: set[AnyTask]) -> None:
    """Cancel and cleanup pending tasks."""
    for task in pending_tasks:
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass


async def _race_flows_for_item(
    flows: tuple[Flow[Input, Output], ...], item: Input
) -> Output:
    """Race multiple flows for a single item and return first result."""
    tasks = _create_race_tasks(flows, item)

    done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)

    try:
        return cast(Output, await _get_first_successful_result(done))
    finally:
        await _cancel_pending_tasks(pending)


def race_stream(*flows: Flow[Input, Output]) -> Flow[Input, Output]:
    """Create a flow that races multiple flows and yields the first result.

    For each input item, runs all flows in parallel and yields the result
    from whichever flow completes first.

    Args:
        *flows: Flows to race against each other

    Returns:
        A flow that yields first results from racing flows
    """

    async def _flow(
        stream: AsyncGenerator[Input, None],
    ) -> AsyncGenerator[Output, None]:
        """Race multiple flows for each item."""
        async for item in stream:
            if not flows:
                continue

            result = await _race_flows_for_item(flows, item)
            yield result

    flow_names = ", ".join(flow.name for flow in flows)
    return Flow(_flow, name=f"race({flow_names})")


async def _run_flow_collect_all(flow: Flow[Input, Output], item: Input) -> list[Output]:
    """Run a flow and collect all results."""
    single_stream = create_single_item_stream(item)
    return [result async for result in flow(single_stream)]


def _create_parallel_tasks(
    flows: tuple[Flow[Input, Output], ...], item: Input
) -> list[AnyTask]:
    """Create tasks to run all flows in parallel."""
    return [asyncio.create_task(_run_flow_collect_all(flow, item)) for flow in flows]


def _flatten_results(results: list[list[Any]]) -> list[Any]:
    """Flatten list of lists into a single list."""
    flattened: list[Any] = []
    for result_list in results:
        flattened.extend(result_list)
    return flattened


async def _run_parallel_all(
    flows: tuple[Flow[Input, Output], ...], item: Input
) -> list[Output]:
    """Run all flows in parallel and collect all results."""
    tasks = _create_parallel_tasks(flows, item)
    try:
        results = await asyncio.gather(*tasks)
        return _flatten_results(results)
    except Exception as e:
        raise FlowExecutionError(f"Parallel execution failed: {e}") from e


def parallel_stream(*flows: Flow[Input, Output]) -> Flow[Input, list[Output]]:
    """Create a flow that runs multiple flows in parallel and collects all results.

    For each input item, runs all flows in parallel and yields a list of all results.

    Args:
        *flows: Flows to run in parallel

    Returns:
        A flow that yields lists of results from parallel execution
    """

    async def _flow(
        stream: AsyncGenerator[Input, None],
    ) -> AsyncGenerator[list[Output], None]:
        """Run multiple flows in parallel for each item."""
        async for item in stream:
            yield await _run_parallel_all(flows, item)

    flow_names = ", ".join(flow.name for flow in flows)
    return Flow(_flow, name=f"parallel({flow_names})")


async def _run_flow_safely(
    flow: Flow[Input, Output], item: Input
) -> list[Output] | None:
    """Run a flow safely and return results or None on error."""
    single_stream = create_single_item_stream(item)
    try:
        return [result async for result in flow(single_stream)]
    except Exception:
        return None


def _create_safe_flow_tasks(
    flows: tuple[Flow[Input, Output], ...], item: Input
) -> list[AnyTask]:
    """Create tasks to run flows safely."""
    return [asyncio.create_task(_run_flow_safely(flow, item)) for flow in flows]


def _collect_successful_results(results: list[Any]) -> list[Any]:
    """Collect successful results from task results."""
    successful: list[Any] = []
    for result in results:
        if result is not None and isinstance(result, list):
            successful.extend(cast(list[Any], result))
    return successful


async def _run_parallel_successful(
    flows: tuple[Flow[Input, Output], ...], item: Input
) -> list[Output]:
    """Run flows in parallel and return only successful results."""
    tasks = _create_safe_flow_tasks(flows, item)
    results = await asyncio.gather(*tasks, return_exceptions=True)
    return _collect_successful_results(results)


def parallel_stream_successful(
    *flows: Flow[Input, Output]
) -> Flow[Input, list[Output]]:
    """Create a flow that runs flows in parallel and yields only successful results.

    Ignores flows that raise exceptions and yields results from successful flows only.

    Args:
        *flows: Flows to run in parallel

    Returns:
        A flow that yields lists of successful results
    """

    async def _flow(
        stream: AsyncGenerator[Input, None],
    ) -> AsyncGenerator[list[Output], None]:
        """Run flows in parallel and collect successful results."""
        async for item in stream:
            yield await _run_parallel_successful(flows, item)

    flow_names = ", ".join(flow.name for flow in flows)
    return Flow(_flow, name=f"parallel_successful({flow_names})")


async def _get_next_or_stop(other_iter: Any) -> Any:
    """Get next item from iterator or raise StopAsyncIteration."""
    return await anext(other_iter)


async def _zip_streams(
    stream: AsyncGenerator[Input, None], other: AsyncGenerator[OtherInput, None]
) -> AsyncGenerator[tuple[Input, OtherInput], None]:
    """Core logic for zipping two streams."""
    other_iter = aiter(other)

    async for item in stream:
        try:
            other_item = await _get_next_or_stop(other_iter)
            yield (item, other_item)
        except StopAsyncIteration:
            break


def zip_stream(
    other: AsyncGenerator[OtherInput, None],
) -> Flow[Input, tuple[Input, OtherInput]]:
    """Create a flow that zips items with another stream.

    Pairs each item from the main stream with the corresponding item
    from the other stream.

    Args:
        other: The other stream to zip with

    Returns:
        A flow that yields tuples of paired items
    """

    async def _flow(
        stream: AsyncGenerator[Input, None],
    ) -> AsyncGenerator[tuple[Input, OtherInput], None]:
        """Zip items with another stream."""
        async for result in _zip_streams(stream, other):
            yield result

    return Flow(_flow, name="zip")


async def _chain_all_streams(
    streams: tuple[AsyncGenerator[Input, None], ...],
) -> AsyncGenerator[Input, None]:
    """Chain all streams sequentially."""
    for stream in streams:
        async for item in stream:
            yield item


def chain_stream(*streams: AsyncGenerator[Input, None]) -> Flow[None, Input]:
    """Create a flow that chains multiple streams sequentially.

    Yields all items from the first stream, then all from the second, etc.

    Args:
        *streams: Streams to chain together

    Returns:
        A flow that yields items from all streams in sequence
    """

    async def _flow(_: AsyncGenerator[None, None]) -> AsyncGenerator[Input, None]:
        """Chain multiple streams sequentially."""
        async for item in _chain_all_streams(streams):
            yield item

    return Flow(_flow, name=f"chain({len(streams)} streams)")


async def _create_replay_stream(items: list[Input]) -> AsyncGenerator[Input, None]:
    """Create a stream that replays the given items."""
    for item in items:
        yield item


async def _run_flow_task(
    flow: Flow[Input, Output], items: list[Input]
) -> AsyncGenerator[Output, None]:
    """Run a flow with replayed input items."""
    return flow(_create_replay_stream(items))


async def _collect_flow_results(task: AnyTask, result_queue: AnyQueue) -> None:
    """Collect results from a flow task into the result queue."""
    try:
        flow_iter = await task
        async for result in flow_iter:
            await result_queue.put(result)
    except Exception as e:
        await result_queue.put(e)
    finally:
        await result_queue.put(None)  # Signal completion


async def _cleanup_collection_tasks(collection_tasks: list[asyncio.Task[None]]) -> None:
    """Cancel and cleanup collection tasks."""
    for task in collection_tasks:
        if not task.done():
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass


def _create_flow_tasks(
    flows: tuple[Flow[Input, Output], ...], items: list[Input]
) -> list[AnyTask]:
    """Create async tasks for each flow."""
    return [asyncio.create_task(_run_flow_task(flow, items)) for flow in flows]


def _create_collection_tasks(
    tasks: list[AnyTask], result_queue: AnyQueue
) -> list[asyncio.Task[None]]:
    """Create tasks to collect results from flow tasks."""
    return [
        asyncio.create_task(_collect_flow_results(task, result_queue)) for task in tasks
    ]


async def _process_queue_results(
    result_queue: AnyQueue, total_flows: int
) -> AsyncGenerator[Any, None]:
    """Process results from the result queue until all flows complete."""
    completed_flows = 0

    while completed_flows < total_flows:
        result: Any = await result_queue.get()

        if result is None:
            completed_flows += 1
        elif isinstance(result, Exception):
            raise result
        else:
            yield result


async def _merge_flow_results(
    flows: tuple[Flow[Input, Output], ...], items: list[Input]
) -> AsyncGenerator[Output, None]:
    """Merge results from multiple flows using a queue."""
    tasks = _create_flow_tasks(flows, items)
    result_queue: AnyQueue = asyncio.Queue()
    collection_tasks = _create_collection_tasks(tasks, result_queue)

    try:
        async for result in _process_queue_results(result_queue, len(flows)):
            yield result
    finally:
        await _cleanup_collection_tasks(collection_tasks)


def merge_stream(*flows: Flow[Input, Output]) -> Flow[Input, Output]:
    """Create a flow that merges results from multiple flows concurrently.

    Runs all flows on the same input stream and merges their outputs
    as they become available.

    Args:
        *flows: Flows to merge

    Returns:
        A flow that yields merged results from all flows
    """

    async def _flow(
        stream: AsyncGenerator[Input, None],
    ) -> AsyncGenerator[Output, None]:
        """Merge results from multiple flows."""
        items = [item async for item in stream]

        if not items:
            return

        async for result in _merge_flow_results(flows, items):
            yield result

    flow_names = ", ".join(flow.name for flow in flows)
    return Flow(_flow, name=f"merge({flow_names})")


def merge_flows(*flows: Flow[Input, Input]) -> Flow[Input, Input]:
    """Create a flow that merges multiple flows that operate on the same input.

    Similar to merge_stream but for flows that have the same input/output types.

    Args:
        *flows: Flows to merge (must have same input/output types)

    Returns:
        A flow that merges all input flows
    """
    return merge_stream(*flows)


async def _get_first_other_item(
    other_iter: Any,
) -> Any:
    """Get the first item from the other stream."""
    try:
        return await anext(other_iter)
    except StopAsyncIteration:
        return None


async def _update_latest_value(other_iter: Any, latest_holder: list[Any]) -> None:
    """Background task to continuously update the latest value."""
    try:
        async for item in other_iter:
            latest_holder[0] = item
    except Exception:
        pass


async def _cleanup_update_task(update_task: asyncio.Task[None]) -> None:
    """Cancel and cleanup the background update task."""
    update_task.cancel()
    try:
        await update_task
    except asyncio.CancelledError:
        pass


async def _combine_with_latest(
    stream: AsyncGenerator[Input, None], other: AsyncGenerator[OtherInput, None]
) -> AsyncGenerator[tuple[Input, OtherInput], None]:
    """Core logic for combining stream items with latest other value."""
    other_iter = aiter(other)
    latest_other = await _get_first_other_item(other_iter)

    if latest_other is None:
        return

    latest_holder: list[Any] = [latest_other]
    update_task = asyncio.create_task(_update_latest_value(other_iter, latest_holder))

    try:
        async for item in stream:
            if latest_holder[0] is not None:
                yield (item, latest_holder[0])
    finally:
        await _cleanup_update_task(update_task)


def combine_latest_stream(
    other: AsyncGenerator[OtherInput, None],
) -> Flow[Input, tuple[Input, OtherInput]]:
    """Create a flow that combines items with the latest value from another stream.

    For each item in the main stream, emits a tuple with that item and
    the most recent item from the other stream.

    Args:
        other: The other stream to combine with

    Returns:
        A flow that yields tuples of (current_item, latest_other_item)
    """

    async def _flow(
        stream: AsyncGenerator[Input, None],
    ) -> AsyncGenerator[tuple[Input, OtherInput], None]:
        """Combine items with latest value from other stream."""
        async for result in _combine_with_latest(stream, other):
            yield result

    return Flow(_flow, name="combine_latest")


async def _apply_flat_map_with_context(
    fn: Callable[[Any, Any], AsyncGenerator[Any, None]], item: Any
) -> AsyncGenerator[Any, None]:
    """Apply flat map function with context to a single item."""
    # LIMITATION: This simplified version passes the item as both arguments.
    # A full implementation would maintain proper context through the flow chain.
    # This is a known limitation documented in the function's docstring.
    async for result in fn(item, item):
        yield result


def flat_map_ctx_stream(
    fn: Callable[[Output, Input], AsyncGenerator[Newput, None]],
) -> Flow[Input, Newput]:
    """Create a flow that flat-maps with access to both item and original context.

    Unlike flat_map_stream which only gets the current item, this passes both
    the current item and the original stream input to the mapping function.

    **LIMITATION**: In this simplified implementation, the same item is passed
    as both the current item and original context. A full implementation would
    need to maintain proper context through the flow transformation chain.
    This is a known limitation that will be addressed in future work.

    Args:
        fn: Function that takes (current_item, original_input) and returns async iterator

    Returns:
        A flow that flat-maps with context access (simplified - see limitation above)
    """

    async def _flow(
        stream: AsyncGenerator[Input, None],
    ) -> AsyncGenerator[Newput, None]:
        """Flat-map with access to original context."""
        async for item in stream:
            async for result in _apply_flat_map_with_context(fn, item):
                yield result

    return Flow(_flow, name=f"flat_map_ctx({get_function_name(fn)})")


async def _collect_from_generator(
    gen: AsyncGenerator[Input, None], result_queue: AnyQueue
) -> None:
    """Collect items from a generator into the result queue."""
    try:
        async for item in gen:
            await result_queue.put(item)
    except Exception as e:
        await result_queue.put(e)
    finally:
        await result_queue.put(None)  # Signal completion


def _create_generator_collection_tasks(
    generators: tuple[AsyncGenerator[Input, None], ...], result_queue: AnyQueue
) -> list[asyncio.Task[None]]:
    """Create tasks to collect from all generators."""
    return [
        asyncio.create_task(_collect_from_generator(gen, result_queue))
        for gen in generators
    ]


async def _cleanup_generator_tasks(tasks: list[asyncio.Task[None]]) -> None:
    """Cancel and cleanup generator collection tasks."""
    for task in tasks:
        if not task.done():
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass


async def merge_async_generators(
    *generators: AsyncGenerator[Input, None],
) -> AsyncGenerator[Input, None]:
    """Utility function to merge multiple async generators.

    This is a utility function used by other combinators to merge async iterators.

    Args:
        *generators: Async generators to merge

    Returns:
        Async iterator that yields from all generators concurrently
    """
    if not generators:
        return

    result_queue: AnyQueue = asyncio.Queue()
    tasks = _create_generator_collection_tasks(generators, result_queue)

    try:
        async for result in _process_queue_results(result_queue, len(generators)):
            yield result
    finally:
        await _cleanup_generator_tasks(tasks)
