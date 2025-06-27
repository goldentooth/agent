from .dependency_graph import DependencyGraph
from .flow_integration import (
    ContextFlowCombinators,
    ContextFlowError,
    ContextTypeMismatchError,
    MissingRequiredKeyError,
    context_flow,
    extend_flow_with_context,
)
from .frame import ContextFrame
from .history_tracker import HistoryTracker
from .key import ContextKey, context_key
from .main import Context
from .snapshot_manager import SnapshotManager
from .symbol import Symbol

# Automatically extend Flow with context methods
extend_flow_with_context()

__all__ = [
    "Context",
    "ContextFrame",
    "ContextKey",
    "context_key",
    "DependencyGraph",
    "HistoryTracker",
    "SnapshotManager",
    "Symbol",
    "ContextFlowCombinators",
    "ContextFlowError",
    "MissingRequiredKeyError",
    "ContextTypeMismatchError",
    "context_flow",
    "extend_flow_with_context",
]
