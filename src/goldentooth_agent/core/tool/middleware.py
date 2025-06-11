from __future__ import annotations
from antidote import inject
from atomic_agents.lib.base.base_io_schema import BaseIOSchema
from atomic_agents.lib.base.base_tool import BaseTool
from goldentooth_agent.core.pipeline import Middleware, NextMiddleware, Pipeline
from goldentooth_agent.core.thunk import Thunk
from .registry import ToolRegistry
from .base import ToolBase

def run_tool_th(tool: BaseTool) -> Thunk[BaseIOSchema, BaseIOSchema]:
  """Generator for thunk to print a message to the console."""
  async def _thunk(input: BaseIOSchema) -> BaseIOSchema:
    """Thunk to run a tool and return the appropriate result."""
    if not isinstance(input, tool.input_schema):
      raise TypeError(f"Input must be of type {tool.input_schema.__name__}, got {type(input).__name__}")
    result = tool.run(type(input))
    if not isinstance(result, tool.output_schema):
      raise TypeError(f"Output must be of type {tool.output_schema.__name__}, got {type(result).__name__}")
    return result
  return Thunk(_thunk)

def register_tool_mw(tool_class: type[BaseTool]) -> Middleware[ToolRegistry]:
  """Middleware to register a tool in the ToolRegistry."""
  async def _middleware(
    registry: ToolRegistry,
    next_middleware: NextMiddleware,
    tool: BaseTool = inject[tool_class],
  ) -> None:
    """Register the tool class in the ToolRegistry."""
    registry.register(tool)
    await next_middleware()
  return Middleware(_middleware)

def tool_registry_pl() -> Pipeline[ToolRegistry]:
  """Pipeline to create a ToolRegistry and register all tools."""
  pipeline = Pipeline()
  return pipeline

def tool_registry_th(tools: list[type[ToolBase]], registry: ToolRegistry = inject[ToolRegistry]) -> Thunk[object, None]:
  """Thunk to create a ToolRegistry and register all tools."""
  @inject
  async def _thunk(_nil) -> None:
    """Register all tools in the ToolRegistry."""
    pipeline = tool_registry_pl()
    for tool_class in tools:
      pipeline.use(register_tool_mw(tool_class))
    await pipeline.run(registry)
    return None
  return Thunk(_thunk)
