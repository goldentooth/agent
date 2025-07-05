from __future__ import annotations

from collections.abc import Awaitable, Callable, Iterable
from typing import Any, AsyncGenerator, Generic, NoReturn, TypeVar, Union, overload

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
        fn: Callable[[AsyncGenerator[Input, None]], AsyncGenerator[Output, None]],
        name: str = "<anonymous>",
        metadata: FlowMetadata | None = None,
    ) -> None:
        super().__init__()
        self.fn = fn
        self.name = name
        self.metadata = metadata if metadata is not None else {}
        self.__name__ = name

    def __call__(
        self, stream: AsyncGenerator[Input, None]
    ) -> AsyncGenerator[Output, None]:
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

        async def _mapped(
            stream: AsyncGenerator[Input, None],
        ) -> AsyncGenerator[Newput, None]:
            inner_iter = self(stream)
            try:
                async for item in inner_iter:
                    yield fn(item)
            finally:
                await inner_iter.aclose()

        return Flow(_mapped, name=f"{self.name}.map({fn.__name__})")

    def filter(self, predicate: Callable[[Output], bool]) -> "Flow[Input, Output]":
        """Filter the output of the flow based on a predicate."""

        async def _filtered(
            stream: AsyncGenerator[Input, None],
        ) -> AsyncGenerator[Output, None]:
            inner_iter = self(stream)
            try:
                async for item in inner_iter:
                    if predicate(item):
                        yield item
            finally:
                await inner_iter.aclose()

        return Flow(_filtered, name=f"{self.name}.filter({predicate.__name__})")

    def flat_map(
        self, fn: Callable[[Output], AsyncGenerator[Newput, None]]
    ) -> "Flow[Input, Newput]":
        """Flat map a function over the output of the flow."""
        _flatmapped = self._create_flatmap_generator(fn)
        return Flow(_flatmapped, name=f"{self.name}.flat_map({fn.__name__})")

    def _create_flatmap_generator(
        self, fn: Callable[[Output], AsyncGenerator[Newput, None]]
    ) -> Callable[[AsyncGenerator[Input, None]], AsyncGenerator[Newput, None]]:
        """Create the flat map generator function."""
        return lambda stream: self._process_flatmap_stream(stream, fn)

    async def _process_flatmap_stream(
        self,
        stream: AsyncGenerator[Input, None],
        fn: Callable[[Output], AsyncGenerator[Newput, None]],
    ) -> AsyncGenerator[Newput, None]:
        """Process stream through flat map function."""
        inner_iter = self(stream)
        try:
            async for item in inner_iter:
                async for sub in fn(item):
                    yield sub
        finally:
            await inner_iter.aclose()

    def to_list(
        self,
    ) -> Callable[[AsyncGenerator[Input, None]], Awaitable[list[Output]]]:
        """Collect the output of the flow into a list."""

        async def _collect(stream: AsyncGenerator[Input, None]) -> list[Output]:
            return [item async for item in self(stream)]

        return _collect

    def for_each(
        self, fn: Callable[[Output], Awaitable[None]]
    ) -> Callable[[AsyncGenerator[Input, None]], Awaitable[None]]:
        """Consume the flow and apply a function to each item."""

        async def _consume(stream: AsyncGenerator[Input, None]) -> None:
            async for item in self(stream):
                await fn(item)

        return _consume

    def __rshift__(self, other: "Flow[Output, Newput]") -> "Flow[Input, Newput]":
        """Pipe the output of this flow to another flow."""
        return Flow(lambda s: other(self(s)), name=f"{self.name} >> {other.name}")

    def collect(
        self,
    ) -> Callable[[AsyncGenerator[Input, None]], Awaitable[list[Output]]]:
        """Ergonomic method to collect all items into a list.

        This is equivalent to to_list() but more discoverable in fluent APIs.
        """
        return self.to_list()

    def label(self, label: str) -> "Flow[Input, Output]":
        """Label the flow for debugging purposes."""

        async def _labeled(
            stream: AsyncGenerator[Input, None],
        ) -> AsyncGenerator[Output, None]:
            print(f"[Flow:{label}] starting")
            async for item in self(stream):
                print(f"[Flow:{label}] yield: {item}")
                yield item

        return Flow(_labeled, name=f"{self.name}.label({label})")

    async def preview(
        self, stream: AsyncGenerator[Input, None], limit: int = 10
    ) -> list[Output]:
        """Preview the first few items from a flow for REPL/Jupyter development.

        Args:
            stream: Input stream to process
            limit: Maximum number of items to collect

        Returns:
            List of up to `limit` items from the flow
        """
        return await self._safe_preview_collection(stream, limit)

    async def _safe_preview_collection(
        self, stream: AsyncGenerator[Input, None], limit: int
    ) -> list[Output]:
        """Safely collect preview items with resource cleanup."""
        async_iter = self(stream)
        try:
            return await self._collect_preview_items(async_iter, limit)
        finally:
            await async_iter.aclose()

    async def _collect_preview_items(
        self, async_iter: AsyncGenerator[Output, None], limit: int
    ) -> list[Output]:
        """Collect preview items up to the limit."""
        results: list[Output] = []
        count = 0
        async for item in async_iter:
            if count >= limit:
                break
            results.append(item)
            count += 1
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
        _flow = self._create_fallback_generator(default)
        return Flow(_flow, name=f"{self.name}.with_fallback({default})")

    def _create_fallback_generator(
        self, default: Output
    ) -> Callable[[AsyncGenerator[Input, None]], AsyncGenerator[Output, None]]:
        """Create fallback generator that yields default if no items produced."""
        return lambda stream: self._process_fallback_stream(stream, default)

    async def _process_fallback_stream(
        self, stream: AsyncGenerator[Input, None], default: Output
    ) -> AsyncGenerator[Output, None]:
        """Process stream with fallback value if empty."""
        yielded_any = False
        async for item in self(stream):
            yielded_any = True
            yield item
        if not yielded_any:
            yield default

    def batch(self, size: int) -> "Flow[Input, list[Output]]":
        """Batch the output into groups of the specified size.

        Args:
            size: Number of items per batch

        Returns:
            Flow that yields lists of items
        """
        _batched = self._create_batch_generator(size)
        return Flow(_batched, name=f"{self.name}.batch({size})")

    def _create_batch_generator(
        self, size: int
    ) -> Callable[[AsyncGenerator[Input, None]], AsyncGenerator[list[Output], None]]:
        """Create the batch generator function."""
        return lambda stream: self._process_batch_stream(stream, size)

    async def _process_batch_stream(
        self, stream: AsyncGenerator[Input, None], size: int
    ) -> AsyncGenerator[list[Output], None]:
        """Process stream into batches of specified size."""
        output_stream = self(stream)
        batch: list[Output] = []
        async for item in output_stream:
            batch.append(item)
            if self._should_yield_batch(batch, size):
                yield batch
                batch = []
        if batch:
            yield batch

    def _should_yield_batch(self, batch: list[Output], size: int) -> bool:
        """Check if batch should be yielded based on size."""
        return len(batch) >= size

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

        Can be used as a decorator for async transformations.
        """
        decorator = Flow._create_value_fn_decorator()
        return decorator if fn is None else decorator(fn)

    @staticmethod
    def _create_value_fn_decorator() -> (
        Callable[[Callable[[T], Awaitable[U]]], Flow[T, U]]
    ):
        """Create decorator for async value functions."""

        def decorator(f: Callable[[T], Awaitable[U]]) -> Flow[T, U]:
            _wrapper = Flow._create_value_wrapper(f)
            return Flow(_wrapper, name=f.__name__)

        return decorator

    @staticmethod
    def _create_value_wrapper(
        f: Callable[[T], Awaitable[U]],
    ) -> Callable[[AsyncGenerator[T, None]], AsyncGenerator[U, None]]:
        """Create wrapper that applies function to each stream item."""

        async def _wrapper(
            stream: AsyncGenerator[T, None],
        ) -> AsyncGenerator[U, None]:
            async for item in stream:
                yield await f(item)

        return _wrapper

    @staticmethod
    @overload
    def from_event_fn(fn: Callable[[T], AsyncGenerator[U, None]]) -> Flow[T, U]: ...

    @staticmethod
    @overload
    def from_event_fn(
        fn: None = None,
    ) -> Callable[[Callable[[T], AsyncGenerator[U, None]]], Flow[T, U]]: ...

    @staticmethod
    def from_event_fn(
        fn: Callable[[T], AsyncGenerator[U, None]] | None = None,
    ) -> Flow[T, U] | Callable[[Callable[[T], AsyncGenerator[U, None]]], Flow[T, U]]:
        """Create a flow from an async function that returns an async iterator.

        Can be used as a decorator for functions that yield multiple values per input.
        """
        decorator = Flow._create_event_decorator()
        return decorator if fn is None else decorator(fn)

    @staticmethod
    def _create_event_decorator() -> (
        Callable[[Callable[[T], AsyncGenerator[U, None]]], Flow[T, U]]
    ):
        """Create decorator for event-based functions."""

        def decorator(f: Callable[[T], AsyncGenerator[U, None]]) -> Flow[T, U]:
            _wrapper = Flow._create_event_stream_wrapper(f)
            return Flow(_wrapper, name=f.__name__)

        return decorator

    @staticmethod
    def _create_event_stream_wrapper(
        f: Callable[[T], AsyncGenerator[U, None]],
    ) -> Callable[[AsyncGenerator[T, None]], AsyncGenerator[U, None]]:
        """Create wrapper for event stream processing."""

        async def _wrapper(
            stream: AsyncGenerator[T, None],
        ) -> AsyncGenerator[U, None]:
            async for item in stream:
                async for sub in f(item):
                    yield sub

        return _wrapper

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

        Can be used as a decorator for simple transformations.
        """
        decorator = Flow._create_sync_decorator()
        return decorator if fn is None else decorator(fn)

    @staticmethod
    def _create_sync_decorator() -> Callable[[Callable[[T], U]], Flow[T, U]]:
        """Create decorator for synchronous functions."""

        def decorator(f: Callable[[T], U]) -> Flow[T, U]:
            async def _wrapper(
                stream: AsyncGenerator[T, None],
            ) -> AsyncGenerator[U, None]:
                async for item in stream:
                    yield f(item)

            return Flow(_wrapper, name=f.__name__)

        return decorator

    @staticmethod
    def from_iterable(iterable: Iterable[T]) -> Flow[Any, T]:
        """Create a flow from an iterable that ignores input stream.

        Args:
            iterable: Any iterable to convert to flow

        Returns:
            Flow that yields all items from the iterable, ignoring input stream
        """
        _wrapper = Flow._create_iterable_wrapper(iterable)
        return Flow(_wrapper, name="from_iterable")

    @staticmethod
    def _create_iterable_wrapper(
        iterable: Iterable[T],
    ) -> Callable[[AsyncGenerator[Any, None]], AsyncGenerator[T, None]]:
        """Create wrapper for iterable-based flows."""

        async def _wrapper(
            stream: AsyncGenerator[Any, None],
        ) -> AsyncGenerator[T, None]:
            # Ignore the input stream and yield from the iterable
            for item in iterable:
                yield item

        return _wrapper

    @staticmethod
    def from_emitter(
        register: Union[
            Callable[[Callable[[T], None]], None],
            Callable[[Callable[[T], None]], Awaitable[None]],
        ],
    ) -> Flow[Any, T]:
        """Create a flow from an emitter system that registers callbacks.

        Args:
            register: Function that registers a callback
        """
        _wrapper = Flow._create_emitter_wrapper(register)
        return Flow(_wrapper, name="from_emitter")

    @staticmethod
    def _create_emitter_wrapper(
        register: Union[
            Callable[[Callable[[T], None]], None],
            Callable[[Callable[[T], None]], Awaitable[None]],
        ],
    ) -> Callable[[AsyncGenerator[Any, None]], AsyncGenerator[T, None]]:
        """Create wrapper for emitter-based flows."""
        return lambda stream: Flow._process_emitter_stream(stream, register)

    @staticmethod
    async def _process_emitter_stream(
        stream: AsyncGenerator[Any, None],
        register: Union[
            Callable[[Callable[[T], None]], None],
            Callable[[Callable[[T], None]], Awaitable[None]],
        ],
    ) -> AsyncGenerator[T, None]:
        """Process emitter stream by collecting and yielding values."""
        emitted_values = await Flow._collect_emitted_values(register)
        for value in emitted_values:
            yield value

    @staticmethod
    async def _collect_emitted_values(
        register: Union[
            Callable[[Callable[[T], None]], None],
            Callable[[Callable[[T], None]], Awaitable[None]],
        ],
    ) -> list[T]:
        """Collect values emitted through callback system."""
        emitted_values: list[T] = []
        callback = Flow._create_collector_callback(emitted_values)
        await Flow._execute_register_function(register, callback)
        return emitted_values

    @staticmethod
    def _create_collector_callback(emitted_values: list[T]) -> Callable[[T], None]:
        """Create callback that collects values into the provided list."""

        def callback(value: T) -> None:
            emitted_values.append(value)

        return callback

    @staticmethod
    async def _execute_register_function(
        register: Union[
            Callable[[Callable[[T], None]], None],
            Callable[[Callable[[T], None]], Awaitable[None]],
        ],
        callback: Callable[[T], None],
    ) -> None:
        """Execute register function, handling both sync and async cases."""
        result = register(callback)
        if result is not None and hasattr(result, "__await__"):
            await result

    @staticmethod
    def identity() -> Flow[T, T]:
        """Create an identity flow that passes items through unchanged.

        Returns:
            Flow that yields each input item unchanged
        """

        async def _identity(stream: AsyncGenerator[T, None]) -> AsyncGenerator[T, None]:
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
        """

        async def _pure(stream: AsyncGenerator[Any, None]) -> AsyncGenerator[T, None]:
            # Ignore the input stream and yield the pure value once
            yield value

        return Flow(_pure, name=f"pure({value})")
