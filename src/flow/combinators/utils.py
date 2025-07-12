"""Shared utilities for combinator functions."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any, AsyncGenerator, TypeVar

Input = TypeVar("Input")

# Type aliases for common patterns
AnyCallable = Callable[..., Any]

# Sentinel object for stream termination
STREAM_END = object()


def get_function_name(fn: AnyCallable) -> str:
    """Extract function name for flow naming."""
    return getattr(fn, "__name__", "function")


def create_single_item_stream(item: Input) -> AsyncGenerator[Input, None]:
    """Create an async iterator that yields a single item."""

    async def _stream() -> AsyncGenerator[Input, None]:
        yield item

    return _stream()


async def empty_stream() -> AsyncGenerator[None, None]:
    """Create an empty async generator stream.

    This is the standard implementation for creating empty streams
    across the codebase. Uses the return/yield pattern which is
    the most efficient and widely compatible approach.
    """
    for _ in range(0):
        yield


async def empty_typed_stream() -> AsyncGenerator[Any, None]:
    """Create an empty async generator stream with specific type.

    Useful when type checkers need a specific return type
    but the stream should still be empty.
    """
    for _ in range(0):
        yield
