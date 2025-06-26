from typing import Callable, Generic, Optional, TypeVar
from dataclasses import dataclass
from .main import Thunk

TIn = TypeVar("TIn")


@dataclass
class Rule(Generic[TIn]):
    """A rule that applies a condition to an input and executes an action if the condition is met."""

    name: str
    condition: Callable[[TIn], bool]
    action: Thunk[TIn, TIn]
    priority: int = 0
    description: Optional[str] = None

    async def __call__(self, ctx: TIn) -> TIn:
        """Evaluate the rule against the context and return the modified context."""
        return await self.apply(ctx)

    async def apply(self, ctx: TIn) -> TIn:
        """Apply the rule to the given context."""
        if self.condition(ctx):
            ctx = await self.action(ctx)
        return ctx

    def as_thunk(self) -> Thunk[TIn, TIn]:
        """Convert the rule to a thunk that applies the rule."""

        async def _thunk(ctx: TIn) -> TIn:
            return await self.apply(ctx)

        return Thunk(
            _thunk,
            name=self.name,
            metadata={
                "condition": self.condition.__name__,
                "action": self.action.name,
                "priority": self.priority,
                "description": self.description,
            },
        )
