from atomic_agents.agents.base_agent import BaseAgent
from typing import Protocol, runtime_checkable

@runtime_checkable
class HasAgents(Protocol):
  """Protocol for objects that have agents defined in them."""

  agents: dict[str, BaseAgent]
  """A dictionary of agent names to agent instances."""

@runtime_checkable
class HasAgent(Protocol):
  """Protocol for objects that have a single agent defined in them."""

  agent: BaseAgent
  """The agent instance."""
