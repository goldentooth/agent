from atomic_agents.lib.base.base_tool import BaseTool
from typing import Protocol, runtime_checkable

@runtime_checkable
class HasTools(Protocol):
  """Protocol for objects that have tools defined in them."""

  tools: dict[str, BaseTool]
  """A dictionary of tool names to tool instances."""

@runtime_checkable
class HasGetInfo(Protocol):
  """Protocol for objects that have a get_info method."""

  def get_info(self) -> str: ...
