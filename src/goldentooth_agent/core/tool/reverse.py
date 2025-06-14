from __future__ import annotations
from antidote import injectable
from atomic_agents.agents.base_agent import BaseIOSchema
from atomic_agents.lib.base.base_tool import BaseTool, BaseToolConfig
from atomic_agents.lib.components.system_prompt_generator import SystemPromptContextProviderBase
from pydantic import Field
from .registry import register_tool

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

  def __init__(self):
    super().__init__("Reverse")

  def get_info(self) -> str:
    return "Use the Reverse tool to return the input string reversed. This tool takes a string and returns it in reverse order, which can be useful for various text manipulation tasks."

@register_tool()
@injectable(factory_method='create')
class ReverseTool(BaseTool):
  """Reverse tool that returns the reversed input string as output."""
  input_schema = ReverseToolInputSchema
  output_schema = ReverseToolOutputSchema

  def __init__(self, config: ReverseToolConfig = ReverseToolConfig()):
    super().__init__(config)

  @classmethod
  def create(cls) -> ReverseTool:
    """Create an instance of this tool."""
    return cls()

  def run(self, params: ReverseToolInputSchema) -> ReverseToolOutputSchema: # type: ignore[attr-defined]
    return ReverseToolOutputSchema(result=''.join(params.string[::-1]))

if __name__ == "__main__":
  # Example usage
  from antidote import world
  tool = world[ReverseTool]
  input_data = ReverseToolInputSchema(string="Hello, World!")
  output_data = tool.run(input_data) # type: ignore[call-arg]
  print(output_data.model_dump_json(indent=2))
  print("ReverseTool created and run successfully.")
