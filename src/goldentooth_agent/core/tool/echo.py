from __future__ import annotations
from antidote import injectable
from atomic_agents.lib.base.base_io_schema import BaseIOSchema
from atomic_agents.lib.base.base_tool import BaseToolConfig, BaseTool
from atomic_agents.lib.components.system_prompt_generator import SystemPromptContextProviderBase
from pydantic import Field
from .registry import register_tool

class EchoToolInputSchema(BaseIOSchema):
  """Schema for the input to the Echo tool."""
  string: str = Field(..., description="String to echo back. For example, 'Hello, World!'.")

class EchoToolOutputSchema(BaseIOSchema):
  """Schema for the output from the Echo tool."""
  result: str = Field(..., description="The echoed result. For example, 'Hello, World!'.")

class EchoToolConfig(BaseToolConfig):
  """Configuration for the Echo tool."""
  pass

@injectable
class EchoToolContextProvider(SystemPromptContextProviderBase):
  """Context provider for the Echo tool."""

  def __init__(self):
    super().__init__("Echo")

  def get_info(self) -> str:
    return "Use the Echo tool to return the input string as output. This tool simply echoes back the input string without any modifications."

@register_tool()
@injectable(factory_method='create')
class EchoTool(BaseTool):
  """Echo tool that returns the input string as output."""
  input_schema = EchoToolInputSchema
  output_schema = EchoToolOutputSchema

  def __init__(self, config: EchoToolConfig = EchoToolConfig()):
    super().__init__(config)

  @classmethod
  def create(cls) -> EchoTool:
    """Create an instance of this tool."""
    return cls()

  def run(self, params: EchoToolInputSchema) -> EchoToolOutputSchema: # type: ignore[attr-defined]
    print(f"Running EchoTool with input: {params.string}")
    return EchoToolOutputSchema(result=params.string)

if __name__ == "__main__":
  # Example usage
  from antidote import world
  tool = world[EchoTool]
  input_data = EchoToolInputSchema(string="Hello, World!")
  output_data = tool.run(input_data) # type: ignore[call-arg]
  print(output_data.model_dump_json(indent=2))
  print("EchoTool created and run successfully.")
