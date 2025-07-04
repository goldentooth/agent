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
        stream: AsyncGenerator[Input, None]
    ) -> AsyncGenerator[Output, None]:
        """Race multiple flows for each item."""
        async for item in stream:
            # If no flows to race, skip this item
            if not flows:
                continue

            # Create tasks for each flow with the current item
            tasks: list[AnyTask] = []

            for flow in flows:
                single_stream = create_single_item_stream(item)

                async def run_flow(
                    f: Flow[Input, Output], s: AsyncGenerator[Input, None]
                ) -> Output:
                    """Run a flow and return first result."""
                    async for result in f(s):
                        return result
                    raise FlowExecutionError("Flow produced no results")

                task = asyncio.create_task(run_flow(flow, single_stream))
                tasks.append(task)

            pending: set[AnyTask] = set()
            try:
                # Wait for first completion
                done, pending = await asyncio.wait(
                    tasks, return_when=asyncio.FIRST_COMPLETED
                )

                # Get result from first completed task
                for task in done:
                    try:
                        result = await task
                        yield result
                        break
                    except Exception:
                        continue
                else:
                    # All tasks failed
                    raise FlowExecutionError("All racing flows failed")

            finally:
                # Cancel remaining tasks
                for task in pending:
                    task.cancel()
                    try:
                        await task
                    except asyncio.CancelledError:
                        pass

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
        stream: AsyncGenerator[Input, None]
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
        stream: AsyncGenerator[Input, None]
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
