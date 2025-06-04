from typing import List
from pydantic import Field
from ..tool import ToolBase, ToolMetadata
from atomic_agents.agents.base_agent import BaseIOSchema
from atomic_agents.lib.base.base_tool import BaseToolConfig

class EchoToolInputSchema(BaseIOSchema):
  """Schema for the input to the Echo tool."""
  string: str = Field(..., description="String to echo back. For example, 'Hello, World!'.")

class EchoToolOutputSchema(BaseIOSchema):
  """Schema for the output from the Echo tool."""
  result: str = Field(..., description="The echoed result. For example, 'Hello, World!'.")

class EchoToolConfig(BaseToolConfig):
  """Configuration for the Echo tool."""
  pass

class EchoToolMetadata(ToolMetadata):
  """Metadata for the Echo tool."""
  name: str = "Echo"
  instructions: List[str] = [
    "This tool echoes back the input string.",
    "You can use it to test the tool functionality.",
    "Provide a string in the 'string' field to see it echoed back."
  ]

class EchoTool(ToolBase):
  """Echo tool that returns the input string as output."""
  config_class = EchoToolConfig
  metadata_class = EchoToolMetadata
  input_schema = EchoToolInputSchema
  output_schema = EchoToolOutputSchema

  def __init__(self, config: EchoToolConfig = EchoToolConfig()):
    super().__init__(config)

  def run(self, params: EchoToolInputSchema) -> EchoToolOutputSchema: # type: ignore[attr-defined]
    print(f"Running EchoTool with input: {params.string}")
    return EchoToolOutputSchema(result=params.string)

if __name__ == "__main__":
  # Example usage
  tool = EchoTool()
  input_data = EchoToolInputSchema(string="Hello, World!")
  output_data = tool.run(input_data)
  print(output_data.result)  # Should print: Hello, World!
  print(f"Tool name: {tool.metadata_class.name}")
  print(f"Tool instructions: {tool.metadata_class.instructions}")
