from atomic_agents.lib.components.system_prompt_generator import SystemPromptGenerator
from goldentooth_agent.core.context import context_key

SYSTEM_PROMPT_GENERATOR_KEY = context_key(
    "system_prompt_generator", SystemPromptGenerator
)
