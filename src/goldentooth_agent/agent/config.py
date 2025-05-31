import instructor
import anthropic
from atomic_agents.lib.components.agent_memory import AgentMemory
from atomic_agents.agents.base_agent import BaseIOSchema, BaseAgentConfig
from atomic_agents.lib.components.system_prompt_generator import SystemPromptGenerator
from dataclasses import dataclass
from typing import Any, Type, Optional
from ..initial_context import InitialContext
from ..system_prompt import SystemPromptFactory
from ..schemata import AgentOutputSchema, UserInputSchema

DEFAULT_MODEL = "claude-sonnet-4-20250514"

@dataclass
class AgentConfig:
  """Configuration for the agent."""
  client: Any = None
  memory: AgentMemory = AgentMemory()
  model: str = DEFAULT_MODEL
  system_prompt_generator: SystemPromptGenerator = SystemPromptFactory.get(InitialContext())
  input_schema: Type[BaseIOSchema] = UserInputSchema
  output_schema: Type[BaseIOSchema] = AgentOutputSchema
  model_api_parameters: Optional[dict[str, Any]] = None

  def base_agent_config(self) -> BaseAgentConfig:
    """Return the base agent configuration."""
    return BaseAgentConfig(
      client=self.client or instructor.from_anthropic(anthropic.AsyncAnthropic()),
      memory=self.memory,
      model=self.model,
      system_prompt_generator=self.system_prompt_generator,
      model_api_parameters=self.model_api_parameters or {"max_tokens": 2048},
      input_schema=self.input_schema,
      output_schema=self.output_schema,
    )

if __name__ == "__main__":
  # Example usage
  config = AgentConfig()
  print(config.model)  # Should print: claude-sonnet-4-20250514
  print(config.client)  # Should print: None (or the actual client if set)
  print(config.memory)  # Should print: AgentMemory instance
  print(config.system_prompt_generator)  # Should print: SystemPromptGenerator instance
  print(config.input_schema)  # Should print: <class 'atomic_agents.agents.base_agent.BaseIOSchema'>
  print(config.output_schema)  # Should print: <class 'atomic_agents.agents.base_agent.BaseIOSchema'>
  print(config.model_api_parameters)  # Should print: {'max_tokens': 2048}
