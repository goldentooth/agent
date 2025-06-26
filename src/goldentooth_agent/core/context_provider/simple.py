from __future__ import annotations
from atomic_agents.lib.components.system_prompt_generator import (
    SystemPromptContextProviderBase,
)


class SimpleContextProvider(SystemPromptContextProviderBase):
    """Context provider that provides static information."""

    def __init__(self, title: str, info: list[str]):
        """Initialize the static context provider with a title."""
        super().__init__(title)
        self.info = info

    def get_info(self) -> str:
        """Get info about the static context provider."""
        return "\n".join(self.info)
