from __future__ import annotations
from atomic_agents.lib.base.base_io_schema import BaseIOSchema
from atomic_agents.agents.base_agent import BaseAgentOutputSchema
from rich.console import RenderableType, Group
from typing import Any, Optional, Protocol, runtime_checkable
from .tool import DisplayInput

@runtime_checkable
class DisplayInputConvertible(Protocol):
  """Protocol for objects that can be converted to a DisplayInput."""

  def as_display_input(self) -> DisplayInput:
    """Convert the object to a DisplayInput."""
    ...

class DisplayInputAdapter(DisplayInputConvertible):
  """Adapter class to convert a BaseIOSchema to a DisplayInput."""

  def __init__(self, schema: BaseIOSchema, prefix: Optional[Any] = None) -> None:
    """Initialize the adapter with a schema and an optional prefix."""
    self.prefix = prefix
    self.schema = schema

  def as_display_input(self) -> DisplayInput:
    """Convert the schema to a DisplayInput."""
    renderables: list[RenderableType] = []
    if self.prefix:
      renderables.append(self.prefix)
    if isinstance(self.schema, BaseAgentOutputSchema):
      renderables.append(self.schema.chat_message)
    output = Group(*renderables)
    return DisplayInput(output=output)
