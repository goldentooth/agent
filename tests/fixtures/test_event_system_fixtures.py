"""Event system testing infrastructure for flow_events module.

This module provides comprehensive testing utilities for event-driven flows,
including mock event emitters, async generator testing utilities, and
flow execution frameworks.
"""

import asyncio
from typing import Any, AsyncGenerator, Callable, Optional, TypeVar, Union
from unittest.mock import Mock

from pyee import EventEmitter
from pyee.asyncio import AsyncIOEventEmitter

T = TypeVar("T")


class MockEventEmitter:
    """Mock event emitter for testing async flows with controlled behavior."""

    def __init__(self) -> None:
        """Initialize mock emitter with event tracking."""
        super().__init__()
        self.events: list[tuple[str, Any]] = []
        self.listeners: dict[str, list[Callable[[Any], None]]] = {}
        self.async_listeners: dict[str, list[Callable[[Any], Any]]] = {}
        self.emit_delay: float = 0.0
        self.emit_exception: Optional[Exception] = None

    def emit(self, event: str, *args: Any) -> bool:
        """Emit an event and call all registered listeners."""
        if self.emit_exception:
            raise self.emit_exception

        # Track the event
        data = args[0] if args else None
        self.events.append((event, data))

        # Call synchronous listeners
        if event in self.listeners:
            for listener in self.listeners[event]:
                try:
                    listener(data)
                except Exception:
                    pass  # Mock doesn't propagate listener errors

        return True

    async def emit_async(self, event: str, *args: Any) -> bool:
        """Emit an async event with optional delay."""
        if self.emit_delay > 0:
            await asyncio.sleep(self.emit_delay)

        if self.emit_exception:
            raise self.emit_exception

        # Track the event
        data = args[0] if args else None
        self.events.append((event, data))

        # Call async listeners
        if event in self.async_listeners:
            for listener in self.async_listeners[event]:
                try:
                    result = listener(data)
                    if asyncio.iscoroutine(result):
                        await result
                except Exception:
                    pass  # Mock doesn't propagate listener errors

        return True

    def on(self, event: str, listener: Callable[[Any], None]) -> None:
        """Register a synchronous event listener."""
        if event not in self.listeners:
            self.listeners[event] = []
        self.listeners[event].append(listener)

    def on_async(self, event: str, listener: Callable[[Any], Any]) -> None:
        """Register an asynchronous event listener."""
        if event not in self.async_listeners:
            self.async_listeners[event] = []
        self.async_listeners[event].append(listener)

    def off(self, event: str, listener: Optional[Callable[..., Any]] = None) -> None:
        """Remove event listener(s)."""
        if listener is None:
            # Remove all listeners for the event
            self.listeners.pop(event, None)
            self.async_listeners.pop(event, None)
        else:
            # Remove specific listener
            if event in self.listeners:
                try:
                    self.listeners[event].remove(listener)
                except ValueError:
                    pass
            if event in self.async_listeners:
                try:
                    self.async_listeners[event].remove(listener)
                except ValueError:
                    pass

    def clear_events(self) -> None:
        """Clear the event history."""
        self.events.clear()

    def get_events(self, event_name: Optional[str] = None) -> list[tuple[str, Any]]:
        """Get event history, optionally filtered by event name."""
        if event_name is None:
            return self.events.copy()
        return [(name, data) for name, data in self.events if name == event_name]

    def set_emit_delay(self, delay: float) -> None:
        """Set delay for async event emission."""
        self.emit_delay = delay

    def set_emit_exception(self, exception: Optional[Exception]) -> None:
        """Set exception to raise on emit."""
        self.emit_exception = exception


class MockEventListener:
    """Mock event listener with controllable async behavior."""

    def __init__(self, name: str = "test_listener") -> None:
        """Initialize mock listener."""
        super().__init__()
        self.name = name
        self.received_events: list[Any] = []
        self.processing_delay: float = 0.0
        self.processing_exception: Optional[Exception] = None
        self.call_count = 0

    def __call__(self, data: Any) -> None:
        """Synchronous event handler."""
        self.call_count += 1
        if self.processing_exception:
            raise self.processing_exception
        self.received_events.append(data)

    async def async_handler(self, data: Any) -> None:
        """Asynchronous event handler."""
        self.call_count += 1
        if self.processing_delay > 0:
            await asyncio.sleep(self.processing_delay)
        if self.processing_exception:
            raise self.processing_exception
        self.received_events.append(data)

    def clear_events(self) -> None:
        """Clear received events."""
        self.received_events.clear()
        self.call_count = 0

    def set_processing_delay(self, delay: float) -> None:
        """Set delay for event processing."""
        self.processing_delay = delay

    def set_processing_exception(self, exception: Optional[Exception]) -> None:
        """Set exception to raise during processing."""
        self.processing_exception = exception


