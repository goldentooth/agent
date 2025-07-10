"""Context-Flow integration package.

This package provides integration between the core Context system and the Flow engine,
enabling context-aware flow compositions with type-safe operations.
"""

from context_flow.integration import ContextFlowCombinators
from context_flow.trampoline import (
    TrampolineFlowCombinators,
    extend_flow_with_trampoline,
)
from context_flow.trampoline.flag_combinators import FlagCombinators

__version__ = "0.1.0"

__all__ = [
    "FlagCombinators",
    "ContextFlowCombinators",
    "TrampolineFlowCombinators",
    "extend_flow_with_trampoline",
]
