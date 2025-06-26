from antidote import inject
from atomic_agents.lib.components.system_prompt_generator import (
    SystemPromptGenerator,
    SystemPromptContextProviderBase,
)
from goldentooth_agent.core.context import Context, context_autothunk
from goldentooth_agent.core.logging import get_logger
from goldentooth_agent.core.thunk import Thunk

from typing import Annotated
from .context import SYSTEM_PROMPT_GENERATOR_KEY


def enable_context_provider(
    context_provider: SystemPromptContextProviderBase,
) -> Thunk[Context, Context]:
    """Enable a tool as a context provider."""

    @context_autothunk(name=f"enable_context_provider({context_provider.title})")
    @inject
    async def _enable(
        system_prompt_generator: Annotated[
            SystemPromptGenerator, SYSTEM_PROMPT_GENERATOR_KEY
        ],
        logger=inject[get_logger(__name__)],
    ) -> Annotated[SystemPromptGenerator, SYSTEM_PROMPT_GENERATOR_KEY]:
        """Enable the context provider."""
        logger.debug(f"Enabling context provider: {context_provider.title}")
        system_prompt_generator.context_providers[context_provider.title] = (
            context_provider
        )
        return system_prompt_generator

    return _enable


def disable_context_provider(name: str) -> Thunk[Context, Context]:
    """Disable a context provider."""

    @context_autothunk(name=f"disable_context_provider({name})")
    @inject
    async def _disable(
        system_prompt_generator: Annotated[
            SystemPromptGenerator, SYSTEM_PROMPT_GENERATOR_KEY
        ],
        logger=inject[get_logger(__name__)],
    ) -> Annotated[SystemPromptGenerator, SYSTEM_PROMPT_GENERATOR_KEY]:
        """Disable the context provider."""
        logger.debug(f"Disabling context provider: {name}")
        if name in system_prompt_generator.context_providers:
            del system_prompt_generator.context_providers[name]
        return system_prompt_generator

    return _disable
