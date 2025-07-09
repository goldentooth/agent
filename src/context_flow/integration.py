"""Context-Flow integration core module.

This module provides the core integration between Context and Flow systems,
including exception classes, combinators, and decorator functions.
"""

from __future__ import annotations

from collections.abc import AsyncIterator
from typing import TypeVar

__all__ = [
    "ContextFlowError",
    "MissingRequiredKeyError",
    "ContextTypeMismatchError",
    "_single_item_stream",
]

T = TypeVar("T")


class ContextFlowError(Exception):
    """Base exception for Context-Flow integration errors."""

    pass


class MissingRequiredKeyError(ContextFlowError):
    """Raised when a required context key is missing."""

    pass


class ContextTypeMismatchError(ContextFlowError):
    """Raised when a context key has the wrong type."""

    pass


async def _single_item_stream(item: T) -> AsyncIterator[T]:
    """Create a single-item async iterator."""
    yield item
