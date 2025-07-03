from __future__ import annotations

from collections.abc import AsyncIterator, Callable
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
