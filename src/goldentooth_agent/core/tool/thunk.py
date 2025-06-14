from goldentooth_agent.core.thunk import Thunk, thunk
from atomic_agents.lib.base.base_io_schema import BaseIOSchema
from atomic_agents.lib.base.base_tool import BaseTool
from .context import HasTools, HasGetInfo

def thunkify_tool(tool: BaseTool) -> Thunk[type[BaseIOSchema], BaseIOSchema]:
  """Convert a tool into a thunk."""
  async def _as_thunk(params: type[BaseIOSchema]) -> BaseIOSchema:
    """Run the tool with the given parameters."""
    return tool.run(params)
  return Thunk(_as_thunk)

def enable_tool(tool: BaseTool) -> Thunk[HasTools, HasTools]:
  """Enable a tool in the context."""
  @thunk
  async def _enable(ctx) -> HasTools:
    """Enable the tool in the context."""
    ctx.tools[tool.tool_name] = tool
    if isinstance(tool, HasGetInfo):
      from goldentooth_agent.core.system_prompt import DynamicContextProvider, enable_context_provider
      dcp = DynamicContextProvider(title=tool.tool_name, fn=tool.get_info)
      ctx = await enable_context_provider(dcp)(ctx)
    return ctx # type: ignore
  return _enable

def disable_tool(tool: BaseTool) -> Thunk[HasTools, HasTools]:
  """Disable a tool in the context."""
  @thunk
  async def _disable(ctx) -> HasTools:
    """Disable the tool in the context."""
    if tool.tool_name in ctx.tools:
      del ctx.tools[tool.tool_name]
    if isinstance(tool, HasGetInfo):
      from goldentooth_agent.core.system_prompt import disable_context_provider
      ctx = await disable_context_provider(tool.tool_name)(ctx)
    return ctx # type: ignore
  return _disable
