from __future__ import annotations
from antidote import inject, injectable
from atomic_agents.agents.base_agent import BaseAgent
from goldentooth_agent.core.context import Context
from typing import Optional
from .strategy import AgentSelectorStrategy
from .strategy_registry import AgentSelectorStrategyRegistry


@injectable(factory_method="create")
class AgentSelector:
    """Class to select an agent based on the current context."""

    def __init__(self, strategy_id: Optional[str] = None) -> None:
        """Initialize the AgentSelector."""
        self.strategy_id = strategy_id

    @classmethod
    def create(cls) -> AgentSelector:
        """Factory method to create an instance of AgentSelector."""
        return cls()

    @inject.method
    def get_strategy(
        self, strategy_registry: AgentSelectorStrategyRegistry = inject.me()
    ) -> AgentSelectorStrategy:
        """Get the currently set strategy."""
        if self.strategy_id is None:
            raise ValueError("Strategy ID must be set before getting the strategy.")
        return strategy_registry.get(self.strategy_id)

    def select_agent(self, context: Context) -> BaseAgent:
        """Select an agent based on the current context."""
        return self.get_strategy().select_agent(context)
