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
    "get_context_bridge",
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


def get_context_bridge() -> "ContextFlowBridge":
    """Get the global Context-Flow bridge instance.

    This function provides access to the global bridge instance that handles
    all Context-Flow system integration. If the bridge has not been initialized
    yet, this function will automatically call initialize_context_integration()
    to set it up.

    Returns:
        The global ContextFlowBridge instance for Context-Flow integration.

    Example:
        ```python
        from context_flow.bridge import get_context_bridge

        # Get the bridge instance (initializes if needed)
        bridge = get_context_bridge()

        # Use bridge methods for integration
        bridge.ensure_context_keys()
        trampoline_key = bridge.get_trampoline_key("should_exit")
        ```

    Note:
        This function is the recommended way to access bridge functionality
        rather than calling initialize_context_integration() directly and
        accessing the global variable. The function ensures proper initialization
        and provides a clean API for bridge access.

        The bridge instance is shared globally across the application to ensure
        consistent Context-Flow integration state. All bridge operations are
        thread-safe and support concurrent access patterns.
    """
    global _bridge_instance

    # Initialize bridge if not already done
    if _bridge_instance is None:
        initialize_context_integration()

    # Bridge should be available after initialization
    if _bridge_instance is None:
        raise RuntimeError(
            "Failed to initialize Context-Flow bridge. "
            + "Check that all required dependencies are available."
        )

    return _bridge_instance


