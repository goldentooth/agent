"""Tests for context_flow.bridge module functions."""

import inspect

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
        from flow.flow import Flow

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
        from context_flow.bridge import get_context_bridge

        # Get function signature
        signature = inspect.signature(get_context_bridge)

        # Should have return annotation
        assert signature.return_annotation is not None
        assert "ContextFlowBridge" in str(signature.return_annotation)
