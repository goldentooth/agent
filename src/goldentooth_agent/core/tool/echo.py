from __future__ import annotations
from antidote import injectable, inject
from atomic_agents.lib.base.base_io_schema import BaseIOSchema
from atomic_agents.lib.base.base_tool import BaseToolConfig
from atomic_agents.lib.components.system_prompt_generator import SystemPromptContextProviderBase
from pydantic import Field
from .base import ToolBase

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

  @inject
  def __init__(self):
    super().__init__("Echo")

  def get_info(self) -> str:
    return "Use the Echo tool to return the input string as output. This tool simply echoes back the input string without any modifications."

@injectable(factory_method='create')
class EchoTool(ToolBase):
  """Echo tool that returns the input string as output."""
  input_schema = EchoToolInputSchema
  output_schema = EchoToolOutputSchema

  @inject
  def __init__(self, config: EchoToolConfig = EchoToolConfig()):
    super().__init__(config)

  @classmethod
  def create(cls) -> EchoTool:
    """Create an instance of this tool."""
    return cls()

  def run(self, params: EchoToolInputSchema) -> EchoToolOutputSchema: # type: ignore[attr-defined]
    print(f"Running EchoTool with input: {params.string}")
    return EchoToolOutputSchema(result=params.string)
