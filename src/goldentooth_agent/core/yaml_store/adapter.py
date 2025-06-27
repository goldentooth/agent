from typing import Any, Protocol, TypeVar, runtime_checkable

T = TypeVar("T")  # Type being serialized/deserialized


@runtime_checkable
class YamlStoreAdapter(Protocol[T]):
    """Protocol for classes that can be serialized to and from YAML."""

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> T:
        """Create an instance from a dictionary representation."""
        ...

    @classmethod
    def to_dict(cls, id: str, obj: T) -> dict[str, Any]:
        """Convert the instance to a dictionary representation."""
        ...
