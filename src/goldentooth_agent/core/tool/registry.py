from __future__ import annotations
from typing import List, Dict
from antidote import inject, injectable
from atomic_agents.lib.base.base_tool import BaseTool
from atomic_agents.lib.base.base_io_schema import BaseIOSchema
from goldentooth_agent.core.thunk import Thunk

@injectable
class ToolRegistry:
  """Registry for managing tools."""

  def __init__(self):
    """Initialize the tool registry."""
    self.registry: Dict[str, BaseTool] = {}

  @inject.method
  def register(self, tool: BaseTool) -> None:
    """Register a tool in the registry."""
    self.registry[tool.tool_name] = tool

  @inject.method
  def get(self, tool_name: str) -> BaseTool:
    """Retrieve a tool by its name."""
    return self.registry[tool_name]

  @inject.method
  def keys(self) -> List[str]:
    """Get all registered tool names."""
    return list(self.registry.keys())

  @inject.method
  def items(self) -> List[tuple[str, BaseTool]]:
    """Get all registered tools as (name, tool) pairs."""
    return list(self.registry.items())

  @inject.method
  def all(self) -> List[BaseTool]:
    """Get all registered tools."""
    return list(self.registry.values())

  @inject.method
  def get_thunk(self, tool_name: str) -> Thunk[type[BaseIOSchema], BaseIOSchema]:
    """Get a thunk for a tool by its name."""
    from .thunk import thunkify_tool
    tool = self.get(tool_name)
    return thunkify_tool(tool)

  @inject.method
  def get_by_input_schema(self, schema: type[BaseIOSchema]) -> BaseTool:
    """Get a tool by its input schema."""
    for tool in self.all():
      if issubclass(schema, tool.input_schema):
        return tool
    raise LookupError(f"No tool found for input schema: {schema}")

@inject
def register_tool(registry: ToolRegistry = inject.me()):
  """Decorator to register a tool in the ToolRegistry."""
  def decorator(tool_cls: type[BaseTool]):
    """Decorator to register a tool class."""
    from antidote import world
    instance = world[tool_cls]
    registry.register(instance)
    return tool_cls
  return decorator
