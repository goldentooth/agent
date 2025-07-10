"""Tests for context_flow.bridge module."""

import pytest


class TestInitializeContextIntegration:
    """Test cases for initialize_context_integration function."""

    def test_initialize_context_integration_import(self) -> None:
        """Test that initialize_context_integration can be imported."""
        from context_flow.bridge import initialize_context_integration

        # Function should be available
        assert callable(initialize_context_integration)

    def test_initialize_context_integration_basic_functionality(self) -> None:
        """Test that initialize_context_integration executes without error."""
        from context_flow.bridge import initialize_context_integration

        # Should execute without raising exceptions
        initialize_context_integration()

    def test_initialize_context_integration_idempotent(self) -> None:
        """Test that initialize_context_integration is idempotent."""
        from context_flow.bridge import initialize_context_integration

        # First call should succeed
        initialize_context_integration()

        # Second call should also succeed without issues
        initialize_context_integration()

        # Multiple calls should be safe
        for _ in range(3):
            initialize_context_integration()

    def test_initialize_context_integration_creates_bridge_instance(self) -> None:
        """Test that initialization creates the global bridge instance."""
        from context_flow.bridge import initialize_context_integration

        # Initialize the bridge
        initialize_context_integration()

        # Bridge instance should exist after initialization
        from context_flow.bridge import _bridge_instance

        assert _bridge_instance is not None
        assert hasattr(_bridge_instance, "register_trampoline_support")

        # Store the instance to verify idempotency
        first_instance = _bridge_instance

        # Call again - should be same instance
        initialize_context_integration()

        from context_flow.bridge import _bridge_instance as second_instance

        assert second_instance is first_instance

    def test_initialize_context_integration_sets_up_extensions(self) -> None:
        """Test that initialization sets up Flow and Context extensions."""
        from context_flow.bridge import initialize_context_integration
        from flowengine.flow import Flow

        # Initialize the bridge
        initialize_context_integration()

        # Flow class should have trampoline methods added
        assert hasattr(Flow, "run_single")
        assert hasattr(Flow, "as_single_stream")
        assert hasattr(Flow, "repeat_until")
        assert hasattr(Flow, "exit_on")

        # Methods should be callable
        assert callable(getattr(Flow, "run_single"))
        assert callable(getattr(Flow, "as_single_stream"))
        assert callable(getattr(Flow, "repeat_until"))
        assert callable(getattr(Flow, "exit_on"))

    def test_initialize_context_integration_documentation(self) -> None:
        """Test that initialize_context_integration has proper documentation."""
        from context_flow.bridge import initialize_context_integration

        # Function should have docstring
        assert initialize_context_integration.__doc__ is not None
        assert len(initialize_context_integration.__doc__.strip()) > 0

        # Docstring should describe the function purpose
        docstring = initialize_context_integration.__doc__.lower()
        assert "initialize" in docstring
        assert "bridge" in docstring
        assert "integration" in docstring


class TestGetContextBridge:
    """Test cases for get_context_bridge function."""

    def test_get_context_bridge_import(self) -> None:
        """Test that get_context_bridge can be imported."""
        from context_flow.bridge import get_context_bridge

        # Function should be available
        assert callable(get_context_bridge)

    def test_get_context_bridge_returns_bridge_instance(self) -> None:
        """Test that get_context_bridge returns a ContextFlowBridge instance."""
        from context_flow.bridge import get_context_bridge

        bridge = get_context_bridge()

        # Should return a bridge instance
        assert bridge is not None
        assert hasattr(bridge, "register_trampoline_support")
        assert callable(getattr(bridge, "register_trampoline_support"))

    def test_get_context_bridge_returns_same_instance(self) -> None:
        """Test that get_context_bridge returns the same instance consistently."""
        from context_flow.bridge import get_context_bridge

        bridge1 = get_context_bridge()
        bridge2 = get_context_bridge()

        # Should return the same instance (singleton pattern)
        assert bridge1 is bridge2

    def test_get_context_bridge_initializes_if_needed(self) -> None:
        """Test that get_context_bridge initializes the bridge if not already done."""
        from context_flow.bridge import get_context_bridge

        # Get bridge (should initialize automatically)
        bridge = get_context_bridge()

        # Bridge should be available
        assert bridge is not None

        # Should have initialized the global instance
        from context_flow.bridge import _bridge_instance

        assert _bridge_instance is not None
        assert _bridge_instance is bridge

    def test_get_context_bridge_documentation(self) -> None:
        """Test that get_context_bridge has proper documentation."""
        from context_flow.bridge import get_context_bridge

        # Function should have docstring
        assert get_context_bridge.__doc__ is not None
        assert len(get_context_bridge.__doc__.strip()) > 0

        # Docstring should describe the function purpose
        docstring = get_context_bridge.__doc__.lower()
        assert "get" in docstring or "access" in docstring
        assert "bridge" in docstring
        assert "global" in docstring

    def test_get_context_bridge_type_annotation(self) -> None:
        """Test that get_context_bridge has proper return type annotation."""
        import inspect

        from context_flow.bridge import get_context_bridge

        # Get function signature
        signature = inspect.signature(get_context_bridge)

        # Should have return annotation
        assert signature.return_annotation is not None
        assert "ContextFlowBridge" in str(signature.return_annotation)


