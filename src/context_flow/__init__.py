"""Context-Flow integration package.

This package provides integration between the core Context system and the Flow engine,
enabling context-aware flow compositions with type-safe operations.

The package includes:
- Bridge functionality for protocol-based integration
- Trampoline support for advanced flow control patterns
- Context-aware flow combinators and utilities
- Extension methods for seamless Context-Flow integration
"""

from context_flow.bridge import (
    ContextFlowBridge,
    get_context_bridge,
    initialize_context_integration,
)
from context_flow.integration import ContextFlowCombinators
from context_flow.trampoline import (
    TrampolineFlowCombinators,
    extend_flow_with_trampoline,
)
from context_flow.trampoline.flag_combinators import FlagCombinators

__version__ = "0.1.0"

__all__ = [
    # Bridge functionality for Context-Flow integration
    "ContextFlowBridge",
    "get_context_bridge",
    "initialize_context_integration",
    # Trampoline functionality for advanced flow control
    "FlagCombinators",
    "TrampolineFlowCombinators",
    "extend_flow_with_trampoline",
    # Context-aware flow combinators
    "ContextFlowCombinators",
]
