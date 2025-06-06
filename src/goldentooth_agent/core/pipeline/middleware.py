from typing import Awaitable, Callable

type Middleware = Callable[..., Awaitable[None]]
type NextMiddleware = Callable[[], Awaitable[None]]

def middleware(fn: Middleware) -> Middleware:
  """Decorator to mark a function as a middleware in the pipeline."""
  return fn
