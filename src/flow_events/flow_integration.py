"""Flow integration functions for event-driven programming patterns."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any, AsyncGenerator, TypeVar

from flow import Flow

from .flow import AsyncEventFlow, EventFlow, SyncEventFlow

T = TypeVar("T")


# Type aliases for Flow integration
AnyFlow = Flow[None, Any]
AnyTransformer = Callable[[Any], Any]
AnyTransformFlow = Flow[None, Any]


def event_source(event_name: str, use_async: bool = True) -> AnyFlow:
    """Create a Flow that emits events from the specified event name.

    Args:
        event_name: Name of the event to listen for
        use_async: Whether to use async event emitter (default: True)

    Returns:
        Flow that yields events as they are emitted
    """
    if use_async:
        event_flow: EventFlow[Any] = AsyncEventFlow[Any](event_name)
    else:
        event_flow = SyncEventFlow[Any](event_name)

    return event_flow.as_flow()


def event_sink(event_name: str, use_async: bool = True) -> Flow[T, T]:
    """Create a Flow that emits each item it receives as an event.

    Args:
        event_name: Name of the event to emit
        use_async: Whether to use async event emitter (default: True)

    Returns:
        Flow that emits events and passes items through unchanged
    """
    if use_async:
        event_flow: EventFlow[T] = AsyncEventFlow[T](event_name)
    else:
        event_flow = SyncEventFlow[T](event_name)

    async def _sink_stream(stream: AsyncGenerator[T, None]) -> AsyncGenerator[T, None]:
        """Emit each item as an event and pass it through."""
        async for item in stream:
            event_flow.emit(item)
            yield item

    return Flow(_sink_stream, name=f"event_sink({event_name})")


def event_bridge(
    from_event: str, to_event: str, use_async: bool = True
) -> Flow[None, None]:
    """Create a Flow that bridges events from one event name to another.

    Args:
        from_event: Source event name to listen for
        to_event: Target event name to emit to
        use_async: Whether to use async event emitter (default: True)

    Returns:
        Flow that forwards events from source to target
    """
    if use_async:
        source_flow: EventFlow[Any] = AsyncEventFlow[Any](from_event)
        target_flow: EventFlow[Any] = AsyncEventFlow[Any](to_event)
    else:
        source_flow = SyncEventFlow[Any](from_event)
        target_flow = SyncEventFlow[Any](to_event)

    async def _bridge_stream(
        _: AsyncGenerator[None, None],
    ) -> AsyncGenerator[None, None]:
        """Bridge events from source to target."""
        source_events = source_flow.as_flow()

        async def empty_stream() -> AsyncGenerator[None, None]:
            """Create an empty stream for source consumption."""
            # Create an empty async generator by yielding from an empty list
            empty_list: list[None] = []
            for item in empty_list:
                yield item  # This will never execute but makes it a valid generator

        async for event_data in source_events(empty_stream()):
            target_flow.emit(event_data)
            yield None

    return Flow(_bridge_stream, name=f"event_bridge({from_event}->{to_event})")


def event_filter(
    event_name: str, predicate: Callable[[T], bool], use_async: bool = True
) -> Flow[None, T]:
    """Create a Flow that filters events based on a predicate.

    Args:
        event_name: Name of the event to listen for
        predicate: Function to filter events with
        use_async: Whether to use async event emitter (default: True)

    Returns:
        Flow that yields only events matching the predicate
    """
    if use_async:
        event_flow: EventFlow[T] = AsyncEventFlow[T](event_name)
    else:
        event_flow = SyncEventFlow[T](event_name)

    base_flow = event_flow.as_flow()

    async def _filter_stream(_: AsyncGenerator[None, None]) -> AsyncGenerator[T, None]:
        """Filter events based on predicate."""

        async def empty_stream() -> AsyncGenerator[None, None]:
            """Create an empty stream for source consumption."""
            # Create an empty async generator by yielding from an empty list
            empty_list: list[None] = []
            for item in empty_list:
                yield item  # This will never execute but makes it a valid generator

        async for event_data in base_flow(empty_stream()):
            if predicate(event_data):
                yield event_data

    return Flow(_filter_stream, name=f"event_filter({event_name})")


def event_transform(
    event_name: str, transformer: AnyTransformer, use_async: bool = True
) -> AnyTransformFlow:
    """Create a Flow that transforms events with a function.

    Args:
        event_name: Name of the event to listen for
        transformer: Function to transform events with
        use_async: Whether to use async event emitter (default: True)

    Returns:
        Flow that yields transformed events
    """
    if use_async:
        event_flow: EventFlow[Any] = AsyncEventFlow[Any](event_name)
    else:
        event_flow = SyncEventFlow[Any](event_name)

    base_flow = event_flow.as_flow()

    async def _transform_stream(
        _: AsyncGenerator[None, None],
    ) -> AsyncGenerator[Any, None]:
        """Transform events with the given function."""

        async def empty_stream() -> AsyncGenerator[None, None]:
            """Create an empty stream for source consumption."""
            # Create an empty async generator by yielding from an empty list
            empty_list: list[None] = []
            for item in empty_list:
                yield item  # This will never execute but makes it a valid generator

        async for event_data in base_flow(empty_stream()):
            yield transformer(event_data)

    return Flow(_transform_stream, name=f"event_transform({event_name})")
