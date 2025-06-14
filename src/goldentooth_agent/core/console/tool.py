from __future__ import annotations
from antidote import injectable, inject
from atomic_agents.lib.base.base_io_schema import BaseIOSchema
from atomic_agents.lib.base.base_tool import BaseToolConfig, BaseTool
from atomic_agents.lib.components.system_prompt_generator import SystemPromptContextProviderBase
from pydantic import Field
from rich.console import Console
from typing import Optional
from goldentooth_agent.core.tool.registry import register_tool
from .inject import get_console

class ConsoleInput(BaseIOSchema):
  """Schema for the input to the Console tool."""
  prompt: str = Field(..., description="The prompt to display to the user. For example, 'Please enter your name:'.")
  style: Optional[str] = Field(..., description="The (optional) style to apply to the prompt. For example, 'bold blue', 'italic green', etc.")

class ConsoleOutput(BaseIOSchema):
  """Schema for the output from the Console tool."""
  input: str = Field(..., description="The user's input. For example, 'John Doe'.")

class ConsoleConfig(BaseToolConfig):
  """Configuration for the Console tool."""
  pass

@injectable
class ConsoleContextProvider(SystemPromptContextProviderBase):
  """Context provider for the console tool."""

  def __init__(self):
    super().__init__("Console")

  def get_info(self) -> str:
    return "\n".join([
      "Use the Console tool to prompt the user for input.",
      "This tool displays a prompt to the user and waits for their input.",
      "You can specify the prompt text and the style (Python 'rich' package) to apply to the prompt.",
    ])

@register_tool()
@injectable(factory_method='create')
class ConsoleTool(BaseTool):
  """Console tool that prompts the user for input and returns their response."""
  input_schema = ConsoleInput
  output_schema = ConsoleOutput

  def __init__(self, config: ConsoleConfig = ConsoleConfig()):
    """Initialize the Console tool."""
    super().__init__(config)

  @classmethod
  def create(cls) -> ConsoleTool:
    """Create an instance of this tool."""
    return cls()

  @inject
  def run(self, params: ConsoleInput, console: Console = inject[get_console()]) -> ConsoleOutput: # type: ignore[override]
    """Run the Console tool and return the user's input."""
    input = console.input(f"\n[{params.style}]{params.prompt}[/{params.style}] " if params.style else f"\n{params.prompt} ")
    return ConsoleOutput(input=input)

if __name__ == "__main__":
    # Example usage
    from antidote import world
    console_tool = world[ConsoleTool]
    console_input = ConsoleInput(prompt="What is your name?", style="bold blue")
    console_output = console_tool.run(console_input) # type: ignore[call-arg]
    print(f"You entered: {console_output.input}") # type: ignore[no-untyped-call]
