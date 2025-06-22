from __future__ import annotations
from antidote import inject, injectable
from atomic_agents.lib.components.system_prompt_generator import SystemPromptContextProviderBase
from goldentooth_agent.core.logging import get_logger
from logging import Logger
from rich.table import Table
from typing import Dict

@injectable(factory_method='create')
class ContextProviderRegistry:
  """Registry for context providers used in chat sessions."""

  def __init__(self, logger: Logger = inject[get_logger(__name__)]):
    """Initialize the registry with an empty dictionary."""
    logger.debug("Initializing ContextProviderRegistry")
    self.providers: Dict[str, SystemPromptContextProviderBase] = {}

  @classmethod
  def create(cls) -> ContextProviderRegistry:
    """Create a new ContextProviderRegistry instance."""
    result = cls()
    return result

  @inject.method
  def register(self, name: str, provider: SystemPromptContextProviderBase, logger: Logger = inject[get_logger(__name__)]) -> None:
    """Register a context provider with a given name."""
    logger.debug(f"Registering context provider: {name}")
    self.providers[name] = provider

  @inject.method
  def list(self, logger: Logger = inject[get_logger(__name__)]) -> Dict[str, SystemPromptContextProviderBase]:
    """List all registered context providers."""
    logger.debug("Listing all registered context providers")
    return self.providers

  @inject.method
  def get(self, name: str, logger: Logger = inject[get_logger(__name__)]) -> SystemPromptContextProviderBase:
    """Retrieve a context provider by name."""
    logger.debug(f"Retrieving context provider: {name}")
    return self.providers[name]

  @inject.method
  def get_many(self, names: list[str], logger: Logger = inject[get_logger(__name__)]) -> Dict[str, SystemPromptContextProviderBase]:
    """Retrieve multiple context providers by their names."""
    logger.debug(f"Retrieving context providers: {names}")
    return {name: self.providers[name] for name in names if name in self.providers}

  @inject.method
  def has(self, name: str, logger: Logger = inject[get_logger(__name__)]) -> bool:
    """Check if a context provider with the given name exists."""
    logger.debug(f"Checking if context provider exists: {name}")
    return name in self.providers

  @inject.method
  def remove(self, name: str, logger: Logger = inject[get_logger(__name__)]) -> None:
    """Remove a context provider by name."""
    logger.debug(f"Removing context provider: {name}")
    if name in self.providers:
      del self.providers[name]
    else:
      raise KeyError(f"Context provider '{name}' not found.")

  @inject.method
  def clear(self, logger: Logger = inject[get_logger(__name__)]) -> None:
    """Clear all registered context providers."""
    logger.debug("Clearing all registered context providers")
    self.providers.clear()

  @inject.method
  def dump(self, logger: Logger = inject[get_logger(__name__)]) -> Table:
    """Dump all registered context providers to a table."""
    logger.debug("Dumping all registered context providers to a table")
    table = Table(title="Context Providers")
    table.add_column("Title", justify="left", style="cyan", no_wrap=True)
    table.add_column("Info", justify="left", style="magenta")
    for name, provider in self.providers.items():
      table.add_row(name, provider.get_info())
    return table

@inject
def register_context_provider(*, name: str, registry: ContextProviderRegistry = inject.me()):
  """Decorator to register a context provider with a given name."""
  def _decorator(cls):
    if not issubclass(cls, SystemPromptContextProviderBase):
      raise TypeError("Context provider must be a subclass of SystemPromptContextProviderBase.")
    registry.register(name, cls(name))
    return cls
  return _decorator
