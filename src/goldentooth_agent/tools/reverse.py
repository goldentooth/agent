from pydantic import Field
from typing import List
from goldentooth_agent.tool import ToolBase, ToolMetadata
from atomic_agents.agents.base_agent import BaseIOSchema
from atomic_agents.lib.base.base_tool import BaseToolConfig

class ReverseToolInputSchema(BaseIOSchema):
  """Schema for the input to the Reverse tool."""
  string: str = Field(..., description="String to echo back. For example, 'Hello, World!'.")

class ReverseToolOutputSchema(BaseIOSchema):
  """Schema for the output from the Reverse tool."""
  result: str = Field(..., description="The reversed result. For example, '!dlroW ,olleH'.")

class ReverseToolConfig(BaseToolConfig):
  """Configuration for the Reverse tool."""
  pass

class ReverseToolMetadata(ToolMetadata):
  """Metadata for the Reverse tool."""
  name: str = "Reverse"
  instructions: List[str] = [
    "This tool reverses the input string.",
    "You can use it to test string manipulation functionality.",
    "Provide a string in the 'string' field to see it reversed."
  ]

class ReverseTool(ToolBase):
  """Reverse tool that returns the reversed input string as output."""
  config_class = ReverseToolConfig
  metadata_class = ReverseToolMetadata
  input_schema = ReverseToolInputSchema
  output_schema = ReverseToolOutputSchema

  def __init__(self, config: ReverseToolConfig = ReverseToolConfig()):
    super().__init__(config)

  def run(self, params: ReverseToolInputSchema) -> ReverseToolOutputSchema: # type: ignore[attr-defined]
    return ReverseToolOutputSchema(result=''.join(params.string[::-1]))

if __name__ == "__main__":
  # Example usage
  tool = ReverseTool()
  input_data = ReverseToolInputSchema(string="Hello, World!")
  output_data = tool.run(input_data)
  print(output_data.result)  # Should print: !dlroW ,olleH
  print(f"Tool name: {tool.metadata_class.name}")
  print(f"Tool instructions: {tool.metadata_class.instructions}")