class EventTestHarness:
    """Complete test harness for event-driven flows with isolated emitters."""

    def __init__(self, use_real_emitters: bool = False) -> None:
        """Initialize test harness.

        Args:
            use_real_emitters: If True, use real pyee emitters; if False, use mocks
        """
        super().__init__()
        if use_real_emitters:
            self.sync_emitter: Union[EventEmitter, MockEventEmitter] = EventEmitter()
            self.async_emitter: Union[AsyncIOEventEmitter, MockEventEmitter] = (
                AsyncIOEventEmitter()
            )
        else:
            self.sync_emitter = MockEventEmitter()
            self.async_emitter = MockEventEmitter()

        self.listeners: list[MockEventListener] = []
        self.cleanup_tasks: list[Callable[[], None]] = []

    def create_listener(self, name: str = "test_listener") -> MockEventListener:
        """Create and register a mock event listener."""
        listener = MockEventListener(name)
        self.listeners.append(listener)
        return listener

    def emit_sync_event(self, event_name: str, data: Any) -> None:
        """Emit a synchronous event."""
        if isinstance(self.sync_emitter, MockEventEmitter):
            self.sync_emitter.emit(event_name, data)
        else:
            self.sync_emitter.emit(event_name, data)

    async def emit_async_event(self, event_name: str, data: Any) -> None:
        """Emit an asynchronous event."""
        if isinstance(self.async_emitter, MockEventEmitter):
            await self.async_emitter.emit_async(event_name, data)
        else:
            self.async_emitter.emit(event_name, data)
            # Give async handlers time to process
            await asyncio.sleep(0.01)

    def register_sync_listener(
        self, event_name: str, listener: MockEventListener
    ) -> None:
        """Register a synchronous event listener."""
        if isinstance(self.sync_emitter, MockEventEmitter):
            self.sync_emitter.on(event_name, listener)
        else:
            self.sync_emitter.on(event_name, listener)

    def register_async_listener(
        self, event_name: str, listener: MockEventListener
    ) -> None:
        """Register an asynchronous event listener."""
        if isinstance(self.async_emitter, MockEventEmitter):
            self.async_emitter.on_async(event_name, listener.async_handler)
        else:
            self.async_emitter.on(event_name, listener.async_handler)

    async def emit_event_sequence(
        self,
        event_name: str,
        data_sequence: list[Any],
        delay_between: float = 0.01,
        use_async: bool = True,
    ) -> None:
        """Emit a sequence of events with delays."""
        for data in data_sequence:
            if use_async:
                await self.emit_async_event(event_name, data)
            else:
                self.emit_sync_event(event_name, data)

            if delay_between > 0:
                await asyncio.sleep(delay_between)

    def get_all_received_events(self) -> dict[str, list[Any]]:
        """Get all events received by all listeners."""
        return {
            listener.name: listener.received_events.copy()
            for listener in self.listeners
        }

    def get_emitted_events(
        self, event_name: Optional[str] = None, from_async: bool = True
    ) -> list[tuple[str, Any]]:
        """Get events emitted by the harness."""
        emitter = self.async_emitter if from_async else self.sync_emitter
        if isinstance(emitter, MockEventEmitter):
            return emitter.get_events(event_name)
        else:
            # Real emitters don't track events
            return []

    def clear_all_events(self) -> None:
        """Clear all event histories."""
        for listener in self.listeners:
            listener.clear_events()

        if isinstance(self.sync_emitter, MockEventEmitter):
            self.sync_emitter.clear_events()
        if isinstance(self.async_emitter, MockEventEmitter):
            self.async_emitter.clear_events()

    async def wait_for_events(
        self, listener: MockEventListener, expected_count: int, timeout: float = 1.0
    ) -> bool:
        """Wait for a listener to receive a specific number of events."""
        start_time = asyncio.get_event_loop().time()

        while len(listener.received_events) < expected_count:
            if asyncio.get_event_loop().time() - start_time > timeout:
                return False
            await asyncio.sleep(0.01)

        return True

    def cleanup(self) -> None:
        """Clean up test harness resources."""
        # Remove all listeners
        for listener in self.listeners:
            listener.clear_events()

        # Run cleanup tasks
        for cleanup_func in self.cleanup_tasks:
            try:
                cleanup_func()
            except Exception:
                pass  # Ignore cleanup errors

        self.cleanup_tasks.clear()
        self.listeners.clear()

    def add_cleanup_task(self, cleanup_func: Callable[[], None]) -> None:
        """Add a cleanup task to run when harness is cleaned up."""
        self.cleanup_tasks.append(cleanup_func)
