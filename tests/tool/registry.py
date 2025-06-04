from __future__ import annotations
from typing import List, Dict, Type, TYPE_CHECKING
from atomic_agents.agents.base_agent import BaseIOSchema
if TYPE_CHECKING:
  from .base import ToolBase

class ToolRegistry:
  _registry: Dict[str, Type[ToolBase]] = {}

  @classmethod
  def register(cls, tool_cls) -> None:
    """Register a tool class in the registry."""
    print(f"Registering tool: {tool_cls.__name__}")
    name = tool_cls.metadata_class.get_name()
    if name in cls._registry:
      # raise ValueError(f"Duplicate tool name: {name}")
      pass
    cls._registry[name] = tool_cls
    return tool_cls

  @classmethod
  def get(cls, name) -> type | None:
    """Retrieve a tool class by its name."""
    return cls._registry.get(name)

  @classmethod
  def keys(cls) -> List[str]:
    """Get all registered tool names."""
    return list(cls._registry.keys())

  @classmethod
  def items(cls) -> List[tuple[str, type]]:
    """Get all registered tool classes as (name, class) pairs."""
    return list(cls._registry.items())

  @classmethod
  def all(cls) -> List[type]:
    """Get all registered tool classes."""
    return list(cls._registry.values())

  @classmethod
  def instructions(cls) -> str:
    """Get instructions for all registered tools."""
    return "\n".join(
      entry.metadata_class.get_instructions() for entry in cls._registry.values()
    )

  @classmethod
  def execute_tool(cls, name: str, params: BaseIOSchema) -> BaseIOSchema:
    """Execute a tool by its name with the given parameters."""
    print(f"Executing tool: {name} with params: {params}")
    entry = cls.get(name)
    if not entry:
      raise ValueError(f"Tool '{name}' not found in registry.")
    tool = entry(entry.config_class())
    return tool.run(params)
