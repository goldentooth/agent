"""Test cases for Context.as_flow method."""

from typing import Any

import pytest

from context.main import Context
from flowengine.flow import Flow


class TestContextAsFlow:
    """Test cases for Context.as_flow method."""

    def test_as_flow_method_exists(self) -> None:
        """Test that Context has as_flow method."""
        context = Context()
        assert hasattr(context, "as_flow"), "Context should have as_flow method"

    def test_as_flow_returns_flow(self) -> None:
        """Test that as_flow returns a Flow instance."""
        context = Context()
        result = context.as_flow("test_key")
        assert isinstance(result, Flow), "as_flow should return a Flow instance"

    def test_as_flow_with_string_key(self) -> None:
        """Test as_flow with a string key parameter."""
        context = Context()
        flow = context.as_flow("user_id")
        assert isinstance(flow, Flow), "as_flow should work with string keys"

    def test_as_flow_with_use_async_true(self) -> None:
        """Test as_flow with use_async=True (default)."""
        context = Context()
        flow = context.as_flow("test_key", use_async=True)
        assert isinstance(flow, Flow), "as_flow should work with use_async=True"

    def test_as_flow_with_use_async_false(self) -> None:
        """Test as_flow with use_async=False."""
        context = Context()
        flow = context.as_flow("test_key", use_async=False)
        assert isinstance(flow, Flow), "as_flow should work with use_async=False"

    def test_as_flow_emits_on_key_change(self) -> None:
        """Test that as_flow emits values when the key changes."""
        context = Context()
        flow = context.as_flow("test_key")

        # This is a placeholder test - we'll implement the actual behavior later
        # For now, just verify the flow can be created
        assert isinstance(flow, Flow), "Flow should be created successfully"

    def test_as_flow_different_keys_are_independent(self) -> None:
        """Test that flows for different keys are independent."""
        context = Context()
        flow1 = context.as_flow("key1")
        flow2 = context.as_flow("key2")

        assert isinstance(flow1, Flow), "First flow should be created"
        assert isinstance(flow2, Flow), "Second flow should be created"
        assert flow1 is not flow2, "Different keys should create different flows"

    def test_as_flow_same_key_reuse_behavior(self) -> None:
        """Test behavior when calling as_flow with the same key multiple times."""
        context = Context()
        flow1 = context.as_flow("same_key")
        flow2 = context.as_flow("same_key")

        # Both should be Flow instances (implementation detail of reuse is internal)
        assert isinstance(flow1, Flow), "First flow should be created"
        assert isinstance(flow2, Flow), "Second flow should be created"

    def test_as_flow_method_signature(self) -> None:
        """Test that as_flow has the correct method signature."""
        context = Context()

        # Test with positional arguments
        flow1 = context.as_flow("test_key")
        assert isinstance(flow1, Flow)

        # Test with keyword arguments
        flow2 = context.as_flow(key="test_key", use_async=True)
        assert isinstance(flow2, Flow)

        # Test with mixed arguments
        flow3 = context.as_flow("test_key", use_async=False)
        assert isinstance(flow3, Flow)

    def test_as_flow_type_hints(self) -> None:
        """Test that as_flow has proper type hints."""
        context = Context()

        # This test verifies that the method exists and can be called
        # Type checker will verify the actual type annotations
        flow: Flow[None, Any] = context.as_flow("test_key")
        assert isinstance(flow, Flow)
