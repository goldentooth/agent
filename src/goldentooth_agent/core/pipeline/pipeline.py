from __future__ import annotations
from antidote import injectable
from typing import Generic, List, Optional, TypeVar
from inspect import iscoroutinefunction
from .middleware import Middleware, NextMiddleware
from ..thunk import Thunk

T = TypeVar('T')

class Pipeline(Generic[T]):
  """Pipeline for executing middleware in a context."""

  def __init__(self) -> None:
    """Initialize the pipeline with a context type."""
    self._middleware: List[Middleware[T]] = []

  def use(self, middleware: Middleware[T]) -> Pipeline[T]:
    """Add middleware to the pipeline."""
    if not iscoroutinefunction(middleware.fn):
      raise TypeError("Middleware must be async")
    self._middleware.append(middleware)
    return self

  async def run(self, context: T) -> None:
    """Run the middleware pipeline with the given context."""

    async def call_next(index: int):
      """Call the next middleware in the pipeline."""
      if index >= len(self._middleware):
        return

      middleware: Middleware[T] = self._middleware[index]
      next_fn: NextMiddleware = lambda: call_next(index + 1)
      await middleware(context, next_fn)

    await call_next(0)

  def as_thunk(self) -> Thunk[T, T]:
    """Convert the pipeline to a thunk that runs the middleware."""
    async def run(ctx: T) -> Optional[T]:
      await self.run(ctx)
      return ctx
    return Thunk(run)
