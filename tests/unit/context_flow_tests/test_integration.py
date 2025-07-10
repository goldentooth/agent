"""Integration tests to verify all context_flow components work together."""

import pytest

from context_flow.integration import (
    ContextFlowCombinators,
    ContextFlowError,
    ContextTypeMismatchError,
    MissingRequiredKeyError,
    _single_item_stream,
    context_flow,
    extend_flow_with_context,
    run_flow_with_input,
)
from flow.flow import Flow


class TestContextFlowIntegration:
    """Integration tests for context_flow components."""

    def test_all_components_importable(self) -> None:
        """Test that all components can be imported successfully."""
        # This test ensures all components are properly accessible
        assert ContextFlowError is not None
        assert MissingRequiredKeyError is not None
        assert ContextTypeMismatchError is not None
        assert _single_item_stream is not None
        assert run_flow_with_input is not None
        assert extend_flow_with_context is not None
        assert context_flow is not None
        assert ContextFlowCombinators is not None
        assert Flow is not None

    def test_end_to_end_context_flow_usage(self) -> None:
        """Test end-to-end usage of context_flow components."""
        from context.key import ContextKey
        from context.main import Context

        # Create context and key
        context = Context()
        name_key: ContextKey[str] = ContextKey("user.name", str, "User's name")
        context["user.name"] = "Alice"

        # Use ContextFlowCombinators to get value
        get_name_flow = ContextFlowCombinators.get_key(name_key)
        result = run_flow_with_input(get_name_flow, context)

        assert result == "Alice"

    def test_context_flow_decorator_with_combinators(self) -> None:
        """Test that context_flow decorator works with ContextFlowCombinators."""
        from context.key import ContextKey
        from context.main import Context

        # Create a context-aware flow using the decorator
        @context_flow()
        async def process_with_context(item: str, context: Context) -> str:
            # Use combinators inside the flow
            name_key: ContextKey[str] = ContextKey("user.name", str, "User's name")
            context["user.name"] = "Bob"

            # Get value using combinators directly (avoid nested run_flow_with_input)
            get_name_flow = ContextFlowCombinators.get_key(name_key)
            # Run the flow directly with async for instead of run_flow_with_input
            async for name in get_name_flow(_single_item_stream(context)):
                return f"{item} processed by {name}"

            return f"{item} processed by unknown"

        # Test the integrated flow
        result = run_flow_with_input(process_with_context, "data")
        assert result == "data processed by Bob"

    def test_flow_extension_with_combinators(self) -> None:
        """Test that flow extensions work with ContextFlowCombinators."""
        from context.key import ContextKey
        from context.main import Context

        # Extend Flow with context methods
        extend_flow_with_context()

        # Create context and key
        context = Context()
        status_key: ContextKey[str] = ContextKey("status", str, "Status message")
        context["status"] = "active"

        # Use flow extension and combinators together
        get_status_flow = ContextFlowCombinators.get_key(status_key)
        result = get_status_flow.run(context)  # type: ignore[attr-defined]

        assert result == "active"

    def test_error_handling_integration(self) -> None:
        """Test that error handling works across all components."""
        from context.key import ContextKey
        from context.main import Context

        # Test MissingRequiredKeyError propagation
        context = Context()
        missing_key: ContextKey[str] = ContextKey("missing", str, "Missing key")

        get_missing_flow = ContextFlowCombinators.get_key(missing_key)

        with pytest.raises(MissingRequiredKeyError):
            run_flow_with_input(get_missing_flow, context)

        # Test ContextTypeMismatchError propagation
        type_key: ContextKey[int] = ContextKey("number", int, "Number key")
        context["number"] = "not_a_number"

        get_number_flow = ContextFlowCombinators.get_key(type_key)

        with pytest.raises(ContextTypeMismatchError):
            run_flow_with_input(get_number_flow, context)
