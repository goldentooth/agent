from atomic_agents.lib.components.system_prompt_generator import SystemPromptContextProviderBase
from typing import Callable

class DynamicContextProvider(SystemPromptContextProviderBase):
  """A context provider that can dynamically provide context based on the current state."""

  def __init__(self, title: str, fn: Callable[[], str]):
    """Initialize the dynamic context provider with a name."""
    super().__init__(title)
    self.fn = fn

  def get_info(self) -> str:
    """Return a string representation of the dynamic context provider."""
    return self.fn()
