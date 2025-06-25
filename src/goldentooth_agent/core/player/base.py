from __future__ import annotations
from antidote import inject
from atomic_agents.lib.components.system_prompt_generator import SystemPromptGenerator
from goldentooth_agent.core.logging import get_logger
from goldentooth_agent.core.persona import PersonaRegistry
from goldentooth_agent.core.role import RoleRegistry
from logging import Logger

class Player:
  """Base class for a (role, persona) tuple in the Goldentooth Agent."""

  @inject
  def __init__(
    self,
    role_id: str,
    persona_id: str,
    logger: Logger = inject[get_logger(__name__)],
  ) -> None:
    """Initialize the player with context providers."""
    logger.debug(f"Initializing Player: ({role_id}, {persona_id})")
    self.role_id = role_id
    self.persona_id = persona_id

  @inject
  def get_system_prompt(
    self,
    role_registry: RoleRegistry = inject.me(),
    persona_registry: PersonaRegistry = inject.me(),
    logger: Logger = inject[get_logger(__name__)],
  ) -> SystemPromptGenerator:
    """Retrieve the system prompt for this persona."""
    logger.debug(f"Retrieving system prompt for Player: ({self.role_id}, {self.persona_id})")
    system_prompt_generator = role_registry.get(self.role_id).get_system_prompt()
    persona = persona_registry.get(self.persona_id)
    persona.visit_generator(system_prompt_generator)
    return system_prompt_generator
