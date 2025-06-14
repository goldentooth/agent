from __future__ import annotations
from antidote import injectable
from atomic_agents.agents.base_agent import BaseIOSchema
from atomic_agents.lib.base.base_tool import BaseTool, BaseToolConfig
from atomic_agents.lib.components.system_prompt_generator import SystemPromptContextProviderBase
from pydantic import Field
from .registry import register_tool

class ReverseInput(BaseIOSchema):
  """Schema for the input to the Reverse tool."""
  string: str = Field(..., description="String to echo back. For example, 'Hello, World!'.")

class ReverseOutput(BaseIOSchema):
  """Schema for the output from the Reverse tool."""
  result: str = Field(..., description="The reversed result. For example, '!dlroW ,olleH'.")

class ReverseConfig(BaseToolConfig):
  """Configuration for the Reverse tool."""
  pass

@register_tool()
@injectable(factory_method='create')
class ReverseTool(BaseTool, SystemPromptContextProviderBase):
  """Reverse tool that returns the reversed input string as output."""
  input_schema = ReverseInput
  output_schema = ReverseOutput

  def __init__(self, config: ReverseConfig = ReverseConfig()):
    super().__init__(config)

  @classmethod
  def create(cls) -> ReverseTool:
    """Create an instance of this tool."""
    return cls()

  def run(self, params: ReverseInput) -> ReverseOutput: # type: ignore[attr-defined]
    return ReverseOutput(result=''.join(params.string[::-1]))

  def get_info(self) -> str:
    return "\n".join([
      "Use the Reverse tool to return the input string reversed.",
      "This tool takes a string and returns it in reverse order, which can be useful for various text manipulation tasks.",
    ])

if __name__ == "__main__":
  # Example usage
  from antidote import world
  tool = world[ReverseTool]
  input_data = ReverseInput(string="Hello, World!")
  output_data = tool.run(input_data) # type: ignore[call-arg]
  print(output_data.model_dump_json(indent=2))
  print("ReverseTool created and run successfully.")
