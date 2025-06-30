from collections.abc import AsyncIterator
from typing import Generic, TypeVar

from goldentooth_agent.flow_engine import Flow

from .rule import Rule

TIn = TypeVar("TIn")


class RuleEngine(Generic[TIn]):
    """A rule engine that evaluates a list of rules against a context and applies actions based on matching conditions.

    The RuleEngine is pure Flow-based and processes rules in priority order. It can be converted
    to a Flow for stream processing or used directly for single context evaluation.
    """

    def __init__(self, rules: list[Rule[TIn]]):
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
        """Convert the rule engine to a flow that evaluates the rules for each item in a stream."""

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
