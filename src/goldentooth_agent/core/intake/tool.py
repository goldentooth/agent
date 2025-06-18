from __future__ import annotations
from antidote import injectable, inject
from atomic_agents.agents.base_agent import BaseAgentInputSchema
from atomic_agents.lib.base.base_io_schema import BaseIOSchema
from atomic_agents.lib.base.base_tool import BaseToolConfig, BaseTool
from goldentooth_agent.core.command import CommandInput
from goldentooth_agent.core.console import get_console
from goldentooth_agent.core.tool.registry import register_tool
from pydantic import Field
from rich.console import Console
from typing import Optional

class IntakeInput(BaseIOSchema):
  """Schema for the input to the Intake tool."""
  prompt: str = Field(..., description="The prompt to display to the user. For example, 'Please enter your name:'.")
  style: Optional[str] = Field(..., description="The (optional) style to apply to the prompt. For example, 'bold blue', 'italic green', etc.")

class IntakeOutput(BaseIOSchema):
  """Schema for the output from the Intake tool."""
  string: str = Field(..., description="The user's input. For example, 'John Doe'.")

  def as_agent_input(self) -> BaseAgentInputSchema:
    """Convert this output to a BaseAgentInputSchema."""
    return BaseAgentInputSchema(chat_message=self.string)

  def as_command_input(self) -> CommandInput:
    """Convert this output to a CommandInput."""
    from goldentooth_agent.core.command.tool import CommandInput
    return CommandInput(input=self.string)

class IntakeConfig(BaseToolConfig):
  """Configuration for the Console tool."""
  pass

@register_tool()
@injectable(factory_method='create')
class IntakeTool(BaseTool):
  """Console tool that prompts the user for input and returns their response."""
  input_schema = IntakeInput
  output_schema = IntakeOutput

  def __init__(self, config: IntakeConfig = IntakeConfig(title="tools.intake", description="Prompts the user for input via the console.")):
    """Initialize the Console tool."""
    super().__init__(config)

  @classmethod
  def create(cls) -> IntakeTool:
    """Create an instance of this tool."""
    return cls()

  @inject
  def run(self, params: IntakeInput, console: Console = inject[get_console()]) -> IntakeOutput: # type: ignore[override]
    """Run the Console tool and return the user's input."""
    string = console.input(f"\n[{params.style}]{params.prompt}[/{params.style}] " if params.style else f"\n{params.prompt} ")
    return IntakeOutput(string=string)

  def get_info(self) -> str:
    return "\n".join([
      "Use the Intake tool to prompt the user for input.",
      "This tool displays a prompt to the user and waits for their input.",
      "You can specify the prompt text (e.g. 'You: ') and the style (Python 'rich' package) to apply to the prompt.",
    ])

if __name__ == "__main__":
  # Example usage
  from antidote import world
  intake_tool = world[IntakeTool]
  intake_request = IntakeInput(prompt="What is your name?", style="bold blue")
  intake_response = intake_tool.run(intake_request) # type: ignore[call-arg]
  print(f"You entered: {intake_response.string}") # type: ignore[no-untyped-call]
