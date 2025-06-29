"""Flow-integrated event system with pyee event emitter wrappers."""

from __future__ import annotations

from collections.abc import AsyncIterator, Awaitable, Callable
from typing import Any, Generic, TypeVar

from pyee import EventEmitter
from pyee.asyncio import AsyncIOEventEmitter

from goldentooth_agent.flow_engine import Flow

from .inject import get_async_event_emitter, get_sync_event_emitter

T = TypeVar("T")
EventType = TypeVar("EventType")


class EventFlow(Generic[T]):
    """Base class for Flow-integrated event handling."""

    def __init__(self, event_name: str) -> None:
        """Initialize with an event name to listen for."""
        self.event_name = event_name

    def emit(self, data: T) -> None:
        """Emit an event with the given data. To be implemented by subclasses."""
        raise NotImplementedError("Subclasses must implement emit method")

    def as_flow(self) -> Flow[None, T]:
        """Convert this event emitter to a Flow. To be implemented by subclasses."""
        raise NotImplementedError("Subclasses must implement as_flow method")


class SyncEventFlow(EventFlow[T]):
    """Flow-integrated synchronous event emitter wrapper."""

    def __init__(self, event_name: str, emitter: EventEmitter | None = None) -> None:
        """Initialize with an event name and optional custom emitter."""
        super().__init__(event_name)
        self.emitter = emitter if emitter is not None else get_sync_event_emitter()

    def emit(self, data: T) -> None:
        """Emit a synchronous event with the given data."""
        self.emitter.emit(self.event_name, data)

    def on(self, handler: Callable[[T], None]) -> None:
        """Register a synchronous event handler."""
        self.emitter.on(self.event_name, handler)

    def once(self, handler: Callable[[T], None]) -> None:
        """Register a one-time synchronous event handler."""
        self.emitter.once(self.event_name, handler)

    def off(self, handler: Callable[[T], None]) -> None:
        """Remove a synchronous event handler."""
        self.emitter.remove_listener(self.event_name, handler)

    def remove_all_listeners(self) -> None:
        """Remove all listeners for this event."""
        self.emitter.remove_all_listeners(self.event_name)

    def listeners(self) -> list[Callable[[T], None]]:
        """Get all listeners for this event."""
        return self.emitter.listeners(self.event_name)

    def listener_count(self) -> int:
        """Get the number of listeners for this event."""
        return len(self.listeners())

    def as_flow(self) -> Flow[None, T]:
        """Convert this synchronous event emitter to a Flow."""

        def register_callback(callback: Callable[[T], None]) -> None:
            """Register the callback with the synchronous emitter."""
            self.emitter.on(self.event_name, callback)

        return Flow.from_emitter(register_callback)


class AsyncEventFlow(EventFlow[T]):
    """Flow-integrated asynchronous event emitter wrapper."""

    def __init__(
        self, event_name: str, emitter: AsyncIOEventEmitter | None = None
    ) -> None:
        """Initialize with an event name and optional custom emitter."""
        super().__init__(event_name)
        self.emitter = emitter if emitter is not None else get_async_event_emitter()

    def emit(self, data: T) -> None:
        """Emit an asynchronous event with the given data."""
        self.emitter.emit(self.event_name, data)

    async def on(self, handler: AnyEventHandler | AnyAwaitableEventHandler) -> None:
        """Register an asynchronous event handler."""
        self.emitter.on(self.event_name, handler)

    async def once(self, handler: AnyEventHandler | AnyAwaitableEventHandler) -> None:
        """Register a one-time asynchronous event handler."""
        self.emitter.once(self.event_name, handler)

    async def off(self, handler: AnyEventHandler | AnyAwaitableEventHandler) -> None:
        """Remove an asynchronous event handler."""
        self.emitter.remove_listener(self.event_name, handler)

    async def remove_all_listeners(self) -> None:
        """Remove all listeners for this event."""
        self.emitter.remove_all_listeners(self.event_name)

    def listeners(self) -> list[AnyEventHandler]:
        """Get all listeners for this event."""
        return self.emitter.listeners(self.event_name)

    def listener_count(self) -> int:
        """Get the number of listeners for this event."""
        return len(self.listeners())

    def as_flow(self) -> Flow[None, T]:
        """Convert this asynchronous event emitter to a Flow."""

        def register_callback(callback: Callable[[T], None]) -> None:
            """Register the callback with the asynchronous emitter."""
            self.emitter.on(self.event_name, callback)

        return Flow.from_emitter(register_callback)


