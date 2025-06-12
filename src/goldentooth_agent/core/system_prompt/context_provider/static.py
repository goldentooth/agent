from __future__ import annotations
from atomic_agents.lib.components.system_prompt_generator import SystemPromptContextProviderBase

class StaticContextProvider(SystemPromptContextProviderBase):
  """Context provider that provides static information."""

  def __init__(self, title: str, info: list[str]):
    """Initialize the static context provider with a title."""
    super().__init__(title)
    self.info = info

  def get_info(self) -> str:
    """Get info about the static context provider."""
    return "\n".join(self.info)

  @classmethod
  def create(cls, title: str, info: list[str]) -> StaticContextProvider:
    """Create a new static context provider instance."""
    return cls(title, info)

  @classmethod
  def from_dict(cls, data: dict) -> StaticContextProvider:
    """Create a static context provider from a dictionary."""
    return cls(data['title'], data['info'])

  def to_dict(self) -> dict:
    """Convert the static context provider to a dictionary."""
    return {
      'title': self.title,
      'info': self.info
    }

