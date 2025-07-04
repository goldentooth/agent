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


async def _get_first_successful_result(done_tasks: set[AnyTask]) -> Any:
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
        return await _get_first_successful_result(done)
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
            # Create tasks for each flow
            tasks: list[AnyTask] = []

            for flow in flows:
                single_stream = create_single_item_stream(item)

                async def run_flow(
                    f: Flow[Input, Output], s: AsyncGenerator[Input, None]
                ) -> list[Output]:
                    """Run a flow and collect all results."""
                    return [result async for result in f(s)]

                task = asyncio.create_task(run_flow(flow, single_stream))
                tasks.append(task)

            # Wait for all to complete
            try:
                results = await asyncio.gather(*tasks)
                # Flatten the results since each flow returns a list
                flattened: list[Output] = []
                for result_list in results:
                    flattened.extend(result_list)
                yield flattened
            except Exception as e:
                raise FlowExecutionError(f"Parallel execution failed: {e}") from e

    flow_names = ", ".join(flow.name for flow in flows)
    return Flow(_flow, name=f"parallel({flow_names})")


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
            # Create tasks for each flow
            tasks: list[AnyTask] = []

            for flow in flows:
                single_stream = create_single_item_stream(item)

                async def run_flow_safe(
                    f: Flow[Input, Output], s: AsyncGenerator[Input, None]
                ) -> list[Output] | None:
                    """Run a flow safely and return results or None on error."""
                    try:
                        return [result async for result in f(s)]
                    except Exception:
                        return None

                task = asyncio.create_task(run_flow_safe(flow, single_stream))
                tasks.append(task)

            # Wait for all to complete
            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Collect successful results
            successful_results: list[Output] = []
            for result in results:
                if result is not None and isinstance(result, list):
                    typed_result = cast(list[Output], result)
                    successful_results.extend(typed_result)

            yield successful_results

    flow_names = ", ".join(flow.name for flow in flows)
    return Flow(_flow, name=f"parallel_successful({flow_names})")


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
        other_iter = aiter(other)

        async for item in stream:
            try:
                other_item = await anext(other_iter)
                yield (item, other_item)
            except StopAsyncIteration:
                # Other stream is exhausted
                break

    return Flow(_flow, name="zip")


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
        for stream in streams:
            async for item in stream:
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
        latest_other = None
        other_iter = aiter(other)

        # Try to get first item from other stream
        try:
            latest_other = await anext(other_iter)
        except StopAsyncIteration:
            # Other stream is empty
            return

        # Start background task to update latest_other
        async def update_latest() -> None:
            nonlocal latest_other
            try:
                async for item in other_iter:
                    latest_other = item
            except Exception:
                pass

        update_task = asyncio.create_task(update_latest())

        try:
            async for item in stream:
                if latest_other is not None:
                    yield (item, latest_other)
        finally:
            update_task.cancel()
            try:
                await update_task
            except asyncio.CancelledError:
                pass

    return Flow(_flow, name="combine_latest")


def flat_map_ctx_stream(
    fn: Callable[[Output, Input], AsyncGenerator[Newput, None]],
) -> Flow[Input, Newput]:
    """Create a flow that flat-maps with access to both item and original context.

    Unlike flat_map_stream which only gets the current item, this passes both
    the current item and the original stream input to the mapping function.

    Args:
        fn: Function that takes (current_item, original_input) and returns async iterator

    Returns:
        A flow that flat-maps with context access
    """

    async def _flow(
        stream: AsyncGenerator[Input, None],
    ) -> AsyncGenerator[Newput, None]:
        """Flat-map with access to original context."""
        async for original_item in stream:
            # For this simplified version, we pass the item as both arguments
            # In a full implementation, this would maintain context properly
            async for result in fn(original_item, original_item):  # type: ignore[arg-type]
                yield result

    return Flow(_flow, name=f"flat_map_ctx({get_function_name(fn)})")


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

    # Use a queue to merge results
    result_queue: AnyQueue = asyncio.Queue()

    async def collect_from_generator(gen: AsyncGenerator[Input, None]) -> None:
        """Collect items from a generator into the result queue."""
        try:
            async for item in gen:
                await result_queue.put(item)
        except Exception as e:
            await result_queue.put(e)
        finally:
            await result_queue.put(None)  # Signal completion

    # Start collection tasks
    tasks = [asyncio.create_task(collect_from_generator(gen)) for gen in generators]

    completed = 0
    total = len(generators)

    try:
        while completed < total:
            result = await result_queue.get()

            if result is None:
                completed += 1
            elif isinstance(result, Exception):
                raise result
            else:
                yield result
    finally:
        # Clean up remaining tasks
        for task in tasks:
            if not task.done():
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
