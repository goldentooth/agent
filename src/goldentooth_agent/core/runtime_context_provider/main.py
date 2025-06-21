from __future__ import annotations
from atomic_agents.lib.components.system_prompt_generator import SystemPromptContextProviderBase
from typing import Callable

class RuntimeContextProvider(SystemPromptContextProviderBase):
  """A context provider without an underlying component, used for dynamic information."""

  def __init__(self, title: str, fn: Callable[[], str]):
    """Initialize the dynamic context provider with a name."""
    super().__init__(title)
    self.fn = fn

  def get_info(self) -> str:
    """Return a string representation of the dynamic context provider's information."""
    return self.fn()

  @classmethod
  def from_dict(cls, data: dict) -> RuntimeContextProvider:
    """Create a DynamicContextProvider from a dictionary."""
    title: str = data['title']
    if not title:
      raise ValueError("DynamicContextProvider must have a 'title' field.")
    info: list[str] = data['info']
    if not info:
      raise ValueError("DynamicContextProvider must have an 'info' field.")
    return cls(title, lambda: "\n".join(info))
