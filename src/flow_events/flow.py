"""Flow-integrated event system with pyee event emitter wrappers."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import Any, Generic, TypeVar

from pyee import EventEmitter
from pyee.asyncio import AsyncIOEventEmitter

from flow import Flow

from .inject import get_async_event_emitter, get_sync_event_emitter

T = TypeVar("T")
EventType = TypeVar("EventType")


class EventFlow(Generic[T]):
    """Base class for Flow-integrated event handling."""

    def __init__(self, event_name: str) -> None:
        """Initialize with an event name to listen for."""
        super().__init__()
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
        self.emitter.once(  # pyright: ignore[reportUnknownMemberType]
            self.event_name, handler
        )
        return None

    def off(self, handler: Callable[[T], None]) -> None:
        """Remove a synchronous event handler."""
        self.emitter.remove_listener(  # pyright: ignore[reportUnknownMemberType]
            self.event_name, handler
        )
        return None

    def remove_all_listeners(self) -> None:
        """Remove all listeners for this event."""
        self.emitter.remove_all_listeners(self.event_name)

    def listeners(self) -> list[Callable[[T], None]]:
        """Get all listeners for this event."""
        return list(
            self.emitter.listeners(  # pyright: ignore[reportUnknownMemberType,reportUnknownArgumentType]
                self.event_name
            )
        )

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

    async def on(
        self, handler: Callable[[T], Any] | Callable[[T], Awaitable[Any]]
    ) -> None:
        """Register an asynchronous event handler."""
        self.emitter.on(self.event_name, handler)

    async def once(
        self, handler: Callable[[T], Any] | Callable[[T], Awaitable[Any]]
    ) -> None:
        """Register a one-time asynchronous event handler."""
        self.emitter.once(  # pyright: ignore[reportUnknownMemberType]
            self.event_name, handler
        )
        return None

    async def off(
        self, handler: Callable[[T], Any] | Callable[[T], Awaitable[Any]]
    ) -> None:
        """Remove an asynchronous event handler."""
        self.emitter.remove_listener(  # pyright: ignore[reportUnknownMemberType]
            self.event_name, handler
        )
        return None

    async def remove_all_listeners(self) -> None:
        """Remove all listeners for this event."""
        self.emitter.remove_all_listeners(self.event_name)

    def listeners(self) -> list[Callable[[T], Any]]:
        """Get all listeners for this event."""
        return list(
            self.emitter.listeners(  # pyright: ignore[reportUnknownMemberType,reportUnknownArgumentType]
                self.event_name
            )
        )

    def listener_count(self) -> int:
        """Get the number of listeners for this event."""
        return len(self.listeners())

    def as_flow(self) -> Flow[None, T]:
        """Convert this asynchronous event emitter to a Flow."""

        def register_callback(callback: Callable[[T], None]) -> None:
            """Register the callback with the asynchronous emitter."""
            self.emitter.on(self.event_name, callback)

        return Flow.from_emitter(register_callback)


# Type aliases for event handling
AnyEventHandler = Callable[[Any], Any]
AnyAwaitableEventHandler = Callable[[Any], Awaitable[Any]]

# Type aliases for convenience
AnyEventFlow = EventFlow[Any]
AnySyncEventFlow = SyncEventFlow[Any]
AnyAsyncEventFlow = AsyncEventFlow[Any]
