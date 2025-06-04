from typing import Awaitable, Callable

type Middleware = Callable[..., Awaitable[None]]
type NextMiddleware = Callable[[], Awaitable[None]]

def middleware(fn: Middleware) -> Middleware:
  return fn
