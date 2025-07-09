"""Context package for managing hierarchical, reactive context data.

This package provides a comprehensive system for managing application context
with support for:
- Hierarchical key-value storage with type safety
- Computed properties and transformations
- Change tracking and history management
- Snapshot and restore functionality
- Dependency tracking between values

The package is designed to have no dependencies on the Flow system, making it
usable as a standalone context management solution.
"""

from .computed import ComputedProperty, Transformation
from .dependency_graph import DependencyGraph
from .frame import ContextFrame
from .history_tracker import ContextChangeEvent, HistoryTracker
from .key import ContextKey, context_key
from .main import Context
from .snapshot_manager import SnapshotManager
from .snapshots import ContextSnapshot
from .symbol import Symbol

__all__ = [
    # Core classes
    "Context",
    "Symbol",
    "ContextKey",
    "ContextFrame",
    "DependencyGraph",
    "HistoryTracker",
    "SnapshotManager",
    "ContextSnapshot",
    "ComputedProperty",
    "Transformation",
    "ContextChangeEvent",
    # Utility functions
    "context_key",
]
