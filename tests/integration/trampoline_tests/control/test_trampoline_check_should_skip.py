"""Tests for context_flow.trampoline TrampolineFlowCombinators.check_should_skip method."""

from typing import Any

import pytest

from context.main import Context
from context_flow.trampoline import SHOULD_SKIP_KEY


class TestTrampolineFlowCombinatorsCheckShouldSkip:
    """Test cases for TrampolineFlowCombinators.check_should_skip method."""

    def test_check_should_skip_import(self) -> None:
        """Test that TrampolineFlowCombinators.check_should_skip can be imported."""
        # This test will fail until check_should_skip is implemented
        from context_flow.trampoline import TrampolineFlowCombinators

        # Verify the class exists and has the method
        assert hasattr(TrampolineFlowCombinators, "check_should_skip")
        assert callable(getattr(TrampolineFlowCombinators, "check_should_skip"))

    def test_check_should_skip_method_signature(self) -> None:
        """Test that check_should_skip has correct method signature."""
        import inspect

        from context_flow.trampoline import TrampolineFlowCombinators

        # Get method signature
        method = getattr(TrampolineFlowCombinators, "check_should_skip")
        signature = inspect.signature(method)

        # Check that it has no parameters (static method)
        params = list(signature.parameters.keys())
        assert len(params) == 0

    def test_check_should_skip_returns_flow(self) -> None:
        """Test that check_should_skip returns a Flow object."""
        from context_flow.trampoline import TrampolineFlowCombinators
        from flowengine.flow import Flow

        # Test that it returns a Flow
        flow = TrampolineFlowCombinators.check_should_skip()
        assert isinstance(flow, Flow)

    def test_check_should_skip_with_flag_true(self) -> None:
        """Test that check_should_skip returns True when flag is set."""
        from context_flow.integration import run_flow_with_input
        from context_flow.trampoline import TrampolineFlowCombinators

        # Create context with skip flag set to True
        context = Context()
        context[SHOULD_SKIP_KEY.path] = True

        # Create flow to check skip flag
        flow = TrampolineFlowCombinators.check_should_skip()

        # Execute flow - should return True
        result = run_flow_with_input(flow, context)
        assert result is True

    def test_check_should_skip_with_flag_false(self) -> None:
        """Test that check_should_skip returns False when flag is False."""
        from context_flow.integration import run_flow_with_input
        from context_flow.trampoline import TrampolineFlowCombinators

        # Create context with skip flag set to False
        context = Context()
        context[SHOULD_SKIP_KEY.path] = False

        # Create flow to check skip flag
        flow = TrampolineFlowCombinators.check_should_skip()

        # Execute flow - should return False
        result = run_flow_with_input(flow, context)
        assert result is False

    def test_check_should_skip_with_flag_missing(self) -> None:
        """Test that check_should_skip returns False when flag is missing."""
        from context_flow.integration import run_flow_with_input
        from context_flow.trampoline import TrampolineFlowCombinators

        # Create context without skip flag
        context = Context()

        # Create flow to check skip flag
        flow = TrampolineFlowCombinators.check_should_skip()

        # Execute flow - should return False (default)
        result = run_flow_with_input(flow, context)
        assert result is False

    def test_check_should_skip_preserves_context(self) -> None:
        """Test that check_should_skip preserves the original context."""
        from context_flow.trampoline import TrampolineFlowCombinators

        # Create context with some data and skip flag
        context = Context()
        context["test_key"] = "test_value"
        context[SHOULD_SKIP_KEY.path] = True

        # Create and execute flow
        flow = TrampolineFlowCombinators.check_should_skip()
        result_generator = flow(self._async_iter_from_context(context))

        # The flow should yield the boolean result, not context
        result = self._get_first_result(result_generator)
        assert result is True

    def test_check_should_skip_static_method(self) -> None:
        """Test that check_should_skip is a static method."""
        from context_flow.trampoline import TrampolineFlowCombinators

        # Should be able to call without instantiating the class
        flow = TrampolineFlowCombinators.check_should_skip()
        assert flow is not None

        # Method should be static
        method = getattr(TrampolineFlowCombinators, "check_should_skip")
        assert isinstance(method, staticmethod) or not hasattr(method, "__self__")

    def test_check_should_skip_flow_composition(self) -> None:
        """Test that check_should_skip flows can be composed with other flows."""
        from context_flow.trampoline import TrampolineFlowCombinators
        from flowengine.flow import Flow

        # Create a flow that sets skip flag
        set_skip_flow = TrampolineFlowCombinators.set_should_skip(True)

        # Create a flow that checks skip flag
        check_skip_flow = TrampolineFlowCombinators.check_should_skip()

        # Compose flows: set flag then check flag
        composed_flow = set_skip_flow >> check_skip_flow

        # Create context
        context = Context()

        # Execute composed flow
        result_generator = composed_flow(self._async_iter_from_context(context))
        result = self._get_first_result(result_generator)

        # Should return True since we set the flag
        assert result is True

    def test_check_should_skip_multiple_executions(self) -> None:
        """Test that check_should_skip can be executed multiple times."""
        from context_flow.trampoline import TrampolineFlowCombinators

        # Create flow
        flow = TrampolineFlowCombinators.check_should_skip()

        # Test with flag True
        context_true = Context()
        context_true[SHOULD_SKIP_KEY.path] = True
        result_generator = flow(self._async_iter_from_context(context_true))
        result = self._get_first_result(result_generator)
        assert result is True

        # Test with flag False
        context_false = Context()
        context_false[SHOULD_SKIP_KEY.path] = False
        result_generator = flow(self._async_iter_from_context(context_false))
        result = self._get_first_result(result_generator)
        assert result is False

    def test_check_should_skip_documentation(self) -> None:
        """Test that check_should_skip has proper documentation."""
        from context_flow.trampoline import TrampolineFlowCombinators

        method = getattr(TrampolineFlowCombinators, "check_should_skip")
        assert method.__doc__ is not None
        assert len(method.__doc__.strip()) > 0
        assert "check" in method.__doc__.lower()
        assert "skip" in method.__doc__.lower()

    def test_check_should_skip_type_consistency(self) -> None:
        """Test that check_should_skip always returns boolean values."""
        from context_flow.trampoline import TrampolineFlowCombinators

        # Create flow
        flow = TrampolineFlowCombinators.check_should_skip()

        # Test with various context states
        test_cases = []

        # No flag
        context_no_flag = Context()
        test_cases.append((context_no_flag, False))

        # Flag True
        context_flag_true = Context()
        context_flag_true[SHOULD_SKIP_KEY.path] = True
        test_cases.append((context_flag_true, True))

        # Flag False
        context_flag_false = Context()
        context_flag_false[SHOULD_SKIP_KEY.path] = False
        test_cases.append((context_flag_false, False))

        for context, expected in test_cases:
            result_generator = flow(self._async_iter_from_context(context))
            result = self._get_first_result(result_generator)
            assert isinstance(result, bool)
            assert result == expected

    def test_check_should_skip_flow_naming(self) -> None:
        """Test that check_should_skip creates flows with descriptive names."""
        from context_flow.trampoline import TrampolineFlowCombinators

        # Create flow
        flow = TrampolineFlowCombinators.check_should_skip()

        # Check that flow has a name (for debugging)
        assert hasattr(flow, "name")
        assert isinstance(flow.name, str)
        assert len(flow.name) > 0

    def test_check_should_skip_error_handling(self) -> None:
        """Test that check_should_skip handles errors gracefully."""
        from context_flow.trampoline import TrampolineFlowCombinators

        # Create flow
        flow = TrampolineFlowCombinators.check_should_skip()

        # Test with empty context
        empty_context = Context()
        result_generator = flow(self._async_iter_from_context(empty_context))
        result = self._get_first_result(result_generator)

        # Should return False (default) without error
        assert result is False

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
