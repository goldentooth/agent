from __future__ import annotations
from asyncio import Queue
from pyee.asyncio import AsyncIOEventEmitter
from typing import (
    Any,
    AsyncIterator,
    Awaitable,
    Callable,
    Generic,
    TypeVar,
    TYPE_CHECKING,
)

TIn = TypeVar("TIn")
TOut = TypeVar("TOut")
TNew = TypeVar("TNew")


class EventThunk(Generic[TIn, TOut]):
    """A thunk that emits a stream of values from a context."""

    def __init__(
        self,
        fn: Callable[[TIn], AsyncIterator[TOut]],
        name: str,
        metadata: dict[str, Any] = {},
    ) -> None:
        """Initialize the event thunk with a function."""
        if not callable(fn):
            raise TypeError("EventThunk requires a callable")
        self.fn = fn
        self.name = name or fn.__name__ or "<anonymous>"
        self.metadata: dict[str, Any] = metadata
        self.__name__ = self.name

    def __call__(self, ctx: TIn) -> AsyncIterator[TOut]:
        """Call the thunk with the given context and return an async iterator."""
        return self.fn(ctx)

    @classmethod
    def from_callable(
        cls, fn: Callable[[TIn], AsyncIterator[TOut]], name: str
    ) -> EventThunk[TIn, TOut]:
        """Create a thunk from a callable."""
        return cls(fn, name=name)

    def map(self, fn: Callable[[TOut], TNew]) -> EventThunk[TIn, TNew]:
        """Map a function over the result of the thunk."""

        async def _mapped(ctx: TIn) -> AsyncIterator[TNew]:
            """Call the thunk and apply the function to its result."""
            async for value in self(ctx):
                yield fn(value)

        return EventThunk(_mapped, name=f"{self.name}.map({fn.__name__})")

    def filter(self, predicate: Callable[[TOut], bool]) -> EventThunk[TIn, TOut]:
        """Filter the result of the thunk based on a predicate."""

        async def _filtered(ctx: TIn) -> AsyncIterator[TOut]:
            """Call the thunk and yield only items that match the predicate."""
            async for item in self(ctx):
                if predicate(item):
                    yield item

        return EventThunk(_filtered, name=f"{self.name}.filter({predicate.__name__})")

    def flat_map(
        self, fn: Callable[[TOut], EventThunk[TIn, TNew]]
    ) -> EventThunk[TIn, TNew]:
        """Flat-map a function over the result of the thunk."""

        async def _bound(ctx: TIn) -> AsyncIterator[TNew]:
            """Call the thunk, get the result, and apply the function to each item."""
            async for item in self(ctx):
                async for subitem in fn(item)(ctx):
                    yield subitem

        return EventThunk(_bound, name=f"{self.name}.flat_map({fn.__name__})")

    def flatten(self: EventThunk[TIn, EventThunk[TIn, TNew]]) -> EventThunk[TIn, TNew]:
        """Collapse a thunk-of-thunks into a single thunk."""

        async def _flattened(ctx: TIn) -> AsyncIterator[TNew]:
            """Call this thunk, which returns another thunk, and execute it."""
            async for item in self(ctx):
                async for subitem in item(ctx):
                    yield subitem

        return EventThunk(_flattened, name=f"{self.name}.flatten")

    def tap(self, fn: Callable[[TOut], Awaitable[None]]) -> EventThunk[TIn, TOut]:
        """Tap into the stream to perform a side effect on each item."""

        async def _tapped(ctx: TIn) -> AsyncIterator[TOut]:
            """Call the thunk, apply the side effect, and yield each item."""
            async for item in self(ctx):
                await fn(item)
                yield item

        return EventThunk(_tapped, name=f"{self.name}.tap({fn.__name__})")

    def __rshift__(self, other: EventThunk[TOut, TNew]) -> EventThunk[TIn, TNew]:
        """Compose this thunk with another, where the output of this is the input to the other."""

        async def _thunk(ctx: TIn) -> AsyncIterator[TNew]:
            """Call self, then pass its result to the second thunk."""
            async for result in self(ctx):
                async for item in other(result):
                    yield item

        return EventThunk(_thunk, name=f"{self.name} >> {other.name}")

    if TYPE_CHECKING:
        from ..thunk.main import Thunk

    def collect(self) -> "Thunk[TIn, list[TOut]]":
        """Collect all emitted values into a list."""
        from ..thunk.main import Thunk

        async def _fn(ctx: TIn) -> list[TOut]:
            """Collect all items emitted by the thunk into a list."""
            return [item async for item in self(ctx)]

        return Thunk(_fn, name=f"{self.name}.collect")

    @staticmethod
    def from_emitter(emitter: AsyncIOEventEmitter, event: str) -> EventThunk[None, Any]:
        """Turn a pyee event into an EventThunk."""
        from asyncio import Queue
        from typing import AsyncGenerator

        async def _generator(_: None) -> AsyncGenerator[Any, None]:
            """Generator that yields values from the event emitter."""
            queue: Queue = Queue()

            async def enqueue(value):
                """Enqueue values emitted by the event."""
                await queue.put(value)

            emitter.on(event, enqueue)
            while True:
                value = await queue.get()
                yield value

        return EventThunk(
            _generator,
            name=f"EventThunk.from_emitter({event})",
            metadata={
                "emitter": emitter,
                "event": event,
            },
        )
