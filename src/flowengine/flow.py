from __future__ import annotations

from collections.abc import AsyncIterator, Callable
from typing import Any, Generic, TypeVar

Input = TypeVar("Input")
Output = TypeVar("Output")

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
