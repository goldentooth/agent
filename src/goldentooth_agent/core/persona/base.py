from __future__ import annotations
from antidote import inject
from atomic_agents.lib.components.system_prompt_generator import (
    SystemPromptGenerator,
    SystemPromptContextProviderBase,
)
from goldentooth_agent.core.context_provider import ContextProviderRegistry
from goldentooth_agent.core.logging import get_logger


class Persona:
    """Base class for all personas in the GoldenTooth Agent system."""

    @inject
    def __init__(
        self,
        id: str,
        name: str,
        color: str,
        context_provider_ids: list[str],
        logger=inject[get_logger(__name__)],
    ) -> None:
        """Initialize the persona with context providers."""
        logger.debug(
            f"Initializing Persona: {name} with context providers {context_provider_ids}"
        )
        self.id = id
        self.name = name
        self.color = color
        self.context_provider_ids = context_provider_ids

    @inject
    def visit_generator(
        self,
        system_prompt_generator: SystemPromptGenerator,
        context_provider_registry: ContextProviderRegistry = inject.me(),
        logger=inject[get_logger(__name__)],
    ) -> None:
        """Modify the system prompt generator to include this role's context providers."""
        logger.debug(f"Visiting generator for Role: {self.name}")
        for cp_id in self.context_provider_ids:
            logger.debug(
                f"Adding context provider '{cp_id}' to system prompt generator"
            )
            context_provider = context_provider_registry.get(cp_id)
            system_prompt_generator.context_providers[cp_id] = context_provider

    @inject
    def unvisit_generator(
        self,
        system_prompt_generator: SystemPromptGenerator,
        logger=inject[get_logger(__name__)],
    ) -> None:
        """Remove this role's context providers and tools from the system prompt generator."""
        logger.debug(f"Unvisiting generator for Role: {self.name}")
        for cp_id in self.context_provider_ids:
            logger.debug(
                f"Removing context provider '{cp_id}' from system prompt generator"
            )
            if cp_id in system_prompt_generator.context_providers:
                logger.debug(
                    f"Removing context provider '{cp_id}' from system prompt generator"
                )
                del system_prompt_generator.context_providers[cp_id]
