from __future__ import annotations
from atomic_agents.lib.base.base_io_schema import BaseIOSchema
from atomic_agents.lib.base.base_tool import BaseTool
from goldentooth_agent.core.thunk import Thunk

class ToolBase(BaseTool):
  """Base class for tools in the GoldenTooth Agent framework."""

  @classmethod
  def create(cls) -> ToolBase:
    """Create an instance of this tool."""
    return cls()

  def as_thunk(self) -> Thunk:
    """Return a thunk for this tool."""
    async def _as_thunk(params: type[BaseIOSchema]) -> BaseIOSchema:
      return self.run(params)
    return Thunk(_as_thunk)
