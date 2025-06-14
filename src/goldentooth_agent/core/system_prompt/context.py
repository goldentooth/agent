from typing import Protocol, runtime_checkable
from atomic_agents.lib.components.system_prompt_generator import SystemPromptGenerator

@runtime_checkable
class HasSystemPromptGenerator(Protocol):
  """Protocol for objects that have a system prompt generator defined in them."""

  system_prompt_generator: SystemPromptGenerator
