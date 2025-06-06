from __future__ import annotations
from typing import Awaitable, Callable, Generic, TypeVar

T = TypeVar('T')

NextMiddleware = Callable[[], Awaitable[None]]

class Middleware(Generic[T]):
  """Protocol for a middleware function in the pipeline."""

  def __init__(self, fn: Callable[[T, NextMiddleware], Awaitable[None]]) -> None:
    """Call the middleware with the context and the next middleware function."""
    self.fn = fn

  async def __call__(self, ctx: T, next: NextMiddleware) -> None:
    """Call the middleware with the given context and next function."""
    return await self.fn(ctx, next)

def middleware(fn: Callable[[T, NextMiddleware], Awaitable[None]]) -> Middleware[T]:
  """Decorator to mark a function as a middleware in the pipeline."""
  return Middleware(fn)
