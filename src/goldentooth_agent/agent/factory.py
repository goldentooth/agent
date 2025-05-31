from atomic_agents.agents.base_agent import BaseAgent
from ..context_provider import ContextProviderRegistry
from .config import AgentConfig

class AgentFactory:
  """Creates agents based on pluggable components."""

  @staticmethod
  def create_base_agent(
    config: AgentConfig,
  ) -> BaseAgent:
    return BaseAgent(config=config.base_agent_config())

  @staticmethod
  def default_base_agent() -> BaseAgent:
    """Create a default agent with the default model."""
    config = AgentConfig()
    return AgentFactory.create_base_agent(config)

if __name__ == "__main__":
  agent = AgentFactory.default_base_agent()

  print("Agent created with model:", agent.model)
  print("Input schema:", agent.input_schema)
  print("Output schema:", agent.output_schema)
  print("System prompt generator:", agent.system_prompt_generator)
  print("Context providers registered:", ContextProviderRegistry.keys())
