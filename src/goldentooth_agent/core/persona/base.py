from __future__ import annotations
from antidote import inject
from atomic_agents.lib.components.system_prompt_generator import SystemPromptGenerator, SystemPromptContextProviderBase
from goldentooth_agent.core.context_provider import ContextProviderRegistry
from goldentooth_agent.core.logging import get_logger
from goldentooth_agent.core.system_prompt import SystemPromptRegistry
from goldentooth_agent.core.tool import ToolRegistry
from logging import Logger

class Persona:
  """Base class for all personas in the GoldenTooth Agent system."""

  @inject
  def __init__(
    self,
    name: str,
    system_prompt_id: str,
    context_provider_id: str,
    tool_ids: list[str],
    logger: Logger = inject[get_logger(__name__)],
  ) -> None:
    """Initialize the persona with system prompt, context provider, and tools."""
    logger.debug(f"Initializing Persona: {name} with system prompt {system_prompt_id}, context provider {context_provider_id}, and tools {tool_ids}")
    self.name = name
    self.system_prompt_id = system_prompt_id
    self.context_provider_id = context_provider_id
    self.tool_ids = tool_ids

  @inject
  def get_system_prompt(
    self,
    system_prompt_registry: SystemPromptRegistry = inject.me(),
    context_provider_registry: ContextProviderRegistry = inject.me(),
    tool_registry: ToolRegistry = inject.me(),
    logger: Logger = inject[get_logger(__name__)],
  ) -> SystemPromptGenerator:
    """Retrieve the system prompt for this persona."""
    logger.debug(f"Retrieving system prompt for Persona: {self.name}")
    system_prompt_generator = system_prompt_registry.get(self.system_prompt_id)
    context_provider = context_provider_registry.get(self.context_provider_id)
    tools = [tool_registry.get(tool_id) for tool_id in self.tool_ids]
    system_prompt_generator.context_providers[self.context_provider_id] = context_provider
    for tool in tools:
      logger.debug(f"Adding tool '{tool.tool_name}' to system prompt generator")
      if isinstance(tool, SystemPromptContextProviderBase):
        system_prompt_generator.context_providers[tool.tool_name] = tool
    return system_prompt_generator
