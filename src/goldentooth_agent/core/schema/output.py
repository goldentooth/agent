from __future__ import annotations
from antidote import inject
from pydantic import Field
from rich.console import Console
from ..console import get_console
from ..thunk import Thunk
from .base import SchemaBase

class OutputSchema(SchemaBase):
  """Schema for output provided by the Goldentooth Agent to the user."""
  output: str = Field(..., description="The output text provided by the agent.")

  @inject
  def print(self, console: Console = inject[get_console()]) -> None:
    """Print the schema in a pretty format using rich."""
    console.print(self.output)

  @classmethod
  def from_output(cls, output: str) -> OutputSchema:
    """Create an OutputSchema instance from a string."""
    return cls(output=output)

def wrap_output_th() -> Thunk[str, OutputSchema]:
  async def _thunk(output: str) -> OutputSchema:
    """Wrap user input in an OutputSchema instance."""
    return OutputSchema.from_output(output)
  return Thunk(_thunk)
