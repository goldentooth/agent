from __future__ import annotations
from antidote import inject
from atomic_agents.lib.components.system_prompt_generator import SystemPromptGenerator, SystemPromptContextProviderBase
from goldentooth_agent.core.context_provider import ContextProviderRegistry
from goldentooth_agent.core.logging import get_logger
from goldentooth_agent.core.system_prompt import SystemPromptRegistry
from goldentooth_agent.core.tool import ToolRegistry
from logging import Logger

class Role:
  """Base class for all roles in the GoldenTooth Agent system."""

  @inject
  def __init__(
    self,
    id: str,
    name: str,
    system_prompt_id: str,
    context_provider_ids: list[str],
    tool_ids: list[str],
    logger: Logger = inject[get_logger(__name__)],
  ) -> None:
    """Initialize the role with context providers and tools."""
    logger.debug(f"Initializing Role: {id} with name {name}, system prompt ID {system_prompt_id}, context providers {context_provider_ids}, and tools {tool_ids}")
    self.id = id
    self.name = name
    self.system_prompt_id = system_prompt_id
    self.context_provider_ids = context_provider_ids
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
    for cp_id in self.context_provider_ids:
      logger.debug(f"Adding context provider '{cp_id}' to system prompt generator")
      context_provider = context_provider_registry.get(cp_id)
      system_prompt_generator.context_providers[cp_id] = context_provider
    for tool_id in self.tool_ids:
      logger.debug(f"Adding tool '{tool_id}' to system prompt generator")
      tool = tool_registry.get(tool_id)
      if isinstance(tool, SystemPromptContextProviderBase):
        system_prompt_generator.context_providers[tool_id] = tool
    return system_prompt_generator
