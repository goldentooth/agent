from atomic_agents.lib.components.agent_memory import AgentMemory
from atomic_agents.agents.base_agent import BaseIOSchema
from atomic_agents.lib.components.system_prompt_generator import SystemPromptGenerator
from dataclasses import dataclass
from typing import Any, Type, Optional

@dataclass
class AgentConfig:
  """Configuration for the agent."""
  client: Any = None
  memory: AgentMemory = AgentMemory()
  model: str = "claude-sonnet-4-20250514"
  system_prompt_generator: Optional[SystemPromptGenerator] = None
  input_schema: Optional[Type[BaseIOSchema]] = None
  output_schema: Optional[Type[BaseIOSchema]] = None
  model_api_parameters: Optional[dict[str, Any]] = None

if __name__ == "__main__":
  # Example usage
  config = AgentConfig()
  print(config.model)  # Should print: claude-sonnet-4-20250514
  print(config.memory)  # Should print: AgentMemory instance
  print(config.system_prompt_generator)  # Should print: None
  print(config.input_schema)  # Should print: None
  print(config.output_schema)  # Should print: None
  print(config.model_api_parameters)  # Should print: None
  print(config)  # Should print the AgentConfig instance with default values
