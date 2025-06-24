from __future__ import annotations
from atomic_agents.agents.base_agent import BaseAgentInputSchema, BaseAgentOutputSchema
from typing import Protocol, runtime_checkable

@runtime_checkable
class AgentInputConvertible(Protocol):
  """Protocol for objects that can be converted to a BaseAgentInputSchema."""

  def as_agent_input(self) -> BaseAgentInputSchema: ...

@runtime_checkable
class AgentOutputConvertible(Protocol):
  """Protocol for objects that can be converted to a BaseAgentOutputSchema."""

  def as_agent_output(self) -> BaseAgentOutputSchema: ...
