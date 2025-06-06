from __future__ import annotations
from antidote import injectable
from atomic_agents.lib.components.system_prompt_generator import SystemPromptContextProviderBase
from typing import Dict

@injectable(factory_method='create')
class ContextProviderRegistry:
  """Registry for context providers used in chat sessions."""

  def __init__(self):
    """Initialize the registry with an empty dictionary."""
    self.providers: Dict[str, SystemPromptContextProviderBase] = {}

  @classmethod
  def create(cls) -> ContextProviderRegistry:
    """Create a new ContextProviderRegistry instance."""
    result = cls()
    return result

  def register(self, name: str, provider: SystemPromptContextProviderBase):
    """Register a context provider with a given name."""
    self.providers[name] = provider

  def list(self) -> Dict[str, SystemPromptContextProviderBase]:
    """List all registered context providers."""
    return self.providers

  def get(self, name: str) -> SystemPromptContextProviderBase:
    """Retrieve a context provider by name."""
    return self.providers[name]

  def exists(self, name: str) -> bool:
    """Check if a context provider with the given name exists."""
    return name in self.providers

  def remove(self, name: str):
    """Remove a context provider by name."""
    if name in self.providers:
      del self.providers[name]
    else:
      raise KeyError(f"Context provider '{name}' not found.")

  def clear(self):
    """Clear all registered context providers."""
    self.providers.clear()
