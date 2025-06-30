# Util

Util module

## Overview

- **Complexity**: Low
- **Files**: 2 Python files
- **Lines of Code**: ~29
- **Classes**: 0
- **Functions**: 1

## API Reference

### Functions

#### `async def maybe_await(func: Callable[..., T], *args: object, **kwargs: object) -> T`
Call a function and conditionally await its result if it returns a coroutine.

    This utility enables uniform handling of both synchronous and asynchronous functions
    in contexts where you don't know ahead of time whether the function is async.
    Useful for building flexible APIs that accept either sync or async callables.

    Args:
        func: The callable to execute (can be sync or async)
        *args: Positional arguments to pass to the function
        **kwargs: Keyword arguments to pass to the function

    Returns:
        The result of the function call, awaited if it was a coroutine

    Example:
        # Works with both sync and async functions
        result1 = await maybe_await(lambda x: x + 1, 5)  # Returns 6
        result2 = await maybe_await(async_function, arg1, kwarg=value)

### Constants

#### `T`

## Dependencies

### External Dependencies
- `collections`
- `inspect`
- `maybe_await`
- `typing`

## Exports

This module exports the following symbols:

- `maybe_await`

## Quality Metrics

- **Test Coverage**: Medium
- **Coverage Target**: 90%+
- **Performance**: All tests <200ms
