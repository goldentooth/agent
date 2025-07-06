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
    clear_registry,
    export_registry,
    flow_registry,
    get_flow,
    import_registry,
    list_flows,
    register_flow,
    registered_flow,
    search_flows,
    unregister_flow,
)

__all__ = [
    "FlowRegistry",
    "FlowRegistryError",
    "clear_registry",
    "export_registry",
    "flow_registry",
    "import_registry",
    "register_flow",
    "registered_flow",
    "get_flow",
    "list_flows",
    "search_flows",
    "unregister_flow",
]
