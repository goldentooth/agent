from __future__ import annotations
from antidote import inject
from atomic_agents.lib.base.base_io_schema import BaseIOSchema
from pydantic import Field, BaseModel
from rich.console import Console
from typing import Optional, Protocol, Type, runtime_checkable
from ..console import get_console
from ..pipeline import Middleware, NextMiddleware, middleware
from ..thunk import Thunk
from .base import SchemaBase

class InputSchema(SchemaBase):
  """Schema for input provided by the user to the Goldentooth Agent."""
  input: str = Field(..., description="The input provided by the user to the Goldentooth Agent.")

  @inject
  def print(self, console: Console = inject[get_console()]) -> None:
    """Print the schema in a pretty format using rich."""
    console.print(self.input)

  @classmethod
  def from_input(cls, user_input: str) -> InputSchema:
    """Create an InputSchema instance from user input."""
    return cls(input=user_input)

def wrap_input_th() -> Thunk[str, InputSchema]:
  async def _thunk(user_input: str) -> InputSchema:
    """Wrap user input in an InputSchema instance."""
    return InputSchema.from_input(user_input)
  return Thunk(_thunk)