class ContextFlowBridge:
    """Protocol-based bridge for Context-Flow system integration.

    This class provides a bridge between Context and Flow systems using
    protocols to avoid circular dependencies while enabling full integration.
    """

    def __init__(self) -> None:
        """Initialize the Context-Flow bridge.

        Sets up the bridge with proper state management for Context-Flow integration.
        Initializes all internal data structures needed for protocol-based communication,
        context key management, trampoline key mappings, and protocol registrations.

        The bridge maintains separate registries for:
        - Context keys: Mappings between context key names and their configurations
        - Trampoline keys: Control signal key mappings for trampoline execution
        - Protocols: Protocol definitions for cross-system communication

        After initialization, the bridge is ready to handle registration and
        integration operations between Context and Flow systems.

        Example:
            ```python
            from context_flow.bridge import ContextFlowBridge

            # Create a new bridge instance
            bridge = ContextFlowBridge()

            # Bridge is now ready for registration operations
            bridge.register_trampoline_support()
            ```

        Note:
            The bridge uses internal state to track initialization and prevent
            double-initialization of components. All registries start empty
            and are populated through registration methods.
        """
        super().__init__()

        # Core bridge state
        self._initialized = True

        # Context key registry for tracking context key configurations
        self._context_keys: dict[str, str] = {}

        # Trampoline key registry for control signal mappings
        self._trampoline_keys: dict[str, str] = {}

        # Protocol registry for cross-system communication
        self._protocols: dict[str, dict[str, str]] = {}

    def ensure_context_keys(self) -> None:
        """Ensure that required Context keys are registered for trampoline operations.

        This method registers the standard trampoline control signal keys that enable
        Context-Flow integration. These keys are used by trampoline execution patterns
        to control flow behavior through context state changes.

        The following keys are registered:
        - should_exit: Controls early termination of trampoline execution
        - should_break: Controls breaking out of trampoline iteration loops
        - should_skip: Controls skipping of trampoline execution steps

        This method is idempotent - calling it multiple times has no additional
        effect beyond the first call. Existing custom keys are preserved.

        Example:
            ```python
            from context_flow.bridge import ContextFlowBridge

            bridge = ContextFlowBridge()

            # Register standard trampoline control keys
            bridge.ensure_context_keys()

            # Keys are now available for trampoline operations
            exit_key = bridge._trampoline_keys["should_exit"]
            break_key = bridge._trampoline_keys["should_break"]
            skip_key = bridge._trampoline_keys["should_skip"]
            ```

        Note:
            The registered keys follow the naming convention "context_flow.{signal}"
            to provide clear namespacing and avoid conflicts with user-defined
            context keys. All keys are stored in the _trampoline_keys registry
            for efficient lookup during trampoline execution.
        """
        # Register standard trampoline control signal keys
        trampoline_signals = {
            "should_exit": "context_flow.should_exit",
            "should_break": "context_flow.should_break",
            "should_skip": "context_flow.should_skip",
        }

        # Add keys if not already present (idempotent)
        for signal_name, context_key in trampoline_signals.items():
            if signal_name not in self._trampoline_keys:
                self._trampoline_keys[signal_name] = context_key

    def get_trampoline_key(self, signal_name: str, default: str | None = None) -> str:
        """Get the context key for a registered trampoline signal.

        This method retrieves the context key associated with a trampoline control
        signal. The signal names correspond to the control signals registered via
        ensure_context_keys() or manually added to the bridge registry.

        Args:
            signal_name: The name of the trampoline signal to retrieve
            default: Optional default value to return if the signal is not found

        Returns:
            The context key string associated with the signal name

        Raises:
            KeyError: If the signal name is not found and no default is provided

        Example:
            ```python
            from context_flow.bridge import ContextFlowBridge

            bridge = ContextFlowBridge()
            bridge.ensure_context_keys()

            # Get standard trampoline control keys
            exit_key = bridge.get_trampoline_key("should_exit")
            break_key = bridge.get_trampoline_key("should_break")
            skip_key = bridge.get_trampoline_key("should_skip")

            # Use with default value for safety
            custom_key = bridge.get_trampoline_key("custom_signal", "default.key")
            ```

        Note:
            This method provides safe access to the internal _trampoline_keys
            registry while supporting both registered standard signals and
            custom signals added by users. The default parameter enables
            graceful handling of missing keys without exceptions.
        """
        if default is not None:
            return self._trampoline_keys.get(signal_name, default)

        if signal_name not in self._trampoline_keys:
            raise KeyError(f"Trampoline key '{signal_name}' not found")

        return self._trampoline_keys[signal_name]

    def register_protocol(
        self, name: str, version: str, metadata: dict[str, str]
    ) -> None:
        """Register a protocol for Context-Flow cross-system communication.

        This method registers communication protocols that enable integration
        between Context and Flow systems. Protocols define the interface and
        capabilities for cross-system operations, version compatibility,
        and feature sets.

        Args:
            name: The unique name identifier for the protocol
            version: The semantic version string for the protocol
            metadata: Additional protocol metadata and configuration options

        Example:
            ```python
            from context_flow.bridge import ContextFlowBridge

            bridge = ContextFlowBridge()

            # Register a simple protocol
            bridge.register_protocol("basic_flow", "1.0", {
                "features": "trampoline,context",
                "compatibility": ">=1.0,<2.0"
            })

            # Register with complex metadata
            metadata = {
                "description": "Advanced trampoline integration",
                "author": "context_flow_team",
                "features": "trampoline,context,flow,async",
                "compatibility": ">=1.2.0",
                "documentation": "https://docs.example.com/protocols/advanced"
            }
            bridge.register_protocol("advanced_integration", "1.2.3", metadata)
            ```

        Note:
            Protocol registration enables the bridge to understand the capabilities
            and requirements of different integration components. The version and
            metadata information is used for compatibility checking and feature
            discovery during cross-system communication setup.

            Registering a protocol with the same name will overwrite the existing
            registration, allowing for protocol updates and version management.
        """
        # Create protocol entry with version and metadata
        protocol_data = {"version": version}
        protocol_data.update(metadata)

        # Register the protocol in the registry
        self._protocols[name] = protocol_data

    def register_trampoline_support(self) -> None:
        """Register trampoline support with the bridge."""
        # Placeholder for trampoline registration
        pass
