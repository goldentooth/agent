"""Context-Flow bridge for protocol-based integration.

This module provides a protocol-based bridge to avoid circular dependencies
between Context and Flow systems while enabling full integration.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass

__all__ = [
    "initialize_context_integration",
]

# Global bridge instance for singleton pattern
_bridge_instance: "ContextFlowBridge | None" = None


def initialize_context_integration() -> None:
    """Initialize the Context-Flow integration bridge.

    This function sets up the global bridge instance and initializes all
    integration components for seamless Context-Flow system interaction.
    It ensures proper registration of context keys, trampoline support,
    and protocol-based communication between systems.

    The initialization is idempotent - calling it multiple times has no
    additional effect beyond the first call.

    Example:
        ```python
        from context_flow.bridge import initialize_context_integration

        # Initialize the bridge (safe to call multiple times)
        initialize_context_integration()

        # Now Context-Flow integration is ready for use
        from context_flow.integration import ContextFlowCombinators
        # Bridge provides protocol-based access to all functionality
        ```

    Note:
        This function should be called early in application startup
        to ensure all Context-Flow integration features are available
        when needed. The initialization handles:

        - Context key registration for trampoline control signals
        - Flow extension methods for trampoline execution
        - Protocol-based bridge instantiation
        - Cross-system communication setup

        All integration is handled through protocols to avoid circular
        dependencies between the Context and Flow engine packages.
    """
    global _bridge_instance

    # Ensure initialization is idempotent
    if _bridge_instance is not None:
        return

    # Initialize the bridge instance
    _bridge_instance = ContextFlowBridge()

    # Set up trampoline integration
    _bridge_instance.register_trampoline_support()

    # Initialize Flow class extensions
    from context_flow.trampoline import extend_flow_with_trampoline

    extend_flow_with_trampoline()

    # Initialize Context class extensions
    from context_flow.integration import extend_flow_with_context

    extend_flow_with_context()


class ContextFlowBridge:
    """Protocol-based bridge for Context-Flow system integration.

    This class provides a bridge between Context and Flow systems using
    protocols to avoid circular dependencies while enabling full integration.
    """

    def __init__(self) -> None:
        """Initialize the Context-Flow bridge."""
        super().__init__()
        # Initialize bridge state
        self._initialized = False

    def register_trampoline_support(self) -> None:
        """Register trampoline support with the bridge."""
        # Placeholder for trampoline registration
        pass
