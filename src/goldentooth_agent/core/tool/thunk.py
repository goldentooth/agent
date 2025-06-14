from goldentooth_agent.core.thunk import Thunk
from atomic_agents.lib.base.base_io_schema import BaseIOSchema
from atomic_agents.lib.base.base_tool import BaseTool

def thunkify_tool(tool: BaseTool) -> Thunk[type[BaseIOSchema], BaseIOSchema]:
  """Convert a tool into a thunk."""
  async def _as_thunk(params: type[BaseIOSchema]) -> BaseIOSchema:
    """Run the tool with the given parameters."""
    return tool.run(params)
  return Thunk(_as_thunk)
