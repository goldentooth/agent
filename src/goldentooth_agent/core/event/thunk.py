from pyee.asyncio import AsyncIOEventEmitter
from typing import Any
from goldentooth_agent.core.thunk import Thunk

class ThunkEventEmitter(AsyncIOEventEmitter):
  """An event emitter that supports thunks for event handling."""

  def thunk_on(self, event: str, thunk: Thunk[Any, Any]):
    """Register a thunk as a handler for an event."""
    async def handler(*args, **kwargs):
      """Handler that executes the thunk with the provided arguments."""
      await thunk((args, kwargs))
    self.on(event, handler)

  def emit_thunk(self, event: str) -> Thunk[Any, None]:
    """Return a thunk that emits an event with the current context."""
    async def _emit(ctx):
      """Thunk to emit an event with the current context."""
      self.emit(event, ctx)
      return ctx
    return Thunk(_emit)
