from __future__ import annotations
from typing import Any, Generic, Type, TypeVar, get_args

T = TypeVar('T')

class ContextKey(Generic[T]):
  """Protocol for context keys that can be used to store and retrieve values in a context."""

  def __init__(self, name: str, type_T: Type[T]) -> None:
    """Initialize the context key with a name."""
    self.name: str = name
    self.type_T: Type[T] = type_T

  @classmethod
  def create(cls, name: str, type_T: Type[T]) -> ContextKey[T]:
    """Create a new context key with the specified name and type."""
    key = cls(name, type_T)
    return key

  def __str__(self) -> str:
    """Return the string representation of the context key."""
    return self.name

  def __repr__(self) -> str:
    """Return the string representation of the context key."""
    return f"ContextKey({self.name}<{self.type_T.__name__}>)"

  def __eq__(self, other: object) -> bool:
    """Check if two context keys are equal by their names."""
    if not isinstance(other, ContextKey):
      return NotImplemented
    return self.name == other.name

  def __hash__(self) -> int:
    """Return the hash of the context key based on its name."""
    return hash(self.name)

def context_key(name: str, type_T: Type[T]) -> ContextKey[T]:
  """Create a context key with the specified name and type."""
  return ContextKey.create(name, type_T)
