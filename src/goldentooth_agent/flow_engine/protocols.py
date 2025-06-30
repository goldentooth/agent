"""Protocol definitions for Flow Engine to break circular dependencies."""

from __future__ import annotations

from typing import Any, Protocol, TypeVar, runtime_checkable

# Type variables for protocols (invariant since they're used in both input and output positions)
T = TypeVar("T")
K = TypeVar("K")  # Key type
V = TypeVar("V")  # Value type


@runtime_checkable
class ContextKeyProtocol(Protocol[T]):
    """Protocol for context keys that can store typed values."""

    @property
    def name(self) -> str:
        """The unique name/identifier for this context key."""
        ...

    @property
    def value_type(self) -> type[T]:
        """The type of values this key can store."""
        ...


@runtime_checkable
class ContextProtocol(Protocol):
    """Protocol for context objects that can store keyed values."""

    def get(self, key: ContextKeyProtocol[T]) -> T:
        """Get a value by key."""
        ...

    def set(self, key: ContextKeyProtocol[T], value: T) -> None:
        """Set a value by key."""
        ...

    def contains(self, key: ContextKeyProtocol[Any]) -> bool:
        """Check if key exists in context."""
        ...


@runtime_checkable
class FlowProtocol(Protocol[T, V]):
    """Protocol for Flow objects to avoid concrete dependencies."""

    @property
    def name(self) -> str:
        """The name of this flow."""
        ...

    def __call__(self, stream: Any) -> Any:
        """Execute the flow with the given stream."""
        ...
