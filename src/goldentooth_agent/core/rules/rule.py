from collections.abc import AsyncIterator, Callable
from dataclasses import dataclass
from typing import Any, Generic, TypeVar

from ..flow import Flow

TIn = TypeVar("TIn")


@dataclass
class Rule(Generic[TIn]):
    """A rule that applies a condition to an input and executes an action if the condition is met.

    Rules are pure Flow-based components that evaluate conditions and apply transformations
    conditionally. They integrate seamlessly with the Flow system for stream processing.
    """

    name: str
    condition: Callable[[TIn], bool]
    action: Flow[TIn, TIn]
    priority: int = 0
    description: str | None = None

    async def __call__(self, ctx: TIn) -> TIn:
        """Evaluate the rule against the context and return the modified context."""
        return await self.apply(ctx)

    async def apply(self, ctx: TIn) -> TIn:
        """Apply the rule to the given context."""
        if self.condition(ctx):
            # Convert single context to stream, apply flow, and extract result
            async def single_item_stream() -> AsyncIterator[Any]:
                yield ctx

            # Get the first (and only) result from the flow
            result_stream = self.action(single_item_stream())
            async for result in result_stream:
                return result

            # Fallback if flow produces no output
            return ctx
        return ctx

    def as_flow(self) -> Flow[TIn, TIn]:
        """Convert the rule to a flow that applies the rule to each item in a stream."""

        async def _flow_fn(stream: AsyncIterator[TIn]) -> AsyncIterator[TIn]:
            async for item in stream:
                yield await self.apply(item)

        return Flow(
            _flow_fn,
            name=self.name,
            metadata={
                "condition": self.condition.__name__,
                "action": self.action.name,
                "priority": self.priority,
                "description": self.description,
            },
        )
