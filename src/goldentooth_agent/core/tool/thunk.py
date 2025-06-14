from goldentooth_agent.core.dynamic_context_provider import DynamicContextProvider
from goldentooth_agent.core.system_prompt import HasSystemPromptGenerator, disable_context_provider, enable_context_provider
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
    return ctx
  return _enable

def enable_tool_context_provider(tool: BaseTool) -> Thunk[HasSystemPromptGenerator, HasSystemPromptGenerator]:
  """Enable a tool's context provider in the system prompt generator."""
  @thunk
  async def _enable(ctx) -> HasSystemPromptGenerator:
    """Enable the tool's context provider in the system prompt generator."""
    if isinstance(tool, HasGetInfo):
      dcp = DynamicContextProvider(title=tool.tool_name, fn=tool.get_info)
      ctx = await enable_context_provider(dcp)(ctx)
    return ctx
  return _enable

def disable_tool(tool: BaseTool) -> Thunk[HasTools, HasTools]:
  """Disable a tool in the context."""
  @thunk
  async def _disable(ctx) -> HasTools:
    """Disable the tool in the context."""
    if tool.tool_name in ctx.tools:
      del ctx.tools[tool.tool_name]
    return ctx
  return _disable

def disable_tool_context_provider(tool: BaseTool) -> Thunk[HasSystemPromptGenerator, HasSystemPromptGenerator]:
  """Disable a tool's context provider in the system prompt generator."""
  @thunk
  async def _disable(ctx) -> HasSystemPromptGenerator:
    """Disable the tool's context provider in the system prompt generator."""
    ctx = await disable_context_provider(tool.tool_name)(ctx)
    return ctx
  return _disable
