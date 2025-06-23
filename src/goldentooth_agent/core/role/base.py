from __future__ import annotations
from antidote import inject
from atomic_agents.lib.components.system_prompt_generator import SystemPromptGenerator, SystemPromptContextProviderBase
from goldentooth_agent.core.context_provider import ContextProviderRegistry
from goldentooth_agent.core.logging import get_logger
from goldentooth_agent.core.tool import ToolRegistry
from logging import Logger

class Role:
  """Base class for all roles in the GoldenTooth Agent system."""

  @inject
  def __init__(self, name: str, context_provider_ids: list[str], tool_ids: list[str], logger: Logger = inject[get_logger(__name__)]) -> None:
    """Initialize the role with context providers and tools."""
    logger.debug(f"Initializing Role: {name} with context providers {context_provider_ids} and tools {tool_ids}")
    self.name = name
    self.context_provider_ids = context_provider_ids
    self.tool_ids = tool_ids

  @inject
  def visit_generator(
    self,
    system_prompt_generator: SystemPromptGenerator = inject.me(),
    context_provider_registry: ContextProviderRegistry = inject.me(),
    tool_registry: ToolRegistry = inject.me(),
    logger: Logger = inject[get_logger(__name__)],
  ) -> None:
    """Modify the system prompt generator to include this role's context providers and tools."""
    logger.debug(f"Visiting generator for Role: {self.name}")
    for cp_id in self.context_provider_ids:
      logger.debug(f"Adding context provider '{cp_id}' to system prompt generator")
      context_provider = context_provider_registry.get(cp_id)
      system_prompt_generator.context_providers[cp_id] = context_provider
    for tool_id in self.tool_ids:
      logger.debug(f"Adding tool '{tool_id}' to system prompt generator")
      tool = tool_registry.get(tool_id)
      if isinstance(tool, SystemPromptContextProviderBase):
        system_prompt_generator.context_providers[tool_id] = tool

  @inject
  def unvisit_generator(
    self,
    system_prompt_generator: SystemPromptGenerator = inject.me(),
    logger: Logger = inject[get_logger(__name__)],
  ) -> None:
    """Remove this role's context providers and tools from the system prompt generator."""
    logger.debug(f"Unvisiting generator for Role: {self.name}")
    for cp_id in self.context_provider_ids:
      logger.debug(f"Removing context provider '{cp_id}' from system prompt generator")
      if cp_id in system_prompt_generator.context_providers:
        logger.debug(f"Removing context provider '{cp_id}' from system prompt generator")
        del system_prompt_generator.context_providers[cp_id]
    for tool_id in self.tool_ids:
      logger.debug(f"Removing tool '{tool_id}' from system prompt generator")
      if tool_id in system_prompt_generator.context_providers:
        logger.debug(f"Removing tool '{tool_id}' from system prompt generator")
        del system_prompt_generator.context_providers[tool_id]
