from __future__ import annotations
from antidote import inject, injectable
from atomic_agents.agents.base_agent import BaseIOSchema
from atomic_agents.lib.base.base_tool import BaseToolConfig
from atomic_agents.lib.components.system_prompt_generator import SystemPromptContextProviderBase
from pydantic import Field
from .base import ToolBase

class ReverseToolInputSchema(BaseIOSchema):
  """Schema for the input to the Reverse tool."""
  string: str = Field(..., description="String to echo back. For example, 'Hello, World!'.")

class ReverseToolOutputSchema(BaseIOSchema):
  """Schema for the output from the Reverse tool."""
  result: str = Field(..., description="The reversed result. For example, '!dlroW ,olleH'.")

class ReverseToolConfig(BaseToolConfig):
  """Configuration for the Reverse tool."""
  pass

@injectable
class ReverseToolContextProvider(SystemPromptContextProviderBase):
  """Context provider for the Reverse tool."""

  @inject
  def __init__(self):
    super().__init__("Reverse")

  def get_info(self) -> str:
    return "Use the Reverse tool to return the input string reversed. This tool takes a string and returns it in reverse order, which can be useful for various text manipulation tasks."

@injectable(factory_method='create')
class ReverseTool(ToolBase):
  """Reverse tool that returns the reversed input string as output."""
  input_schema = ReverseToolInputSchema
  output_schema = ReverseToolOutputSchema

  @inject
  def __init__(self, config: ReverseToolConfig = ReverseToolConfig()):
    super().__init__(config)

  @classmethod
  def create(cls) -> ReverseTool:
    """Create an instance of this tool."""
    return cls()

  def run(self, params: ReverseToolInputSchema) -> ReverseToolOutputSchema: # type: ignore[attr-defined]
    return ReverseToolOutputSchema(result=''.join(params.string[::-1]))
