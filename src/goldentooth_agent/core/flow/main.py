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

Input = TypeVar("Input")
Output = TypeVar("Output")
Newput = TypeVar("Newput")


class Flow(Generic[Input, Output]):
    def __init__(
        self,
        fn: Callable[[AsyncIterator[Input]], AsyncIterator[Output]],
        name: str = "<anonymous>",
        metadata: dict[str, Any] = {},
    ) -> None:
        self.fn = fn
        self.name = name
        self.metadata = metadata
        self.__name__ = name

    def __call__(self, stream: AsyncIterator[Input]) -> AsyncIterator[Output]:
        """Call the flow with the given stream and return an async iterator."""
        return self.fn(stream)

    def map(self, fn: Callable[[Output], Newput]) -> Flow[Input, Newput]:
        """Map a function over the output of the flow."""

        async def _mapped(stream: AsyncIterator[Input]) -> AsyncIterator[Newput]:
            async for item in self(stream):
                yield fn(item)

        return Flow(_mapped, name=f"{self.name}.map({fn.__name__})")

    def filter(self, predicate: Callable[[Output], bool]) -> Flow[Input, Output]:
        """Filter the output of the flow based on a predicate."""

        async def _filtered(stream: AsyncIterator[Input]) -> AsyncIterator[Output]:
            async for item in self(stream):
                if predicate(item):
                    yield item

        return Flow(_filtered, name=f"{self.name}.filter({predicate.__name__})")

    def flat_map(self, fn: Callable[[Output], AsyncIterator[Newput]]) -> Flow[Input, Newput]:
        """Flat map a function over the output of the flow."""

        async def _flatmapped(stream: AsyncIterator[Input]) -> AsyncIterator[Newput]:
            async for item in self(stream):
                async for sub in fn(item):
                    yield sub

        return Flow(_flatmapped, name=f"{self.name}.flat_map({fn.__name__})")

    def for_each(
        self, fn: Callable[[Output], Awaitable[None]]
    ) -> Callable[[AsyncIterator[Input]], Awaitable[None]]:
        """Consume the flow and apply a function to each item."""

        async def _consume(stream: AsyncIterator[Input]) -> None:
            async for item in self(stream):
                await fn(item)

        return _consume

    def to_list(self) -> Callable[[AsyncIterator[Input]], Awaitable[list[Output]]]:
        """Collect the output of the flow into a list."""

        async def _collect(stream: AsyncIterator[Input]) -> list[Output]:
            return [item async for item in self(stream)]

        return _collect

    def __rshift__(self, other: Flow[Output, Newput]) -> Flow[Input, Newput]:
        """Pipe the output of this flow to another flow."""
        return Flow(lambda s: other(self(s)), name=f"{self.name} >> {other.name}")

    def label(self, label: str) -> Flow[Input, Output]:
        """Label the flow for debugging purposes."""

        async def _labeled(stream: AsyncIterator[Input]) -> AsyncIterator[Output]:
            print(f"[Flow:{label}] starting")
            async for item in self(stream):
                print(f"[Flow:{label}] yield: {item}")
                yield item

        return Flow(_labeled, name=f"{self.name}.label({label})")

    @staticmethod
    def from_value_fn(fn: Callable[[Input], Awaitable[Output]]) -> Flow[Input, Output]:
        """Create a flow from an async function that takes an input and returns an output."""

        async def _wrapper(stream: AsyncIterator[Input]) -> AsyncIterator[Output]:
            async for item in stream:
                yield await fn(item)

        return Flow(_wrapper, name=fn.__name__)

    @staticmethod
    def from_sync_fn(fn: Callable[[Input], Output]) -> Flow[Input, Output]:
        """Create a flow from a synchronous function that takes an input and returns an output."""

        async def _wrapper(stream: AsyncIterator[Input]) -> AsyncIterator[Output]:
            async for item in stream:
                yield fn(item)

        return Flow(_wrapper, name=fn.__name__)

    @staticmethod
    def from_event_fn(fn: Callable[[Input], AsyncIterator[Output]]) -> Flow[Input, Output]:
        """Create a flow from an async function that returns an async iterator."""

        async def _wrapper(stream: AsyncIterator[Input]) -> AsyncIterator[Output]:
            async for item in stream:
                async for sub in fn(item):
                    yield sub

        return Flow(_wrapper, name=fn.__name__)

    @staticmethod
    def from_iterable(iterable: list[Input]) -> Flow[None, Input]:
        """Create a flow from an iterable."""

        async def _source(_: AsyncIterator[None]) -> AsyncIterator[Input]:
            for item in iterable:
                yield item

        return Flow(_source, name="from_iterable")

    @staticmethod
    def from_emitter(
        register: Callable[[Callable[[Output], None]], None],
    ) -> Flow[None, Output]:
        """Create a flow from an emitter that registers a callback to receive items."""

        async def _stream(_: AsyncIterator[None]) -> AsyncIterator[Output]:
            queue: asyncio.Queue = asyncio.Queue()

            def on_emit(item):
                queue.put_nowait(item)

            register(on_emit)

            while True:
                item = await queue.get()
                yield item

        return Flow(_stream, name="from_emitter")
