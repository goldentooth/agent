from __future__ import annotations
from typing import List, Dict
from antidote import inject, injectable
from atomic_agents.lib.base.base_tool import BaseTool
from atomic_agents.lib.base.base_io_schema import BaseIOSchema
from goldentooth_agent.core.logging import get_logger
from logging import Logger
from goldentooth_agent.core.thunk import Thunk

@injectable(factory_method='create')
class ToolRegistry:
  """Registry for managing tools."""

  def __init__(self, logger: Logger = inject[get_logger(__name__)]) -> None:
    """Initialize the tool registry."""
    logger.debug("Initializing ToolRegistry")
    self.registry: Dict[str, BaseTool] = {}

  @classmethod
  def create(cls) -> ToolRegistry:
    """Create a new ToolRegistry instance."""
    return cls()

  @inject.method
  def register(self, tool: BaseTool, logger: Logger = inject[get_logger(__name__)]) -> None:
    """Register a tool in the registry."""
    logger.debug(f"Registering tool: {tool.tool_name}")
    self.registry[tool.tool_name] = tool

  @inject.method
  def get(self, tool_name: str, logger: Logger = inject[get_logger(__name__)]) -> BaseTool:
    """Retrieve a tool by its name."""
    logger.debug(f"Retrieving tool: {tool_name}")
    return self.registry[tool_name]

  @inject.method
  def keys(self, logger: Logger = inject[get_logger(__name__)]) -> List[str]:
    """Get all registered tool names."""
    logger.debug("Retrieving all tool names from registry")
    return list(self.registry.keys())

  @inject.method
  def items(self, logger: Logger = inject[get_logger(__name__)]) -> List[tuple[str, BaseTool]]:
    """Get all registered tools as (name, tool) pairs."""
    logger.debug("Retrieving all tool items from registry")
    return list(self.registry.items())

  @inject.method
  def all(self, logger: Logger = inject[get_logger(__name__)]) -> List[BaseTool]:
    """Get all registered tools."""
    logger.debug("Retrieving all tools from registry")
    return list(self.registry.values())

  @inject.method
  def get_thunk(self, tool_name: str, logger: Logger = inject[get_logger(__name__)]) -> Thunk[ BaseIOSchema, BaseIOSchema]:
    """Get a thunk for a tool by its name."""
    logger.debug(f"Creating thunk for tool: {tool_name}")
    from .thunk import thunkify_tool
    tool = self.get(tool_name)
    return thunkify_tool(tool)

  @inject.method
  def get_by_input_schema(self, schema: type[BaseIOSchema], logger: Logger = inject[get_logger(__name__)]) -> BaseTool:
    """Get a tool by its input schema."""
    logger.debug(f"Looking for tool with input schema: {schema}")
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
