import inspect

async def maybe_await(func, *args, **kwargs):
  """Call a function and await its result if it's a coroutine."""
  result = func(*args, **kwargs)
  if inspect.iscoroutine(result):
    return await result
  return result
