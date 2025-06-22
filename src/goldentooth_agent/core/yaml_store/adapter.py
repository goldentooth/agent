from typing import Protocol, TypeVar, runtime_checkable

T = TypeVar("T") # Type being serialized/deserialized

@runtime_checkable
class YamlStoreAdapter(Protocol[T]):
  """Protocol for classes that can be serialized to and from YAML."""

  @classmethod
  def from_dict(cls, data: dict) -> T:
    """Create an instance from a dictionary representation."""
    ...

  @classmethod
  def to_dict(cls, obj: T) -> dict:
    """Convert the instance to a dictionary representation."""
    ...
