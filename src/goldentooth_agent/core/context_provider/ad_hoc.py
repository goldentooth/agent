from __future__ import annotations
from atomic_agents.lib.components.system_prompt_generator import SystemPromptContextProviderBase
from typing import Callable

class AdHocContextProvider(SystemPromptContextProviderBase):
  """A context provider without an underlying component, used for ad-hoc information."""

  def __init__(self, title: str, fn: Callable[[], str]):
    """Initialize the context provider with a name."""
    super().__init__(title)
    self.fn = fn

  def get_info(self) -> str:
    """Return a string representation of the context provider's information."""
    return self.fn()
