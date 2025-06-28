import inspect
from collections.abc import Callable
from typing import TypeVar

T = TypeVar("T")


async def maybe_await(func: Callable[..., T], *args: object, **kwargs: object) -> T:  # type: ignore[explicit-any]
    """Call a function and conditionally await its result if it returns a coroutine.

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
    """
    if not callable(func):
        raise ValueError(f"Expected a callable, got {type(func).__name__}")
    result = func(*args, **kwargs)
    if inspect.iscoroutine(result):
        return await result  # type: ignore[no-any-return]
    return result
