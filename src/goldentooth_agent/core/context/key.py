from __future__ import annotations

from dataclasses import dataclass
from functools import cached_property
from typing import Generic, TypeVar

from .symbol import Symbol

T = TypeVar("T")


@dataclass(frozen=True)
class ContextKey(Generic[T]):
    """Class for context keys that can be used to store and retrieve values in a context."""

    path: str
    type_: type = str
    description: str = ""

    @classmethod
    def create(cls, path: str, type_: type[T], description: str) -> ContextKey[T]:
        """Create a new context key with the specified name, type, and description."""
        return cls(path, type_, description)

    @cached_property
    def symbol(self) -> Symbol:
        """Return a Symbol representation of the context key."""
        return Symbol(self.path)

    def __str__(self) -> str:
        """Return the string representation of the context key."""
        return self.path

    def __repr__(self) -> str:
        """Return the string representation of the context key."""
        return f"ContextKey({self.path}<{self.type_.__name__}>)"

    def __eq__(self, other: object) -> bool:
        """Check if two context keys are equal by their paths."""
        if not isinstance(other, ContextKey):
            return NotImplemented
        return self.path == other.path

    def __hash__(self) -> int:
        """Return the hash of the context key based on its path."""
        return hash(self.path)


def context_key(name: str, type_: type[T], description: str = "") -> ContextKey[T]:
    """Create a context key with the specified name and type."""
    return ContextKey.create(name, type_, description)
