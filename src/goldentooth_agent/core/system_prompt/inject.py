from antidote import inject, lazy
from atomic_agents.lib.components.system_prompt_generator import SystemPromptGenerator
from goldentooth_agent.core.static_system_prompt import StaticSystemPromptRegistry

@lazy
def get_system_prompt_generator(registry: StaticSystemPromptRegistry = inject.me()) -> SystemPromptGenerator:
  """Returns the system prompt generator."""
  return registry.get_default()