# Type aliases for event handling (after class definitions)
AnyEventHandler = Callable[[Any], Any]
AnyAwaitableEventHandler = Callable[[Any], Awaitable[Any]]
AnyEventFlow = EventFlow[Any]
AnyAsyncEventFlow = AsyncEventFlow[Any]
AnySyncEventFlow = SyncEventFlow[Any]
AnyFlow = Flow[None, Any]
AnyTransformer = Callable[[Any], Any]
AnyTransformFlow = Flow[None, Any]


# Flow derivative functions for common event patterns


def event_source(event_name: str, use_async: bool = True) -> AnyFlow:
    """Create a Flow that emits events from the specified event name.

    Args:
        event_name: Name of the event to listen for
        use_async: Whether to use async event emitter (default: True)

    Returns:
        Flow that yields events as they are emitted
    """
    if use_async:
        event_flow: AnyEventFlow = AsyncEventFlow[Any](event_name)
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

    async def _sink_stream(stream: AsyncIterator[T]) -> AsyncIterator[T]:
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
        source_flow: AnyEventFlow = AsyncEventFlow[Any](from_event)
        target_flow: AnyEventFlow = AsyncEventFlow[Any](to_event)
    else:
        source_flow = SyncEventFlow[Any](from_event)
        target_flow = SyncEventFlow[Any](to_event)

    async def _bridge_stream(_: AsyncIterator[None]) -> AsyncIterator[None]:
        """Bridge events from source to target."""
        source_events = source_flow.as_flow()

        # Start with an empty stream since we don't consume input
        async def empty_stream() -> AsyncIterator[None]:
            return
            yield  # unreachable

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

    # Get the base event flow and apply filter
    base_flow = event_flow.as_flow()

    async def _filter_stream(_: AsyncIterator[None]) -> AsyncIterator[T]:
        """Filter events based on predicate."""

        # Start with an empty stream since we don't consume input
        async def empty_stream() -> AsyncIterator[None]:
            return
            yield  # unreachable

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
        event_flow: AnyEventFlow = AsyncEventFlow[Any](event_name)
    else:
        event_flow = SyncEventFlow[Any](event_name)

    # Get the base event flow and apply transformation
    base_flow = event_flow.as_flow()

    async def _transform_stream(_: AsyncIterator[None]) -> AsyncIterator[Any]:
        """Transform events with the given function."""

        # Start with an empty stream since we don't consume input
        async def empty_stream() -> AsyncIterator[None]:
            return
            yield  # unreachable

        async for event_data in base_flow(empty_stream()):
            yield transformer(event_data)

    return Flow(_transform_stream, name=f"event_transform({event_name})")


# Convenience factory functions


def create_sync_event_flow(event_name: str) -> AnySyncEventFlow:
    """Create a synchronous event flow for the given event name."""
    return SyncEventFlow[Any](event_name)


def create_async_event_flow(event_name: str) -> AnyAsyncEventFlow:
    """Create an asynchronous event flow for the given event name."""
    return AsyncEventFlow[Any](event_name)


def create_typed_sync_event_flow(
    event_name: str,
) -> Callable[[type[T]], SyncEventFlow[T]]:
    """Create a typed synchronous event flow factory."""

    def factory(event_type: type[T]) -> SyncEventFlow[T]:
        return SyncEventFlow[T](event_name)

    return factory


def create_typed_async_event_flow(
    event_name: str,
) -> Callable[[type[T]], AsyncEventFlow[T]]:
    """Create a typed asynchronous event flow factory."""

    def factory(event_type: type[T]) -> AsyncEventFlow[T]:
        return AsyncEventFlow[T](event_name)

    return factory
