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
