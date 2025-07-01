"""Observability combinators for debugging and monitoring flows.

This module provides combinators for logging, tracing, metrics collection,
and inspection of stream processing flows.
"""

from __future__ import annotations

import asyncio
import logging
from collections.abc import AsyncIterator, Callable
from typing import Any, TypeVar

from ..core.flow import Flow

Input = TypeVar("Input")

# Type alias
AnyValue = Any


class StreamNotification:
    """Represents a stream notification (item, error, or completion)."""

    pass


class OnNext(StreamNotification):
    def __init__(self, value: AnyValue) -> None:
        self.value = value

    def __repr__(self) -> str:
        return f"OnNext({self.value})"


class OnError(StreamNotification):
    def __init__(self, error: Exception) -> None:
        self.error = error

    def __repr__(self) -> str:
        return f"OnError({self.error})"


class OnComplete(StreamNotification):
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


def trace_stream(tracer: Callable[[str, AnyValue], None]) -> Flow[Input, Input]:
    """Create a flow that provides detailed tracing of stream processing.

    Calls the tracer function for each item with event type and item data.
    Useful for debugging and monitoring stream behavior.

    Args:
        tracer: Function that receives (event_type, item) for tracing

    Returns:
        A flow that traces processing and passes items through
    """

    async def _flow(stream: AsyncIterator[Input]) -> AsyncIterator[Input]:
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

    return Flow(_flow, name=f"trace({getattr(tracer, '__name__', 'function')})")


def metrics_stream(counter: Callable[[str], None]) -> Flow[Input, Input]:
    """Create a flow that emits metrics for stream processing.

    Calls the counter function with metric names as items are processed.
    Useful for monitoring and observability.

    Args:
        counter: Function that receives metric names

    Returns:
        A flow that emits metrics and passes items through
    """

    async def _flow(stream: AsyncIterator[Input]) -> AsyncIterator[Input]:
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

    return Flow(_flow, name=f"metrics({getattr(counter, '__name__', 'function')})")


def inspect_stream(
    inspector: Callable[[Input, dict[str, AnyValue]], None]
) -> Flow[Input, Input]:
    """Create a flow that inspects stream items with context metadata.

    Calls the inspector function with each item and a context dictionary
    containing processing metadata. Useful for debugging and analysis.

    Args:
        inspector: Function that receives (item, context_dict)

    Returns:
        A flow that inspects items and passes them through
    """

    async def _flow(stream: AsyncIterator[Input]) -> AsyncIterator[Input]:
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

    return Flow(_flow, name=f"inspect({getattr(inspector, '__name__', 'function')})")


def materialize_stream() -> Flow[Input, StreamNotification]:
    """Create a flow that converts items and errors into notification objects.

    Converts the stream into a meta-stream where each emission is a notification
    about what happened (OnNext, OnError, OnComplete). Allows treating errors
    as values for complex error handling patterns.

    Returns:
        A flow that yields StreamNotification objects
    """

    async def _flow(stream: AsyncIterator[Input]) -> AsyncIterator[StreamNotification]:
        """Convert stream items and events to notifications."""
        try:
            async for item in stream:
                yield OnNext(item)
        except Exception as e:
            yield OnError(e)
        finally:
            yield OnComplete()

    return Flow(_flow, name="materialize")
