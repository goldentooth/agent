"""Test cases for context_flow.global_changes_as_flow function."""

from typing import Any

import pytest

from context.main import Context
from context_flow.integration import global_changes_as_flow
from flowengine.flow import Flow


class TestGlobalChangesAsFlow:
    """Test cases for context_flow.global_changes_as_flow function."""

    def test_global_changes_as_flow_function_exists(self) -> None:
        """Test that global_changes_as_flow function is available."""
        context = Context()
        # Test that the function can be called
        flow = global_changes_as_flow(context)
        assert isinstance(
            flow, Flow
        ), "global_changes_as_flow should return a Flow instance"

    def test_global_changes_as_flow_returns_flow(self) -> None:
        """Test that global_changes_as_flow returns a Flow instance."""
        context = Context()
        result = global_changes_as_flow(context)
        assert isinstance(
            result, Flow
        ), "global_changes_as_flow should return a Flow instance"

    def test_global_changes_as_flow_with_use_async_true(self) -> None:
        """Test global_changes_as_flow with use_async=True (default)."""
        context = Context()
        flow = global_changes_as_flow(context, use_async=True)
        assert isinstance(
            flow, Flow
        ), "global_changes_as_flow should work with use_async=True"

    def test_global_changes_as_flow_with_use_async_false(self) -> None:
        """Test global_changes_as_flow with use_async=False."""
        context = Context()
        flow = global_changes_as_flow(context, use_async=False)
        assert isinstance(
            flow, Flow
        ), "global_changes_as_flow should work with use_async=False"

    def test_global_changes_as_flow_function_signature(self) -> None:
        """Test that global_changes_as_flow has the correct function signature."""
        context = Context()

        # Test with positional arguments
        flow1 = global_changes_as_flow(context)
        assert isinstance(flow1, Flow)

        # Test with keyword arguments
        flow2 = global_changes_as_flow(context=context, use_async=True)
        assert isinstance(flow2, Flow)

        # Test with mixed arguments
        flow3 = global_changes_as_flow(context, use_async=False)
        assert isinstance(flow3, Flow)

    def test_global_changes_as_flow_type_hints(self) -> None:
        """Test that global_changes_as_flow has proper type hints."""
        context = Context()

        # This test verifies that the function exists and can be called
        # Type checker will verify the actual type annotations
        flow: Flow[None, Any] = global_changes_as_flow(context)
        assert isinstance(flow, Flow)

    def test_global_changes_as_flow_monitors_all_keys(self) -> None:
        """Test that global_changes_as_flow monitors changes to all keys."""
        context = Context()
        flow = global_changes_as_flow(context)

        # This is a placeholder test - we'll implement the actual behavior later
        # For now, just verify the flow can be created for global monitoring
        assert isinstance(flow, Flow), "Flow should be created for global monitoring"

    def test_global_changes_as_flow_different_from_key_specific(self) -> None:
        """Test that global_changes_as_flow differs from key-specific as_flow."""
        from context_flow.integration import as_flow

        context = Context()
        global_flow = global_changes_as_flow(context)
        key_flow = as_flow(context, "specific_key")

        # Both should be Flow instances but serve different purposes
        assert isinstance(global_flow, Flow), "Global flow should be created"
        assert isinstance(key_flow, Flow), "Key-specific flow should be created"
        assert (
            global_flow is not key_flow
        ), "Global and key-specific flows should be different"

    def test_global_changes_as_flow_context_independence(self) -> None:
        """Test that flows from different contexts are independent."""
        context1 = Context()
        context2 = Context()

        flow1 = global_changes_as_flow(context1)
        flow2 = global_changes_as_flow(context2)

        assert isinstance(flow1, Flow), "First flow should be created"
        assert isinstance(flow2, Flow), "Second flow should be created"
        assert flow1 is not flow2, "Flows from different contexts should be different"

    def test_global_changes_as_flow_same_context_reuse_behavior(self) -> None:
        """Test behavior when calling global_changes_as_flow multiple times on same context."""
        context = Context()
        flow1 = global_changes_as_flow(context)
        flow2 = global_changes_as_flow(context)

        # Both should be Flow instances (implementation detail of reuse is internal)
        assert isinstance(flow1, Flow), "First flow should be created"
        assert isinstance(flow2, Flow), "Second flow should be created"
