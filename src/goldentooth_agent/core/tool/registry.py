from __future__ import annotations
from typing import List, Dict
from antidote import inject, injectable
from atomic_agents.lib.base.base_tool import BaseTool

@injectable
class ToolRegistry:
  """Registry for managing tools."""

  def __init__(self):
    """Initialize the tool registry."""
    self.registry: Dict[str, BaseTool] = {}

  @inject.method
  def register(self, tool: BaseTool) -> None:
    """Register a tool in the registry."""
    print(f"Registering tool: {tool.tool_name}")
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
