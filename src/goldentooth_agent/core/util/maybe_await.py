import inspect
from typing import Callable, Any, Awaitable

async def maybe_await(func: Callable, *args, **kwargs):
  """Call a function and await its result if it's a coroutine."""
  if not callable(func):
    raise ValueError(f"Expected a callable, got {type(func).__name__}")
  result = func(*args, **kwargs)
  if inspect.iscoroutine(result):
    return await result
  return result
