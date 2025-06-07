from __future__ import annotations
from typing import Awaitable, Callable, Generic, TypeVar, TYPE_CHECKING
if TYPE_CHECKING:
  from .pipeline import Pipeline

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

  def as_pipeline(self) -> Pipeline[T]:
    """Convert a middleware to a pipeline."""
    from .pipeline import Pipeline  # Import here to avoid circular dependency
    pipeline = Pipeline[T]()
    pipeline.use(self)
    return pipeline

def middleware(fn: Callable[[T, NextMiddleware], Awaitable[None]]) -> Middleware[T]:
  """Decorator to mark a function as a middleware in the pipeline."""
  return Middleware(fn)


