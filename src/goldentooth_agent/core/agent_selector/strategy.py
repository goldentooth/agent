from atomic_agents.agents.base_agent import BaseAgent
from goldentooth_agent.core.context import Context
from typing import Protocol, runtime_checkable

@runtime_checkable
class AgentSelectorStrategy(Protocol):
  """Protocol for agent selection strategies."""
  name: str
  description: str

  def select_agent(self, context: Context) -> BaseAgent:
    """Select an agent based on the current context."""
    ...
