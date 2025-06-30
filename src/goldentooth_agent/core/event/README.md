# Event

Event module

## Overview

- **Complexity**: Medium
- **Files**: 3 Python files
- **Lines of Code**: ~278
- **Classes**: 3
- **Functions**: 32

## API Reference

### Classes

#### EventFlow
Base class for Flow-integrated event handling.

**Public Methods:**
- `emit()`
- `as_flow()`

#### SyncEventFlow
Flow-integrated synchronous event emitter wrapper.

**Public Methods:**
- `emit()`
- `on()`
- `once()`
- `off()`
- `remove_all_listeners()`
- `listeners()`
- `listener_count()`
- `as_flow()`

#### AsyncEventFlow
Flow-integrated asynchronous event emitter wrapper.

**Public Methods:**
- `emit()`
- `on()`
- `once()`
- `off()`
- `remove_all_listeners()`
- `listeners()`
- `listener_count()`
- `as_flow()`

### Functions

#### `def event_source(event_name: str, use_async: bool) -> AnyFlow`
Create a Flow that emits events from the specified event name.

    Args:
        event_name: Name of the event to listen for
        use_async: Whether to use async event emitter (default: True)

    Returns:
        Flow that yields events as they are emitted

#### `def event_sink(event_name: str, use_async: bool) -> Flow[T, T]`
Create a Flow that emits each item it receives as an event.

    Args:
        event_name: Name of the event to emit
        use_async: Whether to use async event emitter (default: True)

    Returns:
        Flow that emits events and passes items through unchanged

#### `def event_bridge(from_event: str, to_event: str, use_async: bool) -> Flow[None, None]`
Create a Flow that bridges events from one event name to another.

    Args:
        from_event: Source event name to listen for
        to_event: Target event name to emit to
        use_async: Whether to use async event emitter (default: True)

    Returns:
        Flow that forwards events from source to target

#### `def event_filter(event_name: str, predicate: Callable[[T], bool], use_async: bool) -> Flow[None, T]`
Create a Flow that filters events based on a predicate.

    Args:
        event_name: Name of the event to listen for
        predicate: Function to filter events with
        use_async: Whether to use async event emitter (default: True)

    Returns:
        Flow that yields only events matching the predicate

#### `def event_transform(event_name: str, transformer: AnyTransformer, use_async: bool) -> AnyTransformFlow`
Create a Flow that transforms events with a function.

    Args:
        event_name: Name of the event to listen for
        transformer: Function to transform events with
        use_async: Whether to use async event emitter (default: True)

    Returns:
        Flow that yields transformed events

#### `def create_sync_event_flow(event_name: str) -> AnySyncEventFlow`
Create a synchronous event flow for the given event name.

#### `def create_async_event_flow(event_name: str) -> AnyAsyncEventFlow`
Create an asynchronous event flow for the given event name.

#### `def create_typed_sync_event_flow(event_name: str) -> Callable[[type[T]], SyncEventFlow[T]]`
Create a typed synchronous event flow factory.

#### `def create_typed_async_event_flow(event_name: str) -> Callable[[type[T]], AsyncEventFlow[T]]`
Create a typed asynchronous event flow factory.

#### `def get_sync_event_emitter() -> EventEmitter`
Get an event emitter instance for synchronous event handling.

#### `def get_async_event_emitter() -> AsyncIOEventEmitter`
Get an asyncio event emitter instance for asynchronous event handling.

### Constants

#### `T`

## Dependencies

### External Dependencies
- `__future__`
- `collections`
- `flow`
- `goldentooth_agent`
- `inject`
- `pyee`
- `typing`

## Exports

This module exports the following symbols:

- `AsyncEventFlow`
- `EventFlow`
- `SyncEventFlow`
- `create_async_event_flow`
- `create_sync_event_flow`
- `create_typed_async_event_flow`
- `create_typed_sync_event_flow`
- `event_bridge`
- `event_filter`
- `event_sink`
- `event_source`
- `event_transform`
- `get_async_event_emitter`
- `get_sync_event_emitter`

## Quality Metrics

- **Test Coverage**: Medium
- **Coverage Target**: 90%+
- **Performance**: All tests <200ms
