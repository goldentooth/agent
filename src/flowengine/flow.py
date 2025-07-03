from __future__ import annotations

from collections.abc import AsyncIterator, Awaitable, Callable
from typing import Any, Generic, NoReturn, TypeVar, overload

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
            async for item in self(stream):
                yield fn(item)

        return Flow(_mapped, name=f"{self.name}.map({fn.__name__})")

    def filter(self, predicate: Callable[[Output], bool]) -> "Flow[Input, Output]":
        """Filter the output of the flow based on a predicate."""

        async def _filtered(stream: AsyncIterator[Input]) -> AsyncIterator[Output]:
            async for item in self(stream):
                if predicate(item):
                    yield item

        return Flow(_filtered, name=f"{self.name}.filter({predicate.__name__})")

    def flat_map(
        self, fn: Callable[[Output], AsyncIterator[Newput]]
    ) -> "Flow[Input, Newput]":
        """Flat map a function over the output of the flow."""

        async def _flatmapped(stream: AsyncIterator[Input]) -> AsyncIterator[Newput]:
            async for item in self(stream):
                async for sub in fn(item):
                    yield sub

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
