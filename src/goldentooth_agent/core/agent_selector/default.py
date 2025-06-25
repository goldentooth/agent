from __future__ import annotations
from antidote import inject
from atomic_agents.agents.base_agent import BaseAgent
from goldentooth_agent.core.agent import AgentRegistry
from goldentooth_agent.core.context import Context
from .strategy import AgentSelectorStrategy
from .strategy_registry import register_agent_selector_strategy

@register_agent_selector_strategy
class DefaultAgentSelectorStrategy(AgentSelectorStrategy):
  """Default agent selector strategy that selects the default agent."""

  id = "default"
  description = "Selects the default agent."

  @classmethod
  def create(cls) -> DefaultAgentSelectorStrategy:
    """Factory method to create an instance of DefaultAgentSelectorStrategy."""
    return cls()

  def select_agent(self, context: Context, agent_registry: AgentRegistry = inject.me()) -> BaseAgent:
    """Select the default agent."""
    agent = agent_registry.get('default')
    return agent
