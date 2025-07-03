from __future__ import annotations

from collections.abc import AsyncIterator, Awaitable, Callable
from typing import Any, Generic, NoReturn, TypeVar

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
