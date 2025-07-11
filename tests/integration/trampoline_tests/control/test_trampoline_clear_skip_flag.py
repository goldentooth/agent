"""Tests for context_flow.trampoline TrampolineFlowCombinators.clear_skip_flag method."""

from typing import Any

import pytest

from context.main import Context
from context_flow.trampoline import SHOULD_SKIP_KEY


class TestTrampolineFlowCombinatorsClearSkipFlag:
    """Test cases for TrampolineFlowCombinators.clear_skip_flag method."""

    def test_clear_skip_flag_import(self) -> None:
        """Test that TrampolineFlowCombinators.clear_skip_flag can be imported."""
        # This test will fail until clear_skip_flag is implemented
        from context_flow.trampoline import TrampolineFlowCombinators

        # Verify the class exists and has the method
        assert hasattr(TrampolineFlowCombinators, "clear_skip_flag")
        assert callable(getattr(TrampolineFlowCombinators, "clear_skip_flag"))

    def test_clear_skip_flag_method_signature(self) -> None:
        """Test that clear_skip_flag has correct method signature."""
        import inspect

        from context_flow.trampoline import TrampolineFlowCombinators

        # Get method signature
        method = getattr(TrampolineFlowCombinators, "clear_skip_flag")
        signature = inspect.signature(method)

        # Check that it has no parameters (static method)
        params = list(signature.parameters.keys())
        assert len(params) == 0

    def test_clear_skip_flag_returns_flow(self) -> None:
        """Test that clear_skip_flag returns a Flow object."""
        from context_flow.trampoline import TrampolineFlowCombinators
        from flow.flow import Flow

        # Test that it returns a Flow
        flow = TrampolineFlowCombinators.clear_skip_flag()
        assert isinstance(flow, Flow)

    def test_clear_skip_flag_clears_existing_flag(self) -> None:
        """Test that clear_skip_flag sets flag to False when it was True."""
        from context_flow.integration import run_flow_with_input
        from context_flow.trampoline import TrampolineFlowCombinators

        # Create context with skip flag set to True
        context = Context()
        context[SHOULD_SKIP_KEY.path] = True

        # Create flow to clear skip flag
        flow = TrampolineFlowCombinators.clear_skip_flag()

        # Execute flow - should set flag to False
        result_context = run_flow_with_input(flow, context)
        assert result_context[SHOULD_SKIP_KEY.path] is False

    def test_clear_skip_flag_sets_false_when_missing(self) -> None:
        """Test that clear_skip_flag sets flag to False when it was missing."""
        from context_flow.integration import run_flow_with_input
        from context_flow.trampoline import TrampolineFlowCombinators

        # Create context without skip flag
        context = Context()

        # Create flow to clear skip flag
        flow = TrampolineFlowCombinators.clear_skip_flag()

        # Execute flow - should set flag to False
        result_context = run_flow_with_input(flow, context)
        assert result_context[SHOULD_SKIP_KEY.path] is False

    def test_clear_skip_flag_keeps_false_when_already_false(self) -> None:
        """Test that clear_skip_flag keeps flag False when it was already False."""
        from context_flow.integration import run_flow_with_input
        from context_flow.trampoline import TrampolineFlowCombinators

        # Create context with skip flag set to False
        context = Context()
        context[SHOULD_SKIP_KEY.path] = False

        # Create flow to clear skip flag
        flow = TrampolineFlowCombinators.clear_skip_flag()

        # Execute flow - should keep flag as False
        result_context = run_flow_with_input(flow, context)
        assert result_context[SHOULD_SKIP_KEY.path] is False

    def test_clear_skip_flag_preserves_other_context_data(self) -> None:
        """Test that clear_skip_flag preserves other context data."""
        from context_flow.integration import run_flow_with_input
        from context_flow.trampoline import TrampolineFlowCombinators

        # Create context with other data and skip flag
        context = Context()
        context["test_key"] = "test_value"
        context["number"] = 42
        context[SHOULD_SKIP_KEY.path] = True

        # Create and execute flow
        flow = TrampolineFlowCombinators.clear_skip_flag()
        result_context = run_flow_with_input(flow, context)

        # Check that other data is preserved
        assert result_context["test_key"] == "test_value"
        assert result_context["number"] == 42
        assert result_context[SHOULD_SKIP_KEY.path] is False

    def test_clear_skip_flag_static_method(self) -> None:
        """Test that clear_skip_flag is a static method."""
        from context_flow.trampoline import TrampolineFlowCombinators

        # Should be able to call without instantiating the class
        flow = TrampolineFlowCombinators.clear_skip_flag()
        assert flow is not None

        # Method should be static
        method = getattr(TrampolineFlowCombinators, "clear_skip_flag")
        assert isinstance(method, staticmethod) or not hasattr(method, "__self__")

    def test_clear_skip_flag_flow_composition(self) -> None:
        """Test that clear_skip_flag flows can be composed with other flows."""
        from context_flow.trampoline import TrampolineFlowCombinators
        from flow.flow import Flow

        # Create a flow that sets skip flag
        set_skip_flow = TrampolineFlowCombinators.set_should_skip(True)

        # Create a flow that clears skip flag
        clear_skip_flow = TrampolineFlowCombinators.clear_skip_flag()

        # Compose flows: set flag then clear flag
        composed_flow = set_skip_flow >> clear_skip_flow

        # Create context
        context = Context()

        # Execute composed flow
        result_generator = composed_flow(self._async_iter_from_context(context))
        result_context = self._get_first_result(result_generator)

        # Should have flag cleared (False)
        assert result_context[SHOULD_SKIP_KEY.path] is False

    def test_clear_skip_flag_equivalent_to_set_false(self) -> None:
        """Test that clear_skip_flag is equivalent to set_should_skip(False)."""
        from context_flow.integration import run_flow_with_input
        from context_flow.trampoline import TrampolineFlowCombinators

        # Create context with skip flag set to True
        context1 = Context()
        context1[SHOULD_SKIP_KEY.path] = True
        context2 = Context()
        context2[SHOULD_SKIP_KEY.path] = True

        # Test clear_skip_flag
        clear_flow = TrampolineFlowCombinators.clear_skip_flag()
        result1 = run_flow_with_input(clear_flow, context1)

        # Test set_should_skip(False)
        set_false_flow = TrampolineFlowCombinators.set_should_skip(False)
        result2 = run_flow_with_input(set_false_flow, context2)

        # Results should be equivalent
        assert result1[SHOULD_SKIP_KEY.path] == result2[SHOULD_SKIP_KEY.path]
        assert result1[SHOULD_SKIP_KEY.path] is False

    def test_clear_skip_flag_multiple_executions(self) -> None:
        """Test that clear_skip_flag can be executed multiple times."""
        from context_flow.trampoline import TrampolineFlowCombinators

        flow = TrampolineFlowCombinators.clear_skip_flag()

        # Test scenarios with different initial flag states
        test_cases = [
            (True, "flag True"),
            (False, "flag False"),
            (None, "missing flag"),
        ]

        for initial_value, description in test_cases:
            context = Context()
            if initial_value is not None:
                context[SHOULD_SKIP_KEY.path] = initial_value

            result_generator = flow(self._async_iter_from_context(context))
            result = self._get_first_result(result_generator)
            assert result[SHOULD_SKIP_KEY.path] is False, f"Failed for {description}"

    def test_clear_skip_flag_documentation(self) -> None:
        """Test that clear_skip_flag has proper documentation."""
        from context_flow.trampoline import TrampolineFlowCombinators

        method = getattr(TrampolineFlowCombinators, "clear_skip_flag")
        assert method.__doc__ is not None
        assert len(method.__doc__.strip()) > 0
        assert "clear" in method.__doc__.lower()
        assert "skip" in method.__doc__.lower()

    def test_clear_skip_flag_flow_naming(self) -> None:
        """Test that clear_skip_flag creates flows with descriptive names."""
        from context_flow.trampoline import TrampolineFlowCombinators

        # Create flow
        flow = TrampolineFlowCombinators.clear_skip_flag()

        # Check that flow has a name (for debugging)
        assert hasattr(flow, "name")
        assert isinstance(flow.name, str)
        assert len(flow.name) > 0

    def test_clear_skip_flag_context_immutability(self) -> None:
        """Test that clear_skip_flag maintains context immutability."""
        from context_flow.integration import run_flow_with_input
        from context_flow.trampoline import TrampolineFlowCombinators

        # Create original context
        original_context = Context()
        original_context[SHOULD_SKIP_KEY.path] = True

        # Store original state
        original_flag_value = original_context[SHOULD_SKIP_KEY.path]

        # Create and execute flow
        flow = TrampolineFlowCombinators.clear_skip_flag()
        result_context = run_flow_with_input(flow, original_context)

        # Original context should remain unchanged
        assert original_context[SHOULD_SKIP_KEY.path] == original_flag_value
        assert original_context[SHOULD_SKIP_KEY.path] is True

        # Result context should have cleared flag
        assert result_context[SHOULD_SKIP_KEY.path] is False

        # Should be different context objects
        assert original_context is not result_context

    def test_clear_skip_flag_integration_with_checkers(self) -> None:
        """Test that clear_skip_flag works with skip flag checkers."""
        from context_flow.trampoline import TrampolineFlowCombinators
        from flow.flow import Flow

        # Create flows
        set_skip_flow = TrampolineFlowCombinators.set_should_skip(True)
        clear_skip_flow = TrampolineFlowCombinators.clear_skip_flag()
        check_skip_flow = TrampolineFlowCombinators.check_should_skip()

        # Create integration flow: set -> check -> clear -> check
        integration_flow = (
            set_skip_flow
            >> check_skip_flow
            >> Flow.identity().map(
                lambda should_skip: should_skip
            )  # Pass through the boolean
            >> Flow.from_sync_fn(
                lambda _: Context()
            )  # Create fresh context for next step
            >> set_skip_flow  # Set skip flag again
            >> clear_skip_flow  # Clear it
            >> check_skip_flow  # Check final state
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
