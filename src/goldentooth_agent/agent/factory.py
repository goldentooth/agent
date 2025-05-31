import instructor
import anthropic
from atomic_agents.agents.base_agent import BaseAgent
from atomic_agents.lib.components.agent_memory import AgentMemory
from ..context_provider import ContextProviderRegistry
from .config import AgentConfig
from ..initial_context import InitialContext
from ..system_prompt import SystemPromptFactory
from ..schemata import AgentOutputSchema, UserInputSchema
from atomic_agents.agents.base_agent import BaseIOSchema, BaseAgentConfig

DEFAULT_MODEL = "claude-sonnet-4-20250514"

class AgentFactory:
  """Creates agents based on pluggable components."""

  @staticmethod
  def create_base_agent(
    config: AgentConfig,
  ) -> BaseAgent:
    new_config = BaseAgentConfig(
      client=config.client or instructor.from_anthropic(anthropic.AsyncAnthropic()),
      memory=config.memory or AgentMemory(),
      model=config.model or DEFAULT_MODEL,
      system_prompt_generator=config.system_prompt_generator or SystemPromptFactory.get(InitialContext()),
      input_schema=config.input_schema or UserInputSchema,
      output_schema=config.output_schema or AgentOutputSchema,
      model_api_parameters=config.model_api_parameters or {"max_tokens": 2048},
    )
    return BaseAgent(config=new_config)

  @staticmethod
  def default_base_agent() -> BaseAgent:
    """Create a default agent with the default model."""
    config = AgentConfig()
    config.client = instructor.from_anthropic(anthropic.AsyncAnthropic())
    config.model = DEFAULT_MODEL
    config.system_prompt_generator = SystemPromptFactory.get(InitialContext())
    config.input_schema = UserInputSchema
    config.output_schema = AgentOutputSchema
    config.model_api_parameters = {"max_tokens": 2048}
    return AgentFactory.create_base_agent(config)

if __name__ == "__main__":
  agent = AgentFactory.default_base_agent()

  print("Agent created with model:", agent.model)
  print("Input schema:", agent.input_schema)
  print("Output schema:", agent.output_schema)
  print("System prompt generator:", agent.system_prompt_generator)
  print("Context providers registered:", ContextProviderRegistry.keys())
