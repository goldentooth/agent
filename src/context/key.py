"""Context key system for hierarchical data access.

This module provides the ContextKey class for representing typed keys
used throughout the context system. ContextKey instances are immutable
identifiers that combine a hierarchical path with type information.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import cached_property
from typing import Generic, TypeVar

from .symbol import Symbol

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

    @cached_property
    def symbol(self) -> Symbol:
        """Return a Symbol representation of the context key.

        The symbol property provides a Symbol instance based on the key's path,
        enabling hierarchical navigation and string-based operations. The Symbol
        is created once and cached for the lifetime of the ContextKey instance.

        Returns:
            A Symbol instance created from the key's path

        Examples:
            Basic usage:
                >>> key = ContextKey("agent.intent.task", str)
                >>> key.symbol
                Symbol('agent.intent.task')
                >>> str(key.symbol)
                'agent.intent.task'

            Hierarchical navigation:
                >>> key = ContextKey("user.profile.settings", str)
                >>> key.symbol.parts()
                ['user', 'profile', 'settings']

            Cached property:
                >>> key = ContextKey("test.key", str)
                >>> symbol1 = key.symbol
                >>> symbol2 = key.symbol
                >>> symbol1 is symbol2  # Same instance
                True
        """
        return Symbol(self.path)

    def __str__(self) -> str:
        """Return the string representation of the context key.

        Returns the path of the context key as a string, providing a clean
        and readable representation. This makes ContextKey instances easy
        to use in string contexts like logging, debugging, and formatting.

        Returns:
            The path string of the context key

        Examples:
            Basic usage:
                >>> key = ContextKey("agent.intent", str)
                >>> str(key)
                'agent.intent'

            String formatting:
                >>> key = ContextKey("user.name", str, "User's name")
                >>> f"Processing key: {key}"
                'Processing key: user.name'

            Logging and debugging:
                >>> key = ContextKey("app.config.debug", bool)
                >>> print(f"Checking {key}")
                Checking app.config.debug
        """
        return self.path

    def __repr__(self) -> str:
        """Return the detailed string representation of the context key.

        Returns a detailed representation showing both the path and type
        information, which is useful for debugging, development, and logging.
        Following Python conventions, this provides more detail than __str__.

        Returns:
            A formatted string in the form "ContextKey(path<type_name>)"

        Examples:
            Basic usage:
                >>> key = ContextKey("agent.intent", str)
                >>> repr(key)
                'ContextKey(agent.intent<str>)'

            Different types:
                >>> int_key = ContextKey("user.age", int)
                >>> repr(int_key)
                'ContextKey(user.age<int>)'

            Complex types:
                >>> list_key = ContextKey("items", list)
                >>> repr(list_key)
                'ContextKey(items<list>)'

            Debugging context:
                >>> key = ContextKey("config.debug", bool, "Debug mode")
                >>> print(f"Working with {repr(key)}")
                Working with ContextKey(config.debug<bool>)
        """
        return f"ContextKey({self.path}<{self.type_.__name__}>)"

    def __eq__(self, other: object) -> bool:
        """Check if two context keys are equal by their paths.

        Two ContextKey instances are considered equal if they have the same path,
        regardless of their type or description. This enables keys to be used
        as dictionary keys and in sets, where equality is based solely on the
        hierarchical path they represent.

        Args:
            other: The object to compare this ContextKey with

        Returns:
            True if other is a ContextKey with the same path, False if other
            is a ContextKey with a different path, or NotImplemented if other
            is not a ContextKey (letting Python handle the comparison)

        Examples:
            Same path, different types:
                >>> key1 = ContextKey("user.name", str)
                >>> key2 = ContextKey("user.name", int)
                >>> key1 == key2
                True

            Same path, different descriptions:
                >>> key1 = ContextKey("config.debug", bool, "Debug mode")
                >>> key2 = ContextKey("config.debug", bool, "Debug flag")
                >>> key1 == key2
                True

            Different paths:
                >>> key1 = ContextKey("user.name", str)
                >>> key2 = ContextKey("user.email", str)
                >>> key1 == key2
                False

            Comparison with non-ContextKey:
                >>> key = ContextKey("test", str)
                >>> key == "test"
                False
        """
        if not isinstance(other, ContextKey):
            return NotImplemented
        return self.path == other.path

    def __hash__(self) -> int:
        """Return the hash of the context key based on its path."""
        return hash(self.path)
