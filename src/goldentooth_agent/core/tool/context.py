from typing import Protocol
from atomic_agents.lib.base.base_tool import BaseTool

class HasTools(Protocol):
  """Protocol for objects that have tools defined in them."""

  tools: dict[str, BaseTool]
  """A dictionary of tool names to tool instances."""