class TestContextFlowBridgeInit:
    """Test cases for ContextFlowBridge.__init__ method."""

    def test_context_flow_bridge_init_basic(self) -> None:
        """Test that ContextFlowBridge.__init__ properly initializes the bridge."""
        from context_flow.bridge import ContextFlowBridge

        # Create a new bridge instance
        bridge = ContextFlowBridge()

        # Bridge should be properly initialized
        assert hasattr(bridge, "_initialized")
        assert bridge._initialized is True

        # Bridge should have context key mappings initialized
        assert hasattr(bridge, "_context_keys")
        assert isinstance(bridge._context_keys, dict)

        # Bridge should have trampoline key mappings
        assert hasattr(bridge, "_trampoline_keys")
        assert isinstance(bridge._trampoline_keys, dict)

        # Bridge should have protocol registrations
        assert hasattr(bridge, "_protocols")
        assert isinstance(bridge._protocols, dict)

    def test_context_flow_bridge_init_state(self) -> None:
        """Test that ContextFlowBridge.__init__ sets up proper initial state."""
        from context_flow.bridge import ContextFlowBridge

        bridge = ContextFlowBridge()

        # Should start with empty registrations
        assert len(bridge._context_keys) == 0
        assert len(bridge._trampoline_keys) == 0
        assert len(bridge._protocols) == 0

        # Should be marked as initialized
        assert bridge._initialized is True

    def test_context_flow_bridge_init_multiple_instances(self) -> None:
        """Test that multiple ContextFlowBridge instances can be created independently."""
        from context_flow.bridge import ContextFlowBridge

        bridge1 = ContextFlowBridge()
        bridge2 = ContextFlowBridge()

        # Should be different instances
        assert bridge1 is not bridge2

        # Both should be properly initialized
        assert bridge1._initialized is True
        assert bridge2._initialized is True

        # Should have independent state
        bridge1._context_keys["test"] = "value1"
        bridge2._context_keys["test"] = "value2"

        assert bridge1._context_keys["test"] != bridge2._context_keys["test"]

    def test_context_flow_bridge_init_protocol_support(self) -> None:
        """Test that ContextFlowBridge.__init__ supports protocol registration."""
        from context_flow.bridge import ContextFlowBridge

        bridge = ContextFlowBridge()

        # Should be able to register protocols
        bridge._protocols["test_protocol"] = {"version": "1.0"}

        assert "test_protocol" in bridge._protocols
        assert bridge._protocols["test_protocol"]["version"] == "1.0"

    def test_context_flow_bridge_init_trampoline_keys(self) -> None:
        """Test that ContextFlowBridge.__init__ supports trampoline key management."""
        from context_flow.bridge import ContextFlowBridge

        bridge = ContextFlowBridge()

        # Should be able to register trampoline keys
        bridge._trampoline_keys["should_exit"] = "context_flow.should_exit"
        bridge._trampoline_keys["should_break"] = "context_flow.should_break"

        assert "should_exit" in bridge._trampoline_keys
        assert "should_break" in bridge._trampoline_keys
        assert bridge._trampoline_keys["should_exit"] == "context_flow.should_exit"

    def test_context_flow_bridge_init_documentation(self) -> None:
        """Test that ContextFlowBridge.__init__ has proper documentation."""
        from context_flow.bridge import ContextFlowBridge

        # Method should have docstring
        assert ContextFlowBridge.__init__.__doc__ is not None
        assert len(ContextFlowBridge.__init__.__doc__.strip()) > 0

        # Docstring should describe initialization
        docstring = ContextFlowBridge.__init__.__doc__.lower()
        assert "initialize" in docstring
        assert "bridge" in docstring
