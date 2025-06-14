from __future__ import annotations
from antidote import inject
from atomic_agents.lib.base.base_io_schema import BaseIOSchema
from atomic_agents.lib.base.base_tool import BaseTool
from typing import Any
from goldentooth_agent.core.pipeline import Middleware, NextMiddleware, Pipeline
from goldentooth_agent.core.thunk import Thunk
from ...src.goldentooth_agent.core.tool.registry import ToolRegistry
from .base import ToolBase

def run_tool_th(tool: BaseTool) -> Thunk[BaseIOSchema, BaseIOSchema]:
  """Generator for thunk to run a tool."""
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
  @inject
  async def _middleware(
    registry: ToolRegistry,
    next_middleware: NextMiddleware,
    tool: BaseTool = inject[tool_class],
  ) -> None:
    """Register the tool class in the ToolRegistry."""
    registry.register(tool)
    await next_middleware()
  return Middleware(_middleware)

def tool_registry_pl(tools: list[type[ToolBase]]) -> Pipeline[ToolRegistry]:
  """Pipeline to create a ToolRegistry and register all tools."""
  pipeline = Pipeline()
  for tool_class in tools:
    pipeline.use(register_tool_mw(tool_class))
  return pipeline

def get_tool_registry_th() -> Thunk[Any, ToolRegistry]:
  """Thunk to get the ToolRegistry instance."""
  @inject
  async def _thunk(_nil, registry: ToolRegistry = inject.me()) -> ToolRegistry:
    """Return the ToolRegistry instance."""
    return registry
  return Thunk(_thunk)

def register_tools_th(tools: list[type[ToolBase]]) -> Thunk[ToolRegistry, ToolRegistry]:
  """Thunk to create a ToolRegistry and register all tools."""
  async def _thunk(registry: ToolRegistry) -> ToolRegistry:
    """Register all tools in the ToolRegistry."""
    for tool_class in tools:
      tool = tool_class.create()
      registry.register(tool)
    return registry
  return Thunk(_thunk)
