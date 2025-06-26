from __future__ import annotations
from typing import (
    TypeVar,
    AsyncIterator,
    Awaitable,
    Callable,
    Generic,
    Any,
)
import asyncio

TIn = TypeVar("TIn")
TOut = TypeVar("TOut")
TNew = TypeVar("TNew")


class Flow(Generic[TIn, TOut]):
    def __init__(
        self,
        fn: Callable[[AsyncIterator[TIn]], AsyncIterator[TOut]],
        name: str = "<anonymous>",
        metadata: dict[str, Any] = {},
    ) -> None:
        self.fn = fn
        self.name = name
        self.metadata = metadata
        self.__name__ = name

    def __call__(self, stream: AsyncIterator[TIn]) -> AsyncIterator[TOut]:
        """Call the flow with the given stream and return an async iterator."""
        return self.fn(stream)

    def map(self, fn: Callable[[TOut], TNew]) -> Flow[TIn, TNew]:
        """Map a function over the output of the flow."""

        async def _mapped(stream: AsyncIterator[TIn]) -> AsyncIterator[TNew]:
            async for item in self(stream):
                yield fn(item)

        return Flow(_mapped, name=f"{self.name}.map({fn.__name__})")

    def filter(self, predicate: Callable[[TOut], bool]) -> Flow[TIn, TOut]:
        """Filter the output of the flow based on a predicate."""

        async def _filtered(stream: AsyncIterator[TIn]) -> AsyncIterator[TOut]:
            async for item in self(stream):
                if predicate(item):
                    yield item

        return Flow(_filtered, name=f"{self.name}.filter({predicate.__name__})")

    def flat_map(self, fn: Callable[[TOut], AsyncIterator[TNew]]) -> Flow[TIn, TNew]:
        """Flat map a function over the output of the flow."""

        async def _flatmapped(stream: AsyncIterator[TIn]) -> AsyncIterator[TNew]:
            async for item in self(stream):
                async for sub in fn(item):
                    yield sub

        return Flow(_flatmapped, name=f"{self.name}.flat_map({fn.__name__})")

    def for_each(
        self, fn: Callable[[TOut], Awaitable[None]]
    ) -> Callable[[AsyncIterator[TIn]], Awaitable[None]]:
        """Consume the flow and apply a function to each item."""

        async def _consume(stream: AsyncIterator[TIn]) -> None:
            async for item in self(stream):
                await fn(item)

        return _consume

    def to_list(self) -> Callable[[AsyncIterator[TIn]], Awaitable[list[TOut]]]:
        """Collect the output of the flow into a list."""

        async def _collect(stream: AsyncIterator[TIn]) -> list[TOut]:
            return [item async for item in self(stream)]

        return _collect

    def __rshift__(self, other: Flow[TOut, TNew]) -> Flow[TIn, TNew]:
        """Pipe the output of this flow to another flow."""
        return Flow(lambda s: other(self(s)), name=f"{self.name} >> {other.name}")

    def label(self, label: str) -> Flow[TIn, TOut]:
        """Label the flow for debugging purposes."""

        async def _labeled(stream: AsyncIterator[TIn]) -> AsyncIterator[TOut]:
            print(f"[Flow:{label}] starting")
            async for item in self(stream):
                print(f"[Flow:{label}] yield: {item}")
                yield item

        return Flow(_labeled, name=f"{self.name}.label({label})")

    @staticmethod
    def from_value_fn(fn: Callable[[TIn], Awaitable[TOut]]) -> Flow[TIn, TOut]:
        """Create a flow from an async function that takes an input and returns an output."""

        async def _wrapper(stream: AsyncIterator[TIn]) -> AsyncIterator[TOut]:
            async for item in stream:
                yield await fn(item)

        return Flow(_wrapper, name=fn.__name__)

    @staticmethod
    def from_sync_fn(fn: Callable[[TIn], TOut]) -> Flow[TIn, TOut]:
        """Create a flow from a synchronous function that takes an input and returns an output."""

        async def _wrapper(stream: AsyncIterator[TIn]) -> AsyncIterator[TOut]:
            async for item in stream:
                yield fn(item)

        return Flow(_wrapper, name=fn.__name__)

    @staticmethod
    def from_event_fn(fn: Callable[[TIn], AsyncIterator[TOut]]) -> Flow[TIn, TOut]:
        """Create a flow from an async function that returns an async iterator."""

        async def _wrapper(stream: AsyncIterator[TIn]) -> AsyncIterator[TOut]:
            async for item in stream:
                async for sub in fn(item):
                    yield sub

        return Flow(_wrapper, name=fn.__name__)

    @staticmethod
    def from_iterable(iterable: list[TIn]) -> Flow[None, TIn]:
        """Create a flow from an iterable."""

        async def _source(_: AsyncIterator[None]) -> AsyncIterator[TIn]:
            for item in iterable:
                yield item

        return Flow(_source, name="from_iterable")

    @staticmethod
    def from_emitter(
        register: Callable[[Callable[[TOut], None]], None],
    ) -> Flow[None, TOut]:
        """Create a flow from an emitter that registers a callback to receive items."""

        async def _stream(_: AsyncIterator[None]) -> AsyncIterator[TOut]:
            queue: asyncio.Queue = asyncio.Queue()

            def on_emit(item):
                queue.put_nowait(item)

            register(on_emit)

            while True:
                item = await queue.get()
                yield item

        return Flow(_stream, name="from_emitter")
