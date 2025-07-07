"""Context key system for hierarchical data access.

This module provides the ContextKey class for representing typed keys
used throughout the context system. ContextKey instances are immutable
identifiers that combine a hierarchical path with type information.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Generic, TypeVar

T = TypeVar("T")


@dataclass(frozen=True)
class ContextKey(Generic[T]):
    """Class for context keys that can be used to store and retrieve values in a context.

    ContextKey instances are immutable identifiers that combine a hierarchical path
    (using dot notation) with type information and optional descriptions. They serve
    as strongly-typed keys for accessing values in the context system.

    The class is implemented as a frozen dataclass to ensure immutability and
    supports generic typing for type safety when accessing context values.

    Attributes:
        path: The hierarchical path using dot notation (e.g., 'agent.intent.task')
        type_: The expected type of values stored under this key
        description: Optional human-readable description of the key's purpose

    Examples:
        Basic usage:
            >>> key = ContextKey("agent.intent", str, "Current agent intent")
            >>> key.path
            'agent.intent'
            >>> key.type_
            <class 'str'>

        Generic typing:
            >>> str_key = ContextKey[str]("user.name", str)
            >>> int_key = ContextKey[int]("user.age", int)

        Equality based on path:
            >>> key1 = ContextKey("agent.status", str)
            >>> key2 = ContextKey("agent.status", int)
            >>> key1 == key2
            True
    """

    path: str
    type_: type = str
    description: str = ""

    @classmethod
    def create(cls, path: str, type_: type[T], description: str) -> ContextKey[T]:
        """Create a new context key with the specified name, type, and description.

        This classmethod provides an alternative way to create ContextKey instances
        with explicit type information. It's equivalent to calling the constructor
        directly but provides better readability and type inference.

        Args:
            path: The hierarchical path using dot notation (e.g., 'agent.intent.task')
            type_: The expected type of values stored under this key
            description: Human-readable description of the key's purpose

        Returns:
            A new ContextKey instance with the specified path, type, and description

        Examples:
            Creating typed keys:
                >>> str_key = ContextKey.create("user.name", str, "User's full name")
                >>> int_key = ContextKey.create("user.age", int, "User's age in years")
                >>> bool_key = ContextKey.create("user.active", bool, "User account status")

            Type inference:
                >>> key = ContextKey.create("items.count", int, "Number of items")
                >>> key.type_
                <class 'int'>
        """
        return cls(path, type_, description)

    def __eq__(self, other: object) -> bool:
        """Check if two context keys are equal by their paths."""
        if not isinstance(other, ContextKey):
            return NotImplemented
        return self.path == other.path

    def __hash__(self) -> int:
        """Return the hash of the context key based on its path."""
        return hash(self.path)
