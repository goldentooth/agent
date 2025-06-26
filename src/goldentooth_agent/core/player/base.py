from __future__ import annotations
from antidote import inject
from atomic_agents.agents.base_agent import BaseAgent
from atomic_agents.lib.components.system_prompt_generator import SystemPromptGenerator
from goldentooth_agent.core.agent import AgentRegistry
from goldentooth_agent.core.logging import get_logger
from goldentooth_agent.core.persona import PersonaRegistry
from goldentooth_agent.core.role import RoleRegistry

from rich.text import Text
from .label import PlayerLabel


class Player:
    """Base class for a (role, persona) tuple in the Goldentooth Agent."""

    @inject
    def __init__(
        self,
        id: str,
        name: str,
        role_id: str,
        persona_id: str,
        agent_id: str,
        label: PlayerLabel,
        logger=inject[get_logger(__name__)],
    ) -> None:
        """Initialize the player with context providers."""
        logger.debug(f"Initializing Player: ({role_id}, {persona_id})")
        self.id = id
        self.name = name
        self.role_id = role_id
        self.persona_id = persona_id
        self.agent_id = agent_id
        self.label = label

    @inject
    def get_system_prompt(
        self,
        role_registry: RoleRegistry = inject.me(),
        persona_registry: PersonaRegistry = inject.me(),
        logger=inject[get_logger(__name__)],
    ) -> SystemPromptGenerator:
        """Retrieve the system prompt for this persona."""
        logger.debug(
            f"Retrieving system prompt for Player: ({self.role_id}, {self.persona_id})"
        )
        system_prompt_generator = role_registry.get(self.role_id).get_system_prompt()
        persona = persona_registry.get(self.persona_id)
        persona.visit_generator(system_prompt_generator)
        return system_prompt_generator

    @inject
    def get_agent(self, agent_registry: AgentRegistry = inject.me()) -> BaseAgent:
        """Get the agent associated with this player."""
        logger = inject[get_logger(__name__)]
        logger.debug(
            f"Retrieving agent for Player: ({self.role_id}, {self.persona_id})"
        )
        return agent_registry.get(self.agent_id)

    def get_label_renderable(self) -> Text:
        """Get the label renderable for this player."""
        return self.label.get_renderable()
