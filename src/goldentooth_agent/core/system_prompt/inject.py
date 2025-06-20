from antidote import inject, lazy
from atomic_agents.lib.components.system_prompt_generator import SystemPromptGenerator
from .registry import SystemPromptRegistry

@lazy
@inject
def get_system_prompt_generator(registry: SystemPromptRegistry = inject.me()) -> SystemPromptGenerator:
  """Returns the system prompt generator."""
  return registry.get_default()
