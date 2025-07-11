"""Protocol definitions for Flow Engine to break circular dependencies."""

from __future__ import annotations

from typing import Any, Protocol, TypeVar, runtime_checkable

# Type variables for protocols
T_co = TypeVar("T_co", covariant=True)  # For protocol return types
T = TypeVar(
    "T"
)  # For protocol methods that use type in both parameter and return positions
K = TypeVar("K", covariant=True)  # Key type
V = TypeVar("V", covariant=True)  # Value type


@runtime_checkable
class ContextKeyProtocol(Protocol[T_co]):
    """Protocol for context keys that can store typed values."""

    @property
    def name(self) -> str:
        """The unique name/identifier for this context key."""
        raise NotImplementedError("Subclasses must implement name property")

    @property
    def value_type(self) -> type[T_co]:
        """The type of values this key can store."""
        raise NotImplementedError("Subclasses must implement value_type property")


@runtime_checkable
class ContextProtocol(Protocol):
    """Protocol for context objects that can store keyed values."""

    def get(self, key: ContextKeyProtocol[T]) -> T:  # noqa: ARG002
        """Get a value by key."""
        raise NotImplementedError("Subclasses must implement get method")

    def set(self, key: ContextKeyProtocol[T], value: T) -> None:  # noqa: ARG002
        """Set a value by key."""
        raise NotImplementedError("Subclasses must implement set method")

    def contains(self, key: ContextKeyProtocol[Any]) -> bool:  # noqa: ARG002
        """Check if key exists in context."""
        raise NotImplementedError("Subclasses must implement contains method")


@runtime_checkable
class FlowProtocol(Protocol[T_co, V]):
    """Protocol for Flow objects to avoid concrete dependencies."""

    @property
    def name(self) -> str:
        """The name of this flow."""
        raise NotImplementedError("Subclasses must implement name property")

    def __call__(self, stream: Any) -> Any:  # noqa: ARG002
        """Execute the flow with the given stream."""
        raise NotImplementedError("Subclasses must implement __call__ method")
