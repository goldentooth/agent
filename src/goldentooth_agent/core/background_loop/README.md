# Background Loop

Background Loop module

## Overview

- **Complexity**: Medium
- **Files**: 3 Python files
- **Lines of Code**: ~174
- **Classes**: 1
- **Functions**: 10

## API Reference

### Classes

#### BackgroundEventLoop
A class to manage an asyncio event loop in a background thread.

**Public Methods:**
- `create()`
- `submit()`
- `shutdown()`
- `is_running()`

### Functions

#### `def async_flow(coroutine_fn: Callable[[T], Coroutine[AnyType, AnyType, R]], background_loop: BackgroundEventLoop) -> Flow[T, R]`
Create a Flow that runs async operations in the background loop.

    Args:
        coroutine_fn: A function that takes an item and returns a coroutine
        background_loop: The background event loop to use (injected)

    Returns:
        A Flow that transforms items asynchronously

    Example:
        # Define an async operation
        async def fetch_data(url: str) -> dict:
            await asyncio.sleep(0.1)  # Simulate async work
            return {"url": url, "data": "fetched"}

        # Create a flow that fetches data asynchronously
        urls = Flow.from_iterable(["url1", "url2", "url3"])
        results = urls >> async_flow(fetch_data)

#### `def schedule_flow(delay_seconds: float, background_loop: BackgroundEventLoop) -> Flow[T, T]`
Create a Flow that delays items using the background loop.

    Args:
        delay_seconds: Seconds to delay each item
        background_loop: The background event loop to use (injected)

    Returns:
        A Flow that delays items

    Example:
        # Delay each item by 1 second
        items = Flow.from_iterable([1, 2, 3])
        delayed = items >> schedule_flow(1.0)

#### `def timeout_async_flow(coroutine_fn: Callable[[T], Coroutine[AnyType, AnyType, R]], timeout_seconds: float, default_value: R | None) -> Flow[T, R]`
Create a Flow that runs async operations with a timeout.

    Args:
        coroutine_fn: A function that takes an item and returns a coroutine
        timeout_seconds: Timeout in seconds
        default_value: Value to return on timeout (None to skip)

    Returns:
        A Flow that transforms items with timeout

    Example:
        # Fetch data with 5 second timeout
        urls = Flow.from_iterable(["url1", "url2", "url3"])
        results = urls >> timeout_async_flow(fetch_data, 5.0, default_value={})

#### `def run_in_background(coroutine: AnyCoroutine[T], background_loop: BackgroundEventLoop) -> T`
Run a coroutine in the background event loop.

### Constants

#### `T`

#### `R`

#### `T`

## Dependencies

### External Dependencies
- `__future__`
- `antidote`
- `asyncio`
- `atexit`
- `collections`
- `concurrent`
- `flow_integration`
- `goldentooth_agent`
- `logging`
- `main`
- `threading`
- `typing`

## Exports

This module exports the following symbols:

- `BackgroundEventLoop`
- `async_flow`
- `run_in_background`
- `schedule_flow`
- `timeout_async_flow`

## Quality Metrics

- **Test Coverage**: Medium
- **Coverage Target**: 90%+
- **Performance**: All tests <200ms
