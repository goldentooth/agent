"""Shared utilities for combinator functions."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

# Type aliases for common patterns
AnyCallable = Callable[..., Any]

# Sentinel object for stream termination
STREAM_END = object()


def get_function_name(fn: AnyCallable) -> str:
    """Extract function name for flow naming."""
    return getattr(fn, "__name__", "function")
