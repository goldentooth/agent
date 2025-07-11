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
        ...

    @property
    def value_type(self) -> type[T_co]:
        """The type of values this key can store."""
        ...


@runtime_checkable
class ContextProtocol(Protocol):
    """Protocol for context objects that can store keyed values."""

    def get(self, key: ContextKeyProtocol[T]) -> T:  # noqa: ARG002
        """Get a value by key."""
        ...

    def set(self, key: ContextKeyProtocol[T], value: T) -> None:  # noqa: ARG002
        """Set a value by key."""
        ...

    def contains(self, key: ContextKeyProtocol[Any]) -> bool:  # noqa: ARG002
        """Check if key exists in context."""
        ...


@runtime_checkable
class FlowProtocol(Protocol[T_co, V]):
    """Protocol for Flow objects to avoid concrete dependencies."""

    @property
    def name(self) -> str:
        """The name of this flow."""
        ...

    def __call__(self, stream: Any) -> Any:  # noqa: ARG002
        """Execute the flow with the given stream."""
        ...
