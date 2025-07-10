"""Observability combinators for debugging and monitoring flows.

This module provides combinators for logging, tracing, metrics collection,
and inspection of stream processing flows.
"""

from __future__ import annotations

import asyncio
import logging
from abc import ABC
from collections.abc import AsyncGenerator, Callable
from typing import Any, TypeVar

from flow.flow import Flow

from .utils import get_function_name

Input = TypeVar("Input")


class StreamNotification(ABC):
    """Represents a stream notification (item, error, or completion)."""

    def __repr__(self) -> str:
        """Return string representation of the notification."""
        return f"{self.__class__.__name__}()"


class OnNext(StreamNotification):
    """Notification for a stream item."""

    def __init__(self, value: Any) -> None:
        super().__init__()
        self.value = value

    def __repr__(self) -> str:
        return f"OnNext({self.value})"


class OnError(StreamNotification):
    """Notification for a stream error."""

    def __init__(self, error: Exception) -> None:
        super().__init__()
        self.error = error

    def __repr__(self) -> str:
        return f"OnError({self.error})"


class OnComplete(StreamNotification):
    """Notification for stream completion."""

    def __repr__(self) -> str:
        return "OnComplete()"


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

    async def _flow(stream: AsyncGenerator[Input, None]) -> AsyncGenerator[Input, None]:
        """Log each stream item and pass it through unchanged."""
        logger = logging.getLogger(__name__)
        async for item in stream:
            if logger.isEnabledFor(level):
                logger.log(level, f"{prefix}{item}")
            yield item

    return Flow(
        _flow,
        name=f"log_stream({name})",
        metadata={
            "prefix": prefix,
            "level": level,
        },
    )


def trace_stream(tracer: Callable[[str, Any], None]) -> Flow[Input, Input]:
    """Create a flow that provides detailed tracing of stream processing.

    Calls the tracer function for each item with event type and item data.
    Useful for debugging and monitoring stream behavior.

    Args:
        tracer: Function that receives (event_type, item) for tracing

    Returns:
        A flow that traces processing and passes items through
    """

    async def _flow(stream: AsyncGenerator[Input, None]) -> AsyncGenerator[Input, None]:
        """Trace stream processing."""
        tracer("stream_start", None)
        try:
            async for item in stream:
                tracer("item", item)
                yield item
        except Exception as e:
            tracer("error", e)
            raise
        finally:
            tracer("stream_end", None)

    return Flow(_flow, name=f"trace({get_function_name(tracer)})")


def metrics_stream(counter: Callable[[str], None]) -> Flow[Input, Input]:
    """Create a flow that emits metrics for stream processing.

    Calls the counter function with metric names as items are processed.
    Useful for monitoring and observability.

    Args:
        counter: Function that receives metric names

    Returns:
        A flow that emits metrics and passes items through
    """

    async def _flow(stream: AsyncGenerator[Input, None]) -> AsyncGenerator[Input, None]:
        """Emit metrics for stream processing."""
        counter("stream.started")
        item_count = 0

        try:
            async for item in stream:
                counter("stream.item")
                item_count += 1
                yield item
        except Exception:
            counter("stream.error")
            raise
        finally:
            counter("stream.completed")
            counter(f"stream.total_items.{item_count}")

    return Flow(_flow, name=f"metrics({get_function_name(counter)})")


def inspect_stream(
    inspector: Callable[[Input, dict[str, Any]], None],
) -> Flow[Input, Input]:
    """Create a flow that inspects stream items with context metadata.

    Calls the inspector function with each item and a context dictionary
    containing processing metadata. Useful for debugging and analysis.

    Args:
        inspector: Function that receives (item, context_dict)

    Returns:
        A flow that inspects items and passes them through
    """

    async def _flow(stream: AsyncGenerator[Input, None]) -> AsyncGenerator[Input, None]:
        """Inspect stream items with context."""
        item_count = 0
        start_time = asyncio.get_event_loop().time()

        async for item in stream:
            context = {
                "item_index": item_count,
                "elapsed_time": asyncio.get_event_loop().time() - start_time,
                "stream_position": item_count + 1,
            }
            inspector(item, context)
            yield item
            item_count += 1

    return Flow(_flow, name=f"inspect({get_function_name(inspector)})")


def materialize_stream() -> Flow[Any, StreamNotification]:
    """Create a flow that converts items and errors into notification objects.

    Converts the stream into a meta-stream where each emission is a notification
    about what happened (OnNext, OnError, OnComplete). Allows treating errors
    as values for complex error handling patterns.

    Returns:
        A flow that yields StreamNotification objects
    """

    async def _flow(
        stream: AsyncGenerator[Any, None],
    ) -> AsyncGenerator[StreamNotification, None]:
        """Convert stream items and events to notifications."""
        try:
            async for item in stream:
                yield OnNext(item)
            # Only emit OnComplete if no exception occurred
            yield OnComplete()
        except Exception as e:
            yield OnError(e)
            # Do not emit OnComplete after an error

    return Flow(_flow, name="materialize")
