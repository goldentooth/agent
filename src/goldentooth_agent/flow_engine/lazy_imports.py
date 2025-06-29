"""Lazy import utilities to break circular dependencies."""

from __future__ import annotations

import importlib
from typing import TYPE_CHECKING, Any, TypeVar

if TYPE_CHECKING:
    from goldentooth_agent.core.context import Context, ContextKey

T = TypeVar("T")


def get_context_module() -> Any:
    """Lazily import the context module to avoid circular imports."""
    return importlib.import_module("goldentooth_agent.core.context")


def get_context_key_class() -> type[ContextKey]:
    """Lazily get the ContextKey class."""
    context_module = get_context_module()
    return context_module.ContextKey


def get_context_class() -> type[Context]:
    """Lazily get the Context class."""
    context_module = get_context_module()
    return context_module.Context


def create_context_key(
    name: str, value_type: type[T], description: str = ""
) -> ContextKey[T]:
    """Create a context key without direct import."""
    ContextKey = get_context_key_class()
    return ContextKey.create(name, value_type, description)
