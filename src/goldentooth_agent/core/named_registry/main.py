from __future__ import annotations
from antidote import inject
from goldentooth_agent.core.logging import get_logger
from logging import Logger
from typing import Callable, Generic, Dict, Optional, Protocol, TypeVar, runtime_checkable

T = TypeVar("T")

class NamedRegistry(Generic[T]):
  """Generic registry for name-keyed objects of type T."""

  @inject
  def __init__(self, logger: Logger = inject[get_logger(__name__)]) -> None:
    """Initialize the registry with an empty dictionary."""
    self._registry: Dict[str, T] = {}
    self.logger = logger
    logger.debug(f"Initializing {self.__class__.__name__}")

  def set(self, id: str, obj: T) -> None:
    """Register an object with a given ID."""
    self.logger.debug(f"Setting {id} -> {obj}")
    self._registry[id] = obj

  def get(self, id: str) -> T:
    """Retrieve an object by its ID."""
    self.logger.debug(f"Retrieving object '{id}'")
    if id not in self._registry:
      raise KeyError(f"'{id}' is not registered; available IDs: {list(self._registry.keys())}")
    return self._registry[id]

  def remove(self, id: str) -> None:
    """Remove an object by its ID."""
    self.logger.debug(f"Removing '{id}'")
    self._registry.pop(id, None)

  def has(self, id: str) -> bool:
    """Check if an object with the given ID is registered."""
    self.logger.debug(f"Checking if '{id}' is registered")
    return id in self._registry

  def list(self) -> list[str]:
    """List all registered IDs in the registry."""
    self.logger.debug(f"Listing all registered IDs in {self.__class__.__name__}")
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

Tc = TypeVar("Tc", covariant=True)

@runtime_checkable
class Creatable(Protocol[Tc]):
  """Protocol for a class that can be instantiated."""

  @classmethod
  def create(cls) -> Tc:
    """Create an instance of the class."""
    ...

@runtime_checkable
class RegisterCallable(Protocol[T]):
  """Protocol for a callable that registers an object with a name."""

  def __call__(self, cls: Optional[type[T]] = None, *, obj: Optional[T] = None, id: Optional[str] = None) -> type[T]:
    """Register an object with the given ID in the specified registry."""
    ...

def make_register_fn(
  registry_cls: type[NamedRegistry[T]],
  *,
  get_instance_fn: Optional[Callable[[], T]] = None,
  default_id_fn: Optional[Callable[[T], str]] = None,
) -> RegisterCallable[T]:
  """Create a registration function for the given type."""
  def _decorate(
    cls: Optional[type[T]] = None,
    *,
    obj: Optional[T] = None,
    id: Optional[str] = None,
    get_instance_fn: Optional[Callable[[], T]] = get_instance_fn,
    default_id_fn: Optional[Callable[[T], str]] = default_id_fn,
  ) -> type[T]:
    """Register an object with the given ID in the specified registry."""
    from antidote import world
    registry = world[registry_cls]
    if get_instance_fn:
      final_obj = get_instance_fn()
    elif cls and isinstance(cls, Creatable):
      final_obj = cls.create()
    elif obj is not None:
      final_obj = obj
    else:
      raise ValueError("An object must be provided or creatable.")
    final_id = id or (default_id_fn(final_obj) if default_id_fn else None)
    if not final_id:
      raise ValueError("An ID must be provided or derivable.")
    registry.set(final_id, final_obj)
    if cls is not None:
      return cls
    return type(final_obj) # type: ignore[return-value]
  return _decorate
