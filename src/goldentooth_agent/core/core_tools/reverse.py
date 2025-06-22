from __future__ import annotations
from antidote import injectable
from atomic_agents.agents.base_agent import BaseAgentInputSchema, BaseAgentOutputSchema
from atomic_agents.lib.base.base_tool import BaseTool, BaseToolConfig
from atomic_agents.lib.components.system_prompt_generator import SystemPromptContextProviderBase
from goldentooth_agent.core.tool.registry import register_tool

class ReverseConfig(BaseToolConfig):
  """Configuration for the Reverse tool."""
  pass

@register_tool()
@injectable(factory_method='create')
class ReverseTool(BaseTool, SystemPromptContextProviderBase):
  """Reverse tool that returns the reversed input string as output."""
  input_schema = BaseAgentInputSchema
  output_schema = BaseAgentOutputSchema

  def __init__(self, config: ReverseConfig = ReverseConfig(title="tools.reverse", description="Reverses the input string.")):
    super().__init__(config)

  @classmethod
  def create(cls) -> ReverseTool:
    """Create an instance of this tool."""
    return cls()

  def run(self, params: BaseAgentInputSchema) -> BaseAgentOutputSchema: # type: ignore[attr-defined]
    return BaseAgentOutputSchema(chat_message=''.join(params.chat_message[::-1]))

  def get_info(self) -> str:
    return "\n".join([
      "Use the Reverse tool to return the input string reversed.",
      "This tool takes a string and returns it in reverse order, which can be useful for various text manipulation tasks.",
    ])

if __name__ == "__main__":
  # Example usage
  from antidote import world
  tool = world[ReverseTool]
  input_data = BaseAgentInputSchema(chat_message="Hello, World!")
  output_data = tool.run(input_data) # type: ignore[call-arg]
  print(output_data.model_dump_json(indent=2))
  print("ReverseTool created and run successfully.")
