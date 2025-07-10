"""Tests for context_flow.bridge ContextFlowBridge class methods."""

import inspect


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


class TestContextFlowBridgeEnsureContextKeys:
    """Test cases for ContextFlowBridge.ensure_context_keys method."""

    def test_ensure_context_keys_import(self) -> None:
        """Test that ensure_context_keys method exists and is callable."""
        from context_flow.bridge import ContextFlowBridge

        bridge = ContextFlowBridge()

        # Method should exist and be callable
        assert hasattr(bridge, "ensure_context_keys")
        assert callable(getattr(bridge, "ensure_context_keys"))

    def test_ensure_context_keys_registers_trampoline_keys(self) -> None:
        """Test that ensure_context_keys registers required trampoline control keys."""
        from context_flow.bridge import ContextFlowBridge

        bridge = ContextFlowBridge()

        # Before calling, trampoline keys should be empty
        assert len(bridge._trampoline_keys) == 0

        # Call ensure_context_keys
        bridge.ensure_context_keys()

        # Should register the standard trampoline control keys
        expected_keys = ["should_exit", "should_break", "should_skip"]
        for key in expected_keys:
            assert key in bridge._trampoline_keys
            assert isinstance(bridge._trampoline_keys[key], str)
            assert len(bridge._trampoline_keys[key]) > 0

    def test_ensure_context_keys_idempotent(self) -> None:
        """Test that ensure_context_keys is idempotent - safe to call multiple times."""
        from context_flow.bridge import ContextFlowBridge

        bridge = ContextFlowBridge()

        # Call multiple times
        bridge.ensure_context_keys()
        first_keys = dict(bridge._trampoline_keys)

        bridge.ensure_context_keys()
        second_keys = dict(bridge._trampoline_keys)

        bridge.ensure_context_keys()
        third_keys = dict(bridge._trampoline_keys)

        # Should be identical across calls
        assert first_keys == second_keys == third_keys

    def test_ensure_context_keys_proper_key_names(self) -> None:
        """Test that ensure_context_keys creates properly formatted key names."""
        from context_flow.bridge import ContextFlowBridge

        bridge = ContextFlowBridge()
        bridge.ensure_context_keys()

        # Keys should follow the expected naming pattern
        assert bridge._trampoline_keys["should_exit"] == "context_flow.should_exit"
        assert bridge._trampoline_keys["should_break"] == "context_flow.should_break"
        assert bridge._trampoline_keys["should_skip"] == "context_flow.should_skip"

    def test_ensure_context_keys_preserves_existing_keys(self) -> None:
        """Test that ensure_context_keys preserves any existing custom keys."""
        from context_flow.bridge import ContextFlowBridge

        bridge = ContextFlowBridge()

        # Add some custom keys first
        bridge._trampoline_keys["custom_key"] = "custom.value"
        bridge._context_keys["user_defined"] = "user.defined.key"

        # Call ensure_context_keys
        bridge.ensure_context_keys()

        # Custom keys should still be present
        assert bridge._trampoline_keys["custom_key"] == "custom.value"
        assert bridge._context_keys["user_defined"] == "user.defined.key"

        # Standard keys should also be present
        assert "should_exit" in bridge._trampoline_keys
        assert "should_break" in bridge._trampoline_keys
        assert "should_skip" in bridge._trampoline_keys

    def test_ensure_context_keys_documentation(self) -> None:
        """Test that ensure_context_keys has proper documentation."""
        from context_flow.bridge import ContextFlowBridge

        bridge = ContextFlowBridge()

        # Method should have docstring
        assert bridge.ensure_context_keys.__doc__ is not None
        assert len(bridge.ensure_context_keys.__doc__.strip()) > 0

        # Docstring should describe the method purpose
        docstring = bridge.ensure_context_keys.__doc__.lower()
        assert "ensure" in docstring or "register" in docstring
        assert "context" in docstring
        assert "key" in docstring


class TestContextFlowBridgeGetTrampolineKey:
    """Test cases for ContextFlowBridge.get_trampoline_key method."""

    def test_get_trampoline_key_import(self) -> None:
        """Test that get_trampoline_key method exists and is callable."""
        from context_flow.bridge import ContextFlowBridge

        bridge = ContextFlowBridge()

        # Method should exist and be callable
        assert hasattr(bridge, "get_trampoline_key")
        assert callable(getattr(bridge, "get_trampoline_key"))

    def test_get_trampoline_key_returns_registered_keys(self) -> None:
        """Test that get_trampoline_key returns properly registered keys."""
        from context_flow.bridge import ContextFlowBridge

        bridge = ContextFlowBridge()
        bridge.ensure_context_keys()

        # Should return the registered trampoline keys
        exit_key = bridge.get_trampoline_key("should_exit")
        break_key = bridge.get_trampoline_key("should_break")
        skip_key = bridge.get_trampoline_key("should_skip")

        assert exit_key == "context_flow.should_exit"
        assert break_key == "context_flow.should_break"
        assert skip_key == "context_flow.should_skip"

    def test_get_trampoline_key_missing_key_raises_error(self) -> None:
        """Test that get_trampoline_key raises KeyError for missing keys."""
        import pytest

        from context_flow.bridge import ContextFlowBridge

        bridge = ContextFlowBridge()

        # Should raise KeyError for missing key
        with pytest.raises(KeyError, match="Trampoline key 'nonexistent' not found"):
            bridge.get_trampoline_key("nonexistent")

    def test_get_trampoline_key_works_with_custom_keys(self) -> None:
        """Test that get_trampoline_key works with custom registered keys."""
        from context_flow.bridge import ContextFlowBridge

        bridge = ContextFlowBridge()

        # Register custom key
        bridge._trampoline_keys["custom_signal"] = "custom.signal.key"

        # Should return the custom key
        custom_key = bridge.get_trampoline_key("custom_signal")
        assert custom_key == "custom.signal.key"

    def test_get_trampoline_key_with_default_value(self) -> None:
        """Test that get_trampoline_key supports default values."""
        from context_flow.bridge import ContextFlowBridge

        bridge = ContextFlowBridge()

        # Should return default value for missing key
        default_key = bridge.get_trampoline_key("missing_key", "default_value")
        assert default_key == "default_value"

        # Should return actual value when key exists
        bridge._trampoline_keys["existing_key"] = "existing.value"
        existing_key = bridge.get_trampoline_key("existing_key", "default_value")
        assert existing_key == "existing.value"

    def test_get_trampoline_key_type_annotations(self) -> None:
        """Test that get_trampoline_key has proper type annotations."""
        from context_flow.bridge import ContextFlowBridge

        bridge = ContextFlowBridge()

        # Get method signature
        signature = inspect.signature(bridge.get_trampoline_key)

        # Should have proper parameter annotations
        params = signature.parameters
        assert "signal_name" in params
        assert "default" in params

        # Should have return annotation
        assert signature.return_annotation is not None

    def test_get_trampoline_key_documentation(self) -> None:
        """Test that get_trampoline_key has proper documentation."""
        from context_flow.bridge import ContextFlowBridge

        bridge = ContextFlowBridge()

        # Method should have docstring
        assert bridge.get_trampoline_key.__doc__ is not None
        assert len(bridge.get_trampoline_key.__doc__.strip()) > 0

        # Docstring should describe the method purpose
        docstring = bridge.get_trampoline_key.__doc__.lower()
        assert "get" in docstring or "retrieve" in docstring
        assert "trampoline" in docstring
        assert "key" in docstring
