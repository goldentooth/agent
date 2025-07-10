"""Constants and utilities for trampoline execution patterns.

This module provides shared constants and basic utilities used across
the trampoline system for context-aware flow execution.
"""

from __future__ import annotations

from collections.abc import AsyncGenerator
from typing import TypeVar

from context.key import ContextKey

__all__ = [
    "async_iter_from_item",
    "SHOULD_EXIT_KEY",
    "SHOULD_BREAK_KEY",
    "SHOULD_SKIP_KEY",
]

T = TypeVar("T")

# Control flow context keys
SHOULD_EXIT_KEY: ContextKey[bool] = ContextKey(
    "flow.trampoline.should_exit", bool, "Signal to exit trampoline loop"
)
SHOULD_BREAK_KEY: ContextKey[bool] = ContextKey(
    "flow.trampoline.should_break", bool, "Signal to break/restart current iteration"
)
SHOULD_SKIP_KEY: ContextKey[bool] = ContextKey(
    "flow.trampoline.should_skip", bool, "Signal to skip certain operations"
)


async def async_iter_from_item(item: T) -> AsyncGenerator[T, None]:
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
        async for value in async_iter_from_item("hello"):
            print(value)  # Prints: hello
        ```
    """
    yield item
