"""Tests for context_flow.trampoline TrampolineFlowCombinators.clear_break_flag method."""

from typing import Any

import pytest

from context.main import Context
from context_flow.trampoline import SHOULD_BREAK_KEY


class TestTrampolineFlowCombinatorsClearBreakFlag:
    """Test cases for TrampolineFlowCombinators.clear_break_flag method."""

    def test_clear_break_flag_import(self) -> None:
        """Test that TrampolineFlowCombinators.clear_break_flag can be imported."""
        # This test will fail until clear_break_flag is implemented
        from context_flow.trampoline import TrampolineFlowCombinators

        # Verify the class exists and has the method
        assert hasattr(TrampolineFlowCombinators, "clear_break_flag")
        assert callable(getattr(TrampolineFlowCombinators, "clear_break_flag"))

    def test_clear_break_flag_method_signature(self) -> None:
        """Test that clear_break_flag has correct method signature."""
        import inspect

        from context_flow.trampoline import TrampolineFlowCombinators

        # Get method signature
        method = getattr(TrampolineFlowCombinators, "clear_break_flag")
        signature = inspect.signature(method)

        # Check that it has no parameters (static method)
        params = list(signature.parameters.keys())
        assert len(params) == 0

    def test_clear_break_flag_returns_flow(self) -> None:
        """Test that clear_break_flag returns a Flow object."""
        from context_flow.trampoline import TrampolineFlowCombinators
        from flow.flow import Flow

        # Test that it returns a Flow
        flow = TrampolineFlowCombinators.clear_break_flag()
        assert isinstance(flow, Flow)

    def test_clear_break_flag_clears_existing_flag(self) -> None:
        """Test that clear_break_flag sets flag to False when it was True."""
        from context_flow.integration import run_flow_with_input
        from context_flow.trampoline import TrampolineFlowCombinators

        # Create context with break flag set to True
        context = Context()
        context[SHOULD_BREAK_KEY.path] = True

        # Create flow to clear break flag
        flow = TrampolineFlowCombinators.clear_break_flag()

        # Execute flow - should set flag to False
        result_context = run_flow_with_input(flow, context)
        assert result_context[SHOULD_BREAK_KEY.path] is False

    def test_clear_break_flag_sets_false_when_missing(self) -> None:
        """Test that clear_break_flag sets flag to False when it was missing."""
        from context_flow.integration import run_flow_with_input
        from context_flow.trampoline import TrampolineFlowCombinators

        # Create context without break flag
        context = Context()

        # Create flow to clear break flag
        flow = TrampolineFlowCombinators.clear_break_flag()

        # Execute flow - should set flag to False
        result_context = run_flow_with_input(flow, context)
        assert result_context[SHOULD_BREAK_KEY.path] is False

    def test_clear_break_flag_keeps_false_when_already_false(self) -> None:
        """Test that clear_break_flag keeps flag False when it was already False."""
        from context_flow.integration import run_flow_with_input
        from context_flow.trampoline import TrampolineFlowCombinators

        # Create context with break flag set to False
        context = Context()
        context[SHOULD_BREAK_KEY.path] = False

        # Create flow to clear break flag
        flow = TrampolineFlowCombinators.clear_break_flag()

        # Execute flow - should keep flag as False
        result_context = run_flow_with_input(flow, context)
        assert result_context[SHOULD_BREAK_KEY.path] is False

    def test_clear_break_flag_preserves_other_context_data(self) -> None:
        """Test that clear_break_flag preserves other context data."""
        from context_flow.integration import run_flow_with_input
        from context_flow.trampoline import TrampolineFlowCombinators

        # Create context with other data and break flag
        context = Context()
        context["test_key"] = "test_value"
        context["number"] = 42
        context[SHOULD_BREAK_KEY.path] = True

        # Create and execute flow
        flow = TrampolineFlowCombinators.clear_break_flag()
        result_context = run_flow_with_input(flow, context)

        # Check that other data is preserved
        assert result_context["test_key"] == "test_value"
        assert result_context["number"] == 42
        assert result_context[SHOULD_BREAK_KEY.path] is False

    def test_clear_break_flag_static_method(self) -> None:
        """Test that clear_break_flag is a static method."""
        from context_flow.trampoline import TrampolineFlowCombinators

        # Should be able to call without instantiating the class
        flow = TrampolineFlowCombinators.clear_break_flag()
        assert flow is not None

        # Method should be static
        method = getattr(TrampolineFlowCombinators, "clear_break_flag")
        assert isinstance(method, staticmethod) or not hasattr(method, "__self__")

    def test_clear_break_flag_flow_composition(self) -> None:
        """Test that clear_break_flag flows can be composed with other flows."""
        from context_flow.trampoline import TrampolineFlowCombinators
        from flow.flow import Flow

        # Create a flow that sets break flag
        set_break_flow = TrampolineFlowCombinators.set_should_break(True)

        # Create a flow that clears break flag
        clear_break_flow = TrampolineFlowCombinators.clear_break_flag()

        # Compose flows: set flag then clear flag
        composed_flow = set_break_flow >> clear_break_flow

        # Create context
        context = Context()

        # Execute composed flow
        result_generator = composed_flow(self._async_iter_from_context(context))
        result_context = self._get_first_result(result_generator)

        # Should have flag cleared (False)
        assert result_context[SHOULD_BREAK_KEY.path] is False

    def test_clear_break_flag_equivalent_to_set_false(self) -> None:
        """Test that clear_break_flag is equivalent to set_should_break(False)."""
        from context_flow.integration import run_flow_with_input
        from context_flow.trampoline import TrampolineFlowCombinators

        # Create context with break flag set to True
        context1 = Context()
        context1[SHOULD_BREAK_KEY.path] = True
        context2 = Context()
        context2[SHOULD_BREAK_KEY.path] = True

        # Test clear_break_flag
        clear_flow = TrampolineFlowCombinators.clear_break_flag()
        result1 = run_flow_with_input(clear_flow, context1)

        # Test set_should_break(False)
        set_false_flow = TrampolineFlowCombinators.set_should_break(False)
        result2 = run_flow_with_input(set_false_flow, context2)

        # Results should be equivalent
        assert result1[SHOULD_BREAK_KEY.path] == result2[SHOULD_BREAK_KEY.path]
        assert result1[SHOULD_BREAK_KEY.path] is False

    def test_clear_break_flag_multiple_executions(self) -> None:
        """Test that clear_break_flag can be executed multiple times."""
        from context_flow.trampoline import TrampolineFlowCombinators

        flow = TrampolineFlowCombinators.clear_break_flag()

        # Test scenarios with different initial flag states
        test_cases = [
            (True, "flag True"),
            (False, "flag False"),
            (None, "missing flag"),
        ]

        for initial_value, description in test_cases:
            context = Context()
            if initial_value is not None:
                context[SHOULD_BREAK_KEY.path] = initial_value

            result_generator = flow(self._async_iter_from_context(context))
            result = self._get_first_result(result_generator)
            assert result[SHOULD_BREAK_KEY.path] is False, f"Failed for {description}"

    def test_clear_break_flag_documentation(self) -> None:
        """Test that clear_break_flag has proper documentation."""
        from context_flow.trampoline import TrampolineFlowCombinators

        method = getattr(TrampolineFlowCombinators, "clear_break_flag")
        assert method.__doc__ is not None
        assert len(method.__doc__.strip()) > 0
        assert "clear" in method.__doc__.lower()
        assert "break" in method.__doc__.lower()

    def test_clear_break_flag_flow_naming(self) -> None:
        """Test that clear_break_flag creates flows with descriptive names."""
        from context_flow.trampoline import TrampolineFlowCombinators

        # Create flow
        flow = TrampolineFlowCombinators.clear_break_flag()

        # Check that flow has a name (for debugging)
        assert hasattr(flow, "name")
        assert isinstance(flow.name, str)
        assert len(flow.name) > 0

    def test_clear_break_flag_context_immutability(self) -> None:
        """Test that clear_break_flag maintains context immutability."""
        from context_flow.integration import run_flow_with_input
        from context_flow.trampoline import TrampolineFlowCombinators

        # Create original context
        original_context = Context()
        original_context[SHOULD_BREAK_KEY.path] = True

        # Store original state
        original_flag_value = original_context[SHOULD_BREAK_KEY.path]

        # Create and execute flow
        flow = TrampolineFlowCombinators.clear_break_flag()
        result_context = run_flow_with_input(flow, original_context)

        # Original context should remain unchanged
        assert original_context[SHOULD_BREAK_KEY.path] == original_flag_value
        assert original_context[SHOULD_BREAK_KEY.path] is True

        # Result context should have cleared flag
        assert result_context[SHOULD_BREAK_KEY.path] is False

        # Should be different context objects
        assert original_context is not result_context

    def test_clear_break_flag_integration_with_checkers(self) -> None:
        """Test that clear_break_flag works with break flag checkers."""
        from context_flow.trampoline import TrampolineFlowCombinators
        from flow.flow import Flow

        # Create flows
        set_break_flow = TrampolineFlowCombinators.set_should_break(True)
        clear_break_flow = TrampolineFlowCombinators.clear_break_flag()
        check_break_flow = TrampolineFlowCombinators.check_should_break()

        # Create integration flow: set -> check -> clear -> check
        integration_flow = (
            set_break_flow
            >> check_break_flow
            >> Flow.identity().map(
                lambda should_break: should_break
            )  # Pass through the boolean
            >> Flow.from_sync_fn(
                lambda _: Context()
            )  # Create fresh context for next step
            >> set_break_flow  # Set break flag again
            >> clear_break_flow  # Clear it
            >> check_break_flow  # Check final state
        )

        # Execute integration flow
        context = Context()
        result_generator = integration_flow(self._async_iter_from_context(context))
        final_result = self._get_first_result(result_generator)

        # Final result should be False (flag cleared)
        assert final_result is False

    # Helper methods for async testing
    def _async_iter_from_context(self, context: Context) -> Any:
        """Helper to create async iterator from context."""

        async def _async_gen() -> Any:
            try:
                yield context
            finally:
                # Explicit cleanup
                pass

        return _async_gen()

    def _get_first_result(self, async_generator: Any) -> Any:
        """Helper to get first result from async generator."""
        import asyncio
        import warnings

        async def _get_result() -> Any:
            try:
                async for result in async_generator:
                    return result
                raise RuntimeError("No result from flow")
            finally:
                # Ensure async generator is properly closed
                if hasattr(async_generator, "aclose"):
                    await async_generator.aclose()

        # Suppress ResourceWarnings during test cleanup
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", category=ResourceWarning)
            # Use asyncio.run with proper cleanup
            try:
                return asyncio.run(_get_result())
            finally:
                # Force cleanup of any remaining async resources
                import gc

                gc.collect()
