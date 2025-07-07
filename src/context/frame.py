"""Context frame system for single-layer context data storage.

This module provides the ContextFrame class that represents a single layer
in a context stack. Each frame acts as a container for key-value pairs with
dictionary-like behavior.
"""

from __future__ import annotations

from typing import Any

# Type aliases for context data - contexts can store any type of value
ContextData = dict[str, Any]
ContextValue = Any


class ContextFrame:
    """A single layer of the context stack, representing local bindings."""

    def __init__(self) -> None:
        """Initialize an empty context frame."""
        super().__init__()
        self.data: ContextData = {}

    def __getitem__(self, key: str) -> ContextValue:
        """Get the value for a key, raising KeyError if not found."""
        return self.data[key]

    def __setitem__(self, key: str, value: ContextValue) -> None:
        """Set the value for a key in this context frame."""
        self.data[key] = value
