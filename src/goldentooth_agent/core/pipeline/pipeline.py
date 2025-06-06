from __future__ import annotations
from typing import List, Type
from inspect import iscoroutinefunction
from .middleware import Middleware, NextMiddleware

class Pipeline:
    """Pipeline for executing middleware in a context."""

    def __init__(self, context_type: Type) -> None:
      """Initialize the pipeline with a context type."""
      self._middleware: List[Middleware] = []
      self._context_type = context_type

    def use(self, fn: Middleware) -> Pipeline:
      """Add middleware to the pipeline."""
      if not iscoroutinefunction(fn):
        raise TypeError("Middleware must be async")
      self._middleware.append(fn)
      return self

    async def run(self, context):
      """Run the middleware pipeline with the given context."""

      async def call_next(index: int):
        """Call the next middleware in the pipeline."""
        if index >= len(self._middleware):
          return

        middleware: Middleware = self._middleware[index]
        next_fn: NextMiddleware = lambda: call_next(index + 1)
        await middleware(context, next_fn)

      await call_next(0)
