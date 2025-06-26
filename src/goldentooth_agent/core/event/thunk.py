from antidote import inject, injectable
from goldentooth_agent.core.thunk import Thunk
from goldentooth_agent.core.logging import get_logger

from pyee.asyncio import AsyncIOEventEmitter
from typing import Any, Awaitable
from .inject import get_event_emitter


@injectable
class ThunkEventEmitter:
    """An event emitter that supports thunks for event handling."""

    @staticmethod
    @inject
    def on(
        event: str,
        thunk: Thunk[Any, None],
        ee: AsyncIOEventEmitter = inject[get_event_emitter()],
        logger=inject[get_logger(__name__)],
    ) -> None:
        """Register a thunk as a handler for an event."""

        async def handler(*args, **kwargs):
            """Handler that executes the thunk with the provided arguments."""
            logger.debug(
                f"Event '{event}' triggered with args: {args}, kwargs: {kwargs}"
            )
            await thunk((args, kwargs))

        ee.on(event, handler)

    @staticmethod
    @inject
    def emit(
        event: str,
        ee: AsyncIOEventEmitter = inject[get_event_emitter()],
        logger=inject[get_logger(__name__)],
    ) -> Thunk[Any, Awaitable[None]]:
        """Return a thunk that emits an event with the current context."""

        async def _emit(ctx):
            """Thunk to emit an event with the current context."""
            logger.debug(f"Emitting event '{event}' with context: {ctx}")
            ee.emit(event, ctx)
            return ctx

        return Thunk(_emit, name=f"emit_event({event})")


if __name__ == "__main__":
    from antidote import world
    import asyncio

    world[ThunkEventEmitter].on(
        "test_event",
        Thunk(lambda x: print(f"Event received with args: {x}"), name="test_handler"),
    )
    asyncio.run(world[ThunkEventEmitter].emit("test_event")(("arg1", "arg2")))
