from __future__ import annotations
from antidote import injectable
from atomic_agents.lib.components.system_prompt_generator import (
    SystemPromptContextProviderBase,
)
from datetime import datetime
from .registry import register_context_provider


@register_context_provider
@injectable(factory_method="create")
class CurrentTime(SystemPromptContextProviderBase):
    """Context provider that provides information about the current time."""

    def get_info(self) -> str:
        """Get info about the current time context provider."""
        time_string = datetime.now().strftime("%H:%M:%S")
        return "\n".join(
            [
                f"The current time in HH:MM:SS format is {time_string}.",
            ]
        )

    @classmethod
    def create(cls) -> CurrentTime:
        """Create a new CurrentTime instance."""
        return cls("Current Time")
