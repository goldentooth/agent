"""Trampoline system for context-aware flow execution.

This module provides trampoline execution patterns for iterative and conditional
flow processing with context state management.
"""

from __future__ import annotations

from collections.abc import AsyncGenerator
from typing import TypeVar

__all__ = [
    "_async_iter_from_item",
]

T = TypeVar("T")


async def _async_iter_from_item(item: T) -> AsyncGenerator[T, None]:
    """Create an async generator that yields a single item.

    This utility function converts a single item into an async generator
    that yields that item exactly once. This is useful for creating
    single-item streams for flow processing.

    Args:
        item: The item to be yielded by the async generator.

    Returns:
        An async generator that yields the item once.

    Example:
        ```python
        async for value in _async_iter_from_item("hello"):
            print(value)  # Prints: hello
        ```
    """
    yield item
