from __future__ import annotations
from antidote import injectable, inject
from atomic_agents.lib.base.base_io_schema import BaseIOSchema
from atomic_agents.lib.base.base_tool import BaseToolConfig, BaseTool
from goldentooth_agent.core.console import get_console
from goldentooth_agent.core.tool.registry import register_tool
from goldentooth_agent.core.logging import get_logger
from logging import Logger
from pydantic import Field
from rich.console import Console
from typing import Any

class DisplayInput(BaseIOSchema):
  """Schema for the input to the Display tool."""
  output: Any = Field(..., description="The output to display to the user. For example, 'Hello, World!'.")

class DisplayOutput(BaseIOSchema):
  """Schema for the output from the Display tool."""

class DisplayConfig(BaseToolConfig):
  """Configuration for the Display tool."""
  pass

@register_tool()
@injectable(factory_method='create')
class DisplayTool(BaseTool):
  """Console tool that displays content to the user."""
  input_schema = DisplayInput
  output_schema = DisplayOutput

  def __init__(self, config: DisplayConfig = DisplayConfig(title="tools.display", description="Displays some output to the user.")):
    """Initialize the Display tool."""
    super().__init__(config)

  @classmethod
  def create(cls) -> DisplayTool:
    """Create an instance of this tool."""
    return cls()

  @inject
  def run(self, params: DisplayInput, console: Console = inject[get_console()], logger: Logger = inject[get_logger(__name__)]) -> DisplayOutput: # type: ignore[override]
    """Run the Display tool and return the user's input."""
    logger.debug("Running Display tool with output: %s", params.output)
    console.print(params.output)
    return DisplayOutput()

  def get_info(self) -> str:
    return "\n".join([
      "Use the Display tool to display text to the user.",
    ])

if __name__ == "__main__":
  # Example usage
  from antidote import world
  display_tool = world[DisplayTool]
  display_request = DisplayInput(output="Hello, World!")
  display_response = display_tool.run(display_request) # type: ignore[call-arg]
  print(f"You entered: {display_response}") # type: ignore[no-untyped-call]
