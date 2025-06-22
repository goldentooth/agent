from __future__ import annotations
from typing import Callable, Generic, Dict, TypeVar
from antidote import inject
from logging import Logger
from goldentooth_agent.core.logging import get_logger

T = TypeVar("T")

class NamedRegistry(Generic[T]):
  """Generic registry for name-keyed objects of type T."""

  @inject
  def __init__(self, logger: Logger = inject[get_logger(__name__)]) -> None:
    """Initialize the registry with an empty dictionary."""
    self._registry: Dict[str, T] = {}
    self.logger = logger
    logger.debug(f"Initializing {self.__class__.__name__}")

  def register(self, name: str, obj: T) -> None:
    """Register an object with a given name."""
    self.logger.debug(f"Registering {name} -> {obj}")
    self._registry[name] = obj

  def get(self, name: str) -> T:
    """Retrieve an object by its name."""
    self.logger.debug(f"Retrieving object '{name}'")
    if name not in self._registry:
      raise KeyError(f"'{name}' is not registered.")
    return self._registry[name]

  def unregister(self, name: str) -> None:
    """Unregister an object by its name."""
    self.logger.debug(f"Unregistering '{name}'")
    self._registry.pop(name, None)

  def has(self, name: str) -> bool:
    """Check if an object with the given name is registered."""
    self.logger.debug(f"Checking if '{name}' is registered")
    return name in self._registry

  def list(self) -> list[str]:
    """List all registered names in the registry."""
    self.logger.debug(f"Listing all registered names in {self.__class__.__name__}")
    return sorted(self._registry.keys())

  def all(self) -> list[T]:
    """Get all registered objects."""
    self.logger.debug(f"Retrieving all objects from {self.__class__.__name__}")
    return list(self._registry.values())

  def items(self) -> list[tuple[str, T]]:
    """Get all registered objects as (name, object) pairs."""
    self.logger.debug(f"Retrieving all items from {self.__class__.__name__}")
    return list(self._registry.items())

  def clear(self) -> None:
    """Clear all entries in the registry."""
    self.logger.debug(f"Clearing all entries in {self.__class__.__name__}")
    self._registry.clear()

def register_named(name: str, registry: NamedRegistry[T]) -> Callable[[type[T]], type[T]]:
  """Decorator to register a class instance in a named registry."""
  def _decorator(cls: type[T]) -> type[T]:
    """Decorator function to register a class instance."""
    from antidote import world
    instance = world[cls]
    registry.register(name, instance)
    return cls
  return _decorator
