from typing import List, TypeVar, Generic, AsyncIterator
from .rule import Rule
from ..flow import Flow

TIn = TypeVar("TIn")


class RuleEngine(Generic[TIn]):
    """A rule engine that evaluates a list of rules against a context and applies actions based on matching conditions."""

    def __init__(self, rules: List[Rule[TIn]]):
        """Initialize the rule engine with a list of rules."""
        self.rules = sorted(rules, key=lambda r: -r.priority)

    async def __call__(self, ctx: TIn) -> TIn:
        """Evaluate the rules against the context and return the modified context."""
        return await self.evaluate(ctx)

    async def evaluate(self, ctx: TIn) -> TIn:
        """Evaluate the rules against the context and apply actions for matching rules."""
        for rule in self.rules:
            ctx = await rule.apply(ctx)
        return ctx

    def add_rule(self, rule: Rule[TIn]) -> None:
        """Add a new rule to the rule engine."""
        self.rules.append(rule)
        self.rules.sort(key=lambda r: -r.priority)

    def as_flow(self) -> Flow[TIn, TIn]:
        """Convert the rule engine to a flow that evaluates the rules."""

        async def _flow_fn(stream: AsyncIterator[TIn]) -> AsyncIterator[TIn]:
            async for item in stream:
                yield await self.evaluate(item)

        return Flow(
            _flow_fn,
            name="RuleEngine",
            metadata={
                "rules": [rule.name for rule in self.rules],
                "count": len(self.rules),
            },
        )

    def as_thunk(self):
        """Convert the rule engine to a thunk that evaluates the rules (for backward compatibility)."""
        from .main import Thunk

        async def _thunk(ctx: TIn) -> TIn:
            return await self.evaluate(ctx)

        return Thunk(
            _thunk,
            name="RuleEngine",
            metadata={
                "rules": [rule.name for rule in self.rules],
                "count": len(self.rules),
            },
        )
