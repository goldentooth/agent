from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator, Awaitable, Callable
from typing import Any, Generic, TypeVar

Input = TypeVar("Input")
Output = TypeVar("Output")
Newput = TypeVar("Newput")

# Type alias for flow metadata
FlowMetadata = dict[str, Any]


class Flow(Generic[Input, Output]):
    def __init__(
        self,
        fn: Callable[[AsyncIterator[Input]], AsyncIterator[Output]],
        name: str = "<anonymous>",
        metadata: FlowMetadata | None = None,
    ) -> None:
        self.fn = fn
        self.name = name
        self.metadata = metadata if metadata is not None else {}
        self.__name__ = name

    def __call__(self, stream: AsyncIterator[Input]) -> AsyncIterator[Output]:
        """Call the flow with the given stream and return an async iterator."""
        return self.fn(stream)

    def __repr__(self) -> str:
        """Rich representation for debugging and development."""
        return (
            f"<Flow name='{self.name}' fn={self.fn.__name__} metadata={self.metadata}>"
        )

    def __aiter__(self) -> None:
        """Prevent direct iteration - flows must be called with a stream."""
        raise TypeError(
            "Flows must be called with a stream to get an iterator (e.g., flow(stream))"
        )

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

    def flat_map(
        self, fn: Callable[[Output], AsyncIterator[Newput]]
    ) -> Flow[Input, Newput]:
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

    def collect(self) -> Callable[[AsyncIterator[Input]], Awaitable[list[Output]]]:
        """Ergonomic method to collect all items into a list.

        This is equivalent to to_list() but more discoverable in fluent APIs.
        """
        return self.to_list()

    async def preview(
        self, stream: AsyncIterator[Input], limit: int = 10
    ) -> list[Output]:
        """Preview the first few items from a flow for REPL/Jupyter development.

        Args:
            stream: Input stream to process
            limit: Maximum number of items to collect

        Returns:
            List of up to `limit` items from the flow
        """
        results = []
        count = 0
        async_iter = aiter(self(stream))
        try:
            async for item in async_iter:
                results.append(item)
                count += 1
                if count >= limit:
                    break
        finally:
            # Ensure async iterator is properly closed
            if hasattr(async_iter, "aclose"):
                await async_iter.aclose()
        return results

    def print(self) -> Flow[Input, Output]:
        """Print flow information for debugging (chainable).

        Returns:
            Self for method chaining
        """
        print(f"📦 Flow<{self.name}> :: {self.fn.__name__}")
        if self.metadata:
            print("  metadata:", self.metadata)
        return self

    def with_fallback(self, default: Output) -> Flow[Input, Output]:
        """Add a fallback value that's yielded if the flow produces no items.

        Args:
            default: Value to yield if the flow is empty

        Returns:
            New flow that yields the default value if original flow is empty
        """

        async def _flow(stream: AsyncIterator[Input]) -> AsyncIterator[Output]:
            yielded_any = False
            async for item in self(stream):
                yielded_any = True
                yield item
            if not yielded_any:
                yield default

        return Flow(_flow, name=f"{self.name}.with_fallback({default})")

    def batch(self, size: int) -> Flow[Input, list[Output]]:
        """Batch the output into groups of the specified size.

        Args:
            size: Number of items per batch

        Returns:
            Flow that yields lists of items
        """

        async def _batched(stream: AsyncIterator[Input]) -> AsyncIterator[list[Output]]:
            output_stream = self(stream)
            batch: list[Output] = []
            async for item in output_stream:
                batch.append(item)
                if len(batch) >= size:
                    yield batch
                    batch = []
            # Yield remaining items if any
            if batch:
                yield batch

        return Flow(_batched, name=f"{self.name}.batch({size})")

    @staticmethod
    def from_value_fn(
        fn: Callable[[Input], Awaitable[Output]] | None = None,
    ) -> (
        Flow[Input, Output]
        | Callable[[Callable[[Input], Awaitable[Output]]], Flow[Input, Output]]
    ):
        """Create a flow from an async function that takes an input and returns an output.

        Can be used as a decorator:
            @Flow.from_value_fn
            async def process(item):
                return await some_async_operation(item)
        """

        def decorator(f: Callable[[Input], Awaitable[Output]]) -> Flow[Input, Output]:
            async def _wrapper(stream: AsyncIterator[Input]) -> AsyncIterator[Output]:
                async for item in stream:
                    yield await f(item)

            return Flow(_wrapper, name=f.__name__)

        if fn is None:
            return decorator
        else:
            return decorator(fn)

    @staticmethod
    def from_sync_fn(
        fn: Callable[[Input], Output] | None = None,
    ) -> (
        Flow[Input, Output] | Callable[[Callable[[Input], Output]], Flow[Input, Output]]
    ):
        """Create a flow from a synchronous function that takes an input and returns an output.

        Can be used as a decorator:
            @Flow.from_sync_fn
            def double(x):
                return x * 2
        """

        def decorator(f: Callable[[Input], Output]) -> Flow[Input, Output]:
            async def _wrapper(stream: AsyncIterator[Input]) -> AsyncIterator[Output]:
                async for item in stream:
                    yield f(item)

            return Flow(_wrapper, name=f.__name__)

        if fn is None:
            return decorator
        else:
            return decorator(fn)

    @staticmethod
    def from_event_fn(
        fn: Callable[[Input], AsyncIterator[Output]] | None = None,
    ) -> (
        Flow[Input, Output]
        | Callable[[Callable[[Input], AsyncIterator[Output]]], Flow[Input, Output]]
    ):
        """Create a flow from an async function that returns an async iterator.

        Can be used as a decorator:
            @Flow.from_event_fn
            async def split_lines(text):
                for line in text.split('\\n'):
                    yield line
        """

        def decorator(
            f: Callable[[Input], AsyncIterator[Output]],
        ) -> Flow[Input, Output]:
            async def _wrapper(stream: AsyncIterator[Input]) -> AsyncIterator[Output]:
                async for item in stream:
                    async for sub in f(item):
                        yield sub

            return Flow(_wrapper, name=f.__name__)

        if fn is None:
            return decorator
        else:
            return decorator(fn)

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
            queue: asyncio.Queue[Output] = asyncio.Queue[Output]()

            def on_emit(item: Output) -> None:
                queue.put_nowait(item)

            register(on_emit)

            while True:
                item = await queue.get()
                yield item

        return Flow(_stream, name="from_emitter")

    @staticmethod
    def identity() -> Flow[Input, Input]:
        """Create an identity flow that passes items through unchanged.

        Returns:
            Flow that yields each input item unchanged
        """

        async def _identity(stream: AsyncIterator[Input]) -> AsyncIterator[Input]:
            async for item in stream:
                yield item

        return Flow(_identity, name="identity")

    @staticmethod
    def pure(value: Output) -> Flow[None, Output]:
        """Create a flow that yields a single pure value.

        Args:
            value: The value to yield

        Returns:
            Flow that yields the given value once
        """

        async def _single(_: AsyncIterator[None]) -> AsyncIterator[Output]:
            yield value

        return Flow(_single, name=f"pure({value})")
