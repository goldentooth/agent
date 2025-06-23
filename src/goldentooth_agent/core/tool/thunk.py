from atomic_agents.lib.base.base_io_schema import BaseIOSchema
from atomic_agents.lib.base.base_tool import BaseTool
from goldentooth_agent.core.context import Context
from goldentooth_agent.core.context_provider import AdHocContextProvider
from goldentooth_agent.core.system_prompt import disable_context_provider, enable_context_provider
from goldentooth_agent.core.thunk import Thunk, thunk
from .protocol import HasGetInfo

def thunkify_tool(tool: BaseTool) -> Thunk[BaseIOSchema, BaseIOSchema]:
  """Convert a tool into a thunk."""
  @thunk(name=f"thunkify_tool({repr(tool)})")
  async def _thunkify_tool(params: BaseIOSchema) -> BaseIOSchema:
    """Run the tool with the given parameters."""
    return tool.run(params) # type: ignore[call-arg]
  return _thunkify_tool

def enable_tool_context_provider(tool: BaseTool) -> Thunk[Context, Context]:
  """Enable a tool's context provider in the system prompt generator."""
  fn = tool.get_info if isinstance(tool, HasGetInfo) else lambda: "This tool does not have a get_info method."
  dcp = AdHocContextProvider(title=tool.tool_name, fn=fn)
  return enable_context_provider(dcp)

def disable_tool_context_provider(tool: BaseTool) -> Thunk[Context, Context]:
  """Disable a tool's context provider in the system prompt generator."""
  return disable_context_provider(tool.tool_name)
