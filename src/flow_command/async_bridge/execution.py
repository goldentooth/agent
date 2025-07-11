from __future__ import annotations

import asyncio
import logging
from collections.abc import AsyncGenerator, AsyncIterable, Iterable
from typing import TypeVar

from flow.flow import Flow

from ..core.context import FlowCommandContext
from ..core.result import FlowCommandResult
from .loop_manager import FlowEventLoop

logger = logging.getLogger(__name__)

# Track cleanup events for debugging - only log in development/debug mode
_cleanup_events_count = 0

T = TypeVar("T")
U = TypeVar("U")

_flow_loop: FlowEventLoop | None = None


def _get_flow_loop() -> FlowEventLoop:
    """Get or create the global flow event loop."""
    global _flow_loop
    if _flow_loop is None:
        _flow_loop = FlowEventLoop()
    return _flow_loop


def get_cleanup_events_count() -> int:
    """Get the count of coroutine cleanup events for debugging."""
    return _cleanup_events_count


def reset_cleanup_events_count() -> None:
    """Reset the cleanup events counter (useful for testing)."""
    global _cleanup_events_count
    _cleanup_events_count = 0


def run_flow_sync(
    flow: Flow[T, U], input_data: Iterable[T], context: FlowCommandContext
) -> FlowCommandResult[list[U]]:
    """Execute flow synchronously in any context."""
    loop = _get_flow_loop()

    async def execute() -> list[U]:
        async_input = _convert_to_async_iterable(input_data)
        async_gen = _convert_to_async_generator(async_input)
        return await flow.collect()(async_gen)

    # Create coroutine and execute with proper error handling
    coro = execute()
    try:
        result = loop.execute_with_timeout(coro, context.execution_timeout)
        return FlowCommandResult[list[U]].success_result(result)
    except Exception as e:
        # Let the loop manager handle coroutine cleanup
        # Only track cleanup events for debugging without interfering
        if hasattr(coro, "cr_frame") and getattr(coro, "cr_frame", None) is not None:
            global _cleanup_events_count
            _cleanup_events_count += 1
        return FlowCommandResult[list[U]].error_result(str(e))


async def run_flow_async(
    flow: Flow[T, U], input_data: AsyncIterable[T], context: FlowCommandContext
) -> FlowCommandResult[list[U]]:
    """Execute flow asynchronously when in async context."""
    try:
        async_gen = _convert_to_async_generator(input_data)
        result = await asyncio.wait_for(
            flow.collect()(async_gen), timeout=context.execution_timeout
        )
        return FlowCommandResult[list[U]].success_result(result)
    except Exception as e:
        return FlowCommandResult[list[U]].error_result(str(e))


async def _convert_to_async_iterable(data: Iterable[T]) -> AsyncIterable[T]:
    """Convert iterable to async iterable."""
    for item in data:
        yield item


async def _convert_to_async_generator(
    async_iterable: AsyncIterable[T],
) -> AsyncGenerator[T, None]:
    """Convert AsyncIterable to AsyncGenerator for Flow compatibility."""
    async for item in async_iterable:
        yield item
