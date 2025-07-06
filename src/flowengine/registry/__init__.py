"""FlowEngine Registry System.

This module provides a centralized registry for Flow objects with support for:
- Name-based flow registration and retrieval
- Category-based organization
- Tag-based classification
- Metadata storage and search
- Thread-safe operations
"""

from .main import FlowRegistry, FlowRegistryError

__all__ = ["FlowRegistry", "FlowRegistryError"]
