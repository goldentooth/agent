"""FlowEngine Registry System.

This module provides a centralized registry for Flow objects with support for:
- Name-based flow registration and retrieval
- Category-based organization
- Tag-based classification
- Metadata storage and search
- Thread-safe operations
"""

from .main import (
    FlowRegistry,
    FlowRegistryError,
    flow_registry,
    get_flow,
    list_flows,
    register_flow,
    search_flows,
    unregister_flow,
)

__all__ = [
    "FlowRegistry",
    "FlowRegistryError",
    "flow_registry",
    "register_flow",
    "get_flow",
    "list_flows",
    "search_flows",
    "unregister_flow",
]
