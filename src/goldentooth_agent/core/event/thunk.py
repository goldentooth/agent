from antidote import inject, injectable
from pyee.asyncio import AsyncIOEventEmitter
from typing import Any, Awaitable
from goldentooth_agent.core.thunk import Thunk
from .emitter import get_event_emitter

@injectable
class ThunkEventEmitter:
  """An event emitter that supports thunks for event handling."""

  @staticmethod
  @inject
  def on(
    event: str,
    thunk: Thunk[Any, None],
    ee: AsyncIOEventEmitter = inject[get_event_emitter()],
  ) -> None:
    """Register a thunk as a handler for an event."""
    async def handler(*args, **kwargs):
      """Handler that executes the thunk with the provided arguments."""
      await thunk((args, kwargs))
    ee.on(event, handler)

  @staticmethod
  @inject
  def emit(
    event: str,
    ee: AsyncIOEventEmitter = inject[get_event_emitter()],
  ) -> Thunk[Any, Awaitable[None]]:
    """Return a thunk that emits an event with the current context."""
    async def _emit(ctx):
      """Thunk to emit an event with the current context."""
      ee.emit(event, ctx)
      return ctx
    return Thunk(_emit)
