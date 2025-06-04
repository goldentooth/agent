from __future__ import annotations
from typing import List, Dict, Type, TYPE_CHECKING

from atomic_agents.agents.base_agent import BaseAgent

if TYPE_CHECKING:
  from .base import ContextProviderBase
  from ..initial_context import InitialContext

class ContextProviderRegistry:
  _registry: Dict[str, Type[ContextProviderBase]] = {}

  @classmethod
  def register(cls, cp_cls) -> None:
    """Register a context provider class in the registry."""
    print(f"Registering context provider: {cp_cls.__name__}")
    name = cp_cls.metadata_class.get_name()
    if name in cls._registry:
      # raise ValueError(f"Duplicate context provider name: {name}")
      pass
    cls._registry[name] = cp_cls
    return cp_cls

  @classmethod
  def get(cls, name) -> type | None:
    """Retrieve a context provider class by its name."""
    return cls._registry.get(name)

  @classmethod
  def keys(cls) -> List[str]:
    """Get all registered context provider names."""
    return list(cls._registry.keys())

  @classmethod
  def items(cls) -> List[tuple[str, type]]:
    """Get all registered context provider classes as (name, class) pairs."""
    return list(cls._registry.items())

  @classmethod
  def all(cls) -> List[type]:
    """Get all registered context provider classes."""
    return list(cls._registry.values())

  @classmethod
  def populate(cls, agent: BaseAgent, initial_context: InitialContext) -> None:
    """Populate the agent with all discovered context providers."""
    for title, cp_cls in cls.items():
      agent.register_context_provider(title, cp_cls(initial_context))

if __name__ == "__main__":
  # Example usage
  from .base import ContextProviderBase
  from ..initial_context import InitialContext
  from datetime import datetime

  class ExampleContextProvider(ContextProviderBase):
    class metadata_class:
      @staticmethod
      def get_name():
        return "ExampleContextProvider"

  initial_context = InitialContext(current_date=datetime.now())
  ContextProviderRegistry.register(ExampleContextProvider)

  print("Registered context providers:", ContextProviderRegistry.keys())
  print("ExampleContextProvider registered successfully.")
  print("All registered context providers:", ContextProviderRegistry.all())
  print("Retrieving ExampleContextProvider:", ContextProviderRegistry.get("ExampleContextProvider"))
  print("Retrieving non-existent provider:", ContextProviderRegistry.get("NonExistentProvider"))
  print("Items in registry:", ContextProviderRegistry.items())
  print("All context providers:", ContextProviderRegistry.all())
  print("Keys in registry:", ContextProviderRegistry.keys())
  print("ExampleContextProvider metadata name:", ExampleContextProvider.metadata_class.get_name())
