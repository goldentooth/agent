from __future__ import annotations
from antidote import injectable, inject
from atomic_agents.lib.base.base_tool import BaseToolConfig
from atomic_agents.lib.components.system_prompt_generator import SystemPromptContextProviderBase
from pydantic import Field
from rich.console import Console
import typer
from typing import Any, Optional, Union
from .base import ToolBase
from goldentooth_agent.core.console import get_console
from goldentooth_agent.core.schema import SchemaBase, InputSchema
from goldentooth_agent.core.thunk import Thunk

class RequestUserInputToolInputSchema(SchemaBase):
  """Schema for the input to the Request User Input tool."""
  prompt: str = Field(..., description="The prompt to display to the user. For example, 'Please enter your name:'.")
  style: Optional[str] = Field(..., description="The (optional) style to apply to the prompt. For example, 'bold blue', 'italic green', etc.")

class RequestUserInputToolOutputSchema(SchemaBase):
  """Schema for the output from the Request User Input tool."""
  input: str = Field(..., description="The user's input. For example, 'John Doe'.")

class RequestUserInputToolQuitSchema(SchemaBase):
  """Schema for the output when the user quits the Request User Input tool."""

RequestUserInputFinalOutputSchema = Union[RequestUserInputToolOutputSchema, RequestUserInputToolQuitSchema]

class RequestUserInputToolConfig(BaseToolConfig):
  """Configuration for the Request User Input tool."""
  pass

@injectable
class RequestUserInputToolContextProvider(SystemPromptContextProviderBase):
  """Context provider for the Echo tool."""

  def __init__(self):
    super().__init__("Request User Input")

  def get_info(self) -> str:
    return "\n".join([
      "Use the Request User Input tool to prompt the user for input.",
      "This tool displays a prompt to the user and waits for their input.",
      "You can specify the prompt text and the style (Python 'rich' package) to apply to the prompt.",
    ])

@injectable(factory_method='create')
class RequestUserInputTool(ToolBase):
  """Request User Input tool that prompts the user for input and returns their response."""
  input_schema = RequestUserInputToolInputSchema
  output_schema = RequestUserInputToolOutputSchema

  def __init__(self, config: RequestUserInputToolConfig = RequestUserInputToolConfig()):
    """Initialize the Request User Input tool."""
    super().__init__(config)

  @classmethod
  def create(cls) -> RequestUserInputTool:
    """Create an instance of this tool."""
    return cls()

  @inject
  def run(self, params: RequestUserInputToolInputSchema, console: Console = inject[get_console()]) -> RequestUserInputFinalOutputSchema: # type: ignore[override]
    """Run the Request User Input tool and return the user's input."""
    input = console.input(f"\n[{params.style}]{params.prompt}[/{params.style}] " if params.style else f"\n{params.prompt} ")
    if input.lower() in ["/quit", "/exit"]:
      return RequestUserInputToolQuitSchema()
    return RequestUserInputToolOutputSchema(input=input)

def request_user_input_th(input_schema: RequestUserInputToolInputSchema = RequestUserInputToolInputSchema(prompt="You:", style="bold blue")) -> Thunk[Any, RequestUserInputToolOutputSchema]:
  """Thunk to run the Request User Input tool."""
  @inject
  async def _thunk(_nil, tool: RequestUserInputTool = inject.me()) -> RequestUserInputToolOutputSchema:
    """Run the Request User Input tool and return the user's input."""
    result = tool.run(params=input_schema)
    if isinstance(result, RequestUserInputToolQuitSchema):
      typer.Exit()
      return RequestUserInputToolOutputSchema(input="")  # Return empty input to indicate exit
    else:
      return result
  return Thunk(_thunk)

def read_user_input_th() -> Thunk[RequestUserInputToolOutputSchema, InputSchema]:
  """Thunk to read user input using the Request User Input tool."""

  async def _thunk(user_input: RequestUserInputToolOutputSchema) -> InputSchema:
    """Read user input and return it wrapped in an InputSchema."""
    return InputSchema.from_input(user_input.input)
  return Thunk(_thunk)
