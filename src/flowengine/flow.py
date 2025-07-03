from __future__ import annotations

from collections.abc import AsyncIterator, Awaitable, Callable, Iterable
from typing import Any, Generic, NoReturn, TypeVar, Union, overload

Input = TypeVar("Input")
Output = TypeVar("Output")
Newput = TypeVar("Newput")

# TypeVars for static methods
T = TypeVar("T")
U = TypeVar("U")

# Type alias for flow metadata
FlowMetadata = dict[str, Any]


class Flow(Generic[Input, Output]):
    def __init__(
        self,
        fn: Callable[[AsyncIterator[Input]], AsyncIterator[Output]],
        name: str = "<anonymous>",
        metadata: FlowMetadata | None = None,
    ) -> None:
        super().__init__()
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

    def __aiter__(self) -> NoReturn:
        """Prevent direct iteration - flows must be called with a stream."""
        raise TypeError(
            "Flows must be called with a stream to get an iterator (e.g., flow(stream))"
        )

    def map(self, fn: Callable[[Output], Newput]) -> "Flow[Input, Newput]":
        """Map a function over the output of the flow."""

        async def _mapped(stream: AsyncIterator[Input]) -> AsyncIterator[Newput]:
            inner_iter = self(stream).__aiter__()
            try:
                async for item in inner_iter:
                    yield fn(item)
            finally:
                if hasattr(inner_iter, "aclose"):
                    await inner_iter.aclose()  # type: ignore[attr-defined]

        return Flow(_mapped, name=f"{self.name}.map({fn.__name__})")

    def filter(self, predicate: Callable[[Output], bool]) -> "Flow[Input, Output]":
        """Filter the output of the flow based on a predicate."""

        async def _filtered(stream: AsyncIterator[Input]) -> AsyncIterator[Output]:
            inner_iter = self(stream).__aiter__()
            try:
                async for item in inner_iter:
                    if predicate(item):
                        yield item
            finally:
                if hasattr(inner_iter, "aclose"):
                    await inner_iter.aclose()  # type: ignore[attr-defined]

        return Flow(_filtered, name=f"{self.name}.filter({predicate.__name__})")

    def flat_map(
        self, fn: Callable[[Output], AsyncIterator[Newput]]
    ) -> "Flow[Input, Newput]":
        """Flat map a function over the output of the flow."""

        async def _flatmapped(stream: AsyncIterator[Input]) -> AsyncIterator[Newput]:
            inner_iter = self(stream).__aiter__()
            try:
                async for item in inner_iter:
                    async for sub in fn(item):
                        yield sub
            finally:
                if hasattr(inner_iter, "aclose"):
                    await inner_iter.aclose()  # type: ignore[attr-defined]

        return Flow(_flatmapped, name=f"{self.name}.flat_map({fn.__name__})")

    def to_list(self) -> Callable[[AsyncIterator[Input]], Awaitable[list[Output]]]:
        """Collect the output of the flow into a list."""

        async def _collect(stream: AsyncIterator[Input]) -> list[Output]:
            return [item async for item in self(stream)]

        return _collect

    def for_each(
        self, fn: Callable[[Output], Awaitable[None]]
    ) -> Callable[[AsyncIterator[Input]], Awaitable[None]]:
        """Consume the flow and apply a function to each item."""

        async def _consume(stream: AsyncIterator[Input]) -> None:
            async for item in self(stream):
                await fn(item)

        return _consume

    def __rshift__(self, other: "Flow[Output, Newput]") -> "Flow[Input, Newput]":
        """Pipe the output of this flow to another flow."""
        return Flow(lambda s: other(self(s)), name=f"{self.name} >> {other.name}")

    def collect(self) -> Callable[[AsyncIterator[Input]], Awaitable[list[Output]]]:
        """Ergonomic method to collect all items into a list.

        This is equivalent to to_list() but more discoverable in fluent APIs.
        """
        return self.to_list()

    def label(self, label: str) -> "Flow[Input, Output]":
        """Label the flow for debugging purposes."""

        async def _labeled(stream: AsyncIterator[Input]) -> AsyncIterator[Output]:
            print(f"[Flow:{label}] starting")
            async for item in self(stream):
                print(f"[Flow:{label}] yield: {item}")
                yield item

        return Flow(_labeled, name=f"{self.name}.label({label})")

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
        results: list[Output] = []
        count = 0
        async_iter = self(stream).__aiter__()
        try:
            async for item in async_iter:
                if count >= limit:
                    break
                results.append(item)
                count += 1
        finally:
            # Ensure async iterator is properly closed
            if hasattr(async_iter, "aclose"):
                await async_iter.aclose()  # type: ignore[attr-defined]
        return results

    def print(self) -> "Flow[Input, Output]":
        """Print flow information for debugging (chainable).

        Returns:
            Self for method chaining
        """
        print(f"📦 Flow<{self.name}> :: {self.fn.__name__}")
        if self.metadata:
            print("  metadata:", self.metadata)
        return self

    def with_fallback(self, default: Output) -> "Flow[Input, Output]":
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

    def batch(self, size: int) -> "Flow[Input, list[Output]]":
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
    @overload
    def from_value_fn(fn: Callable[[T], Awaitable[U]]) -> Flow[T, U]: ...

    @staticmethod
    @overload
    def from_value_fn(
        fn: None = None,
    ) -> Callable[[Callable[[T], Awaitable[U]]], Flow[T, U]]: ...

    @staticmethod
    def from_value_fn(
        fn: Callable[[T], Awaitable[U]] | None = None,
    ) -> Flow[T, U] | Callable[[Callable[[T], Awaitable[U]]], Flow[T, U]]:
        """Create a flow from an async function that takes an input and returns an output.

        Can be used as a decorator::

            @Flow.from_value_fn
            async def process(item):
                return await some_async_operation(item)
        """

        def decorator(f: Callable[[T], Awaitable[U]]) -> Flow[T, U]:
            async def _wrapper(stream: AsyncIterator[T]) -> AsyncIterator[U]:
                async for item in stream:
                    yield await f(item)

            return Flow(_wrapper, name=f.__name__)

        if fn is None:
            return decorator
        else:
            return decorator(fn)

    @staticmethod
    @overload
    def from_event_fn(fn: Callable[[T], AsyncIterator[U]]) -> Flow[T, U]: ...

    @staticmethod
    @overload
    def from_event_fn(
        fn: None = None,
    ) -> Callable[[Callable[[T], AsyncIterator[U]]], Flow[T, U]]: ...

    @staticmethod
    def from_event_fn(
        fn: Callable[[T], AsyncIterator[U]] | None = None,
    ) -> Flow[T, U] | Callable[[Callable[[T], AsyncIterator[U]]], Flow[T, U]]:
        """Create a flow from an async function that returns an async iterator.

        Can be used as a decorator::

            @Flow.from_event_fn
            async def split_lines(text):
                for line in text.split('\\n'):
                    yield line
        """

        def decorator(f: Callable[[T], AsyncIterator[U]]) -> Flow[T, U]:
            async def _wrapper(stream: AsyncIterator[T]) -> AsyncIterator[U]:
                async for item in stream:
                    async for sub in f(item):
                        yield sub

            return Flow(_wrapper, name=f.__name__)

        if fn is None:
            return decorator
        else:
            return decorator(fn)

    @staticmethod
    @overload
    def from_sync_fn(fn: Callable[[T], U]) -> Flow[T, U]: ...

    @staticmethod
    @overload
    def from_sync_fn(
        fn: None = None,
    ) -> Callable[[Callable[[T], U]], Flow[T, U]]: ...

    @staticmethod
    def from_sync_fn(
        fn: Callable[[T], U] | None = None,
    ) -> Flow[T, U] | Callable[[Callable[[T], U]], Flow[T, U]]:
        """Create a flow from a synchronous function that takes an input and returns an output.

        Can be used as a decorator::

            @Flow.from_sync_fn
            def double(x):
                return x * 2
        """

        def decorator(f: Callable[[T], U]) -> Flow[T, U]:
            async def _wrapper(stream: AsyncIterator[T]) -> AsyncIterator[U]:
                async for item in stream:
                    yield f(item)

            return Flow(_wrapper, name=f.__name__)

        if fn is None:
            return decorator
        else:
            return decorator(fn)

    @staticmethod
    def from_iterable(iterable: Iterable[T]) -> Flow[Any, T]:
        """Create a flow from an iterable that ignores input stream.

        Args:
            iterable: Any iterable (list, tuple, range, etc.) to convert to flow

        Returns:
            Flow that yields all items from the iterable, ignoring input stream

        Example::

            # Create flow from list
            flow = Flow.from_iterable([1, 2, 3])

            # Create flow from range
            flow = Flow.from_iterable(range(10))
        """

        async def _wrapper(stream: AsyncIterator[Any]) -> AsyncIterator[T]:
            # Ignore the input stream and yield from the iterable
            for item in iterable:
                yield item

        return Flow(_wrapper, name="from_iterable")

    @staticmethod
    def from_emitter(
        register: Union[
            Callable[[Callable[[T], None]], None],
            Callable[[Callable[[T], None]], Awaitable[None]],
        ]
    ) -> Flow[Any, T]:
        """Create a flow from an emitter system that registers callbacks.

        Args:
            register: Function that registers a callback. Can be sync or async.
                      The callback will be called with emitted values.

        Returns:
            Flow that yields all values emitted through the callback system

        Example::

            # Sync emitter
            def setup_callbacks(callback):
                callback("event1")
                callback("event2")

            flow = Flow.from_emitter(setup_callbacks)

            # Async emitter
            async def setup_async_callbacks(callback):
                await some_async_setup()
                callback("async_event")

            flow = Flow.from_emitter(setup_async_callbacks)
        """

        async def _wrapper(stream: AsyncIterator[Any]) -> AsyncIterator[T]:
            # Ignore the input stream and collect emitted values
            emitted_values: list[T] = []

            def callback(value: T) -> None:
                emitted_values.append(value)

            # Call the register function with our callback
            result = register(callback)

            # If register function is async, await it
            if result is not None and hasattr(result, "__await__"):
                await result

            # Yield all collected values
            for value in emitted_values:
                yield value

        return Flow(_wrapper, name="from_emitter")

    @staticmethod
    def identity() -> Flow[T, T]:
        """Create an identity flow that passes items through unchanged.

        Returns:
            Flow that yields each input item unchanged

        Example::

            # Create identity flow
            flow = Flow.identity()

            # Use with any stream type
            async def string_stream():
                yield "hello"
                yield "world"

            result = flow(string_stream())
            items = [item async for item in result]  # ["hello", "world"]
        """

        async def _identity(stream: AsyncIterator[T]) -> AsyncIterator[T]:
            async for item in stream:
                yield item

        return Flow(_identity, name="identity")

    @staticmethod
    def pure(value: T) -> Flow[Any, T]:
        """Create a flow that yields a single pure value.

        Args:
            value: The value to yield

        Returns:
            Flow that yields the given value once, ignoring input stream

        Example::

            # Create pure value flow
            flow = Flow.pure("hello")

            # Yields "hello" regardless of input
            async def any_stream():
                yield 1
                yield 2

            result = flow(any_stream())
            items = [item async for item in result]  # ["hello"]
        """

        async def _pure(stream: AsyncIterator[Any]) -> AsyncIterator[T]:
            # Ignore the input stream and yield the pure value once
            yield value

        return Flow(_pure, name=f"pure({value})")
