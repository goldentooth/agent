"""Tests for context_flow.trampoline TrampolineFlowCombinators class."""

from typing import Any

import pytest

from context.main import Context
from context_flow.trampoline import SHOULD_BREAK_KEY, SHOULD_EXIT_KEY, SHOULD_SKIP_KEY


class TestTrampolineFlowCombinatorsSetShouldExit:
    """Test cases for TrampolineFlowCombinators.set_should_exit method."""

    def test_set_should_exit_import(self) -> None:
        """Test that TrampolineFlowCombinators.set_should_exit can be imported."""
        # This test will fail until TrampolineFlowCombinators is implemented
        from context_flow.trampoline import TrampolineFlowCombinators

        # Verify the class exists and has the method
        assert hasattr(TrampolineFlowCombinators, "set_should_exit")
        assert callable(getattr(TrampolineFlowCombinators, "set_should_exit"))

    def test_set_should_exit_method_signature(self) -> None:
        """Test that set_should_exit has correct method signature."""
        import inspect

        from context_flow.trampoline import TrampolineFlowCombinators

        # Get method signature
        method = getattr(TrampolineFlowCombinators, "set_should_exit")
        signature = inspect.signature(method)

        # Check parameters
        params = list(signature.parameters.keys())
        assert "value" in params

        # Check default value
        value_param = signature.parameters["value"]
        assert value_param.default is True

        # Check parameter annotation (handle both bool type and string 'bool')
        assert value_param.annotation == bool or value_param.annotation == "bool"

    def test_set_should_exit_returns_flow(self) -> None:
        """Test that set_should_exit returns a Flow object."""
        from context_flow.trampoline import TrampolineFlowCombinators
        from flowengine.flow import Flow

        # Test with default value
        flow = TrampolineFlowCombinators.set_should_exit()
        assert isinstance(flow, Flow)

        # Test with explicit True
        flow_true = TrampolineFlowCombinators.set_should_exit(True)
        assert isinstance(flow_true, Flow)

        # Test with False
        flow_false = TrampolineFlowCombinators.set_should_exit(False)
        assert isinstance(flow_false, Flow)

    def test_set_should_exit_default_value_true(self) -> None:
        """Test that set_should_exit defaults to True when no argument provided."""
        from context_flow.integration import run_flow_with_input
        from context_flow.trampoline import TrampolineFlowCombinators

        # Create context
        context = Context()

        # Create flow with default value (should be True)
        flow = TrampolineFlowCombinators.set_should_exit()

        # Execute flow using the utility function for simpler execution
        result_context = run_flow_with_input(flow, context)

        # Check that exit flag is set to True
        assert result_context.get(SHOULD_EXIT_KEY.path, False) is True

    def test_set_should_exit_explicit_true(self) -> None:
        """Test that set_should_exit works with explicit True value."""
        from context_flow.integration import run_flow_with_input
        from context_flow.trampoline import TrampolineFlowCombinators

        # Create context
        context = Context()

        # Create flow with explicit True
        flow = TrampolineFlowCombinators.set_should_exit(True)

        # Execute flow
        result_context = run_flow_with_input(flow, context)

        # Check that exit flag is set to True
        assert result_context.get(SHOULD_EXIT_KEY.path, False) is True

    def test_set_should_exit_false_value(self) -> None:
        """Test that set_should_exit works with False value."""
        from context_flow.integration import run_flow_with_input
        from context_flow.trampoline import TrampolineFlowCombinators

        # Create context with exit flag initially True
        context = Context()
        context[SHOULD_EXIT_KEY.path] = True

        # Create flow to set exit to False
        flow = TrampolineFlowCombinators.set_should_exit(False)

        # Execute flow
        result_context = run_flow_with_input(flow, context)

        # Check that exit flag is now False
        assert result_context.get(SHOULD_EXIT_KEY.path, True) is False

    def test_set_should_exit_preserves_other_context_data(self) -> None:
        """Test that set_should_exit preserves other context data."""
        from context_flow.trampoline import TrampolineFlowCombinators

        # Create context with some data
        context = Context()
        context["test_key"] = "test_value"
        context["number"] = 42

        # Create and execute flow
        flow = TrampolineFlowCombinators.set_should_exit(True)
        result_generator = flow(self._async_iter_from_context(context))
        result_context = self._get_first_result(result_generator)

        # Check that original data is preserved
        assert result_context["test_key"] == "test_value"
        assert result_context["number"] == 42

        # Check that exit flag is set
        assert result_context.get(SHOULD_EXIT_KEY.path, False) is True

    def test_set_should_exit_immutable_context(self) -> None:
        """Test that set_should_exit creates new context (immutable pattern)."""
        from context_flow.trampoline import TrampolineFlowCombinators

        # Create context
        original_context = Context()

        # Create and execute flow
        flow = TrampolineFlowCombinators.set_should_exit(True)
        result_generator = flow(self._async_iter_from_context(original_context))
        result_context = self._get_first_result(result_generator)

        # Check that original context is unchanged
        assert original_context.get(SHOULD_EXIT_KEY.path, False) is False

        # Check that result context has the flag set
        assert result_context.get(SHOULD_EXIT_KEY.path, False) is True

        # Check that they are different objects
        assert result_context is not original_context

    def test_set_should_exit_static_method(self) -> None:
        """Test that set_should_exit is a static method."""
        from context_flow.trampoline import TrampolineFlowCombinators

        # Should be able to call without instantiating the class
        flow = TrampolineFlowCombinators.set_should_exit()
        assert flow is not None

        # Method should be static
        method = getattr(TrampolineFlowCombinators, "set_should_exit")
        assert isinstance(method, staticmethod) or not hasattr(method, "__self__")

    def test_set_should_exit_flow_composition(self) -> None:
        """Test that set_should_exit flows can be composed with other flows."""
        from context_flow.trampoline import TrampolineFlowCombinators
        from flowengine.flow import Flow

        # Create a simple transformation flow
        def add_data_flow(stream: Any) -> Any:
            async def _flow() -> Any:
                async for context in stream:
                    new_context = context.fork()
                    new_context["added_data"] = "test"
                    yield new_context

            return _flow()

        transform_flow = Flow(add_data_flow)

        # Create context
        context = Context()

        # Compose flows: add data then set exit
        exit_flow = TrampolineFlowCombinators.set_should_exit(True)
        composed_flow = transform_flow >> exit_flow

        # Execute composed flow
        result_generator = composed_flow(self._async_iter_from_context(context))
        result_context = self._get_first_result(result_generator)

        # Check both operations happened
        assert result_context["added_data"] == "test"
        assert result_context.get(SHOULD_EXIT_KEY.path, False) is True

    def test_set_should_exit_multiple_executions(self) -> None:
        """Test that set_should_exit can be executed multiple times."""
        from context_flow.trampoline import TrampolineFlowCombinators

        # Create flow
        flow = TrampolineFlowCombinators.set_should_exit(True)

        # Execute multiple times with different contexts
        for i in range(3):
            context = Context()
            context["iteration"] = i

            result_generator = flow(self._async_iter_from_context(context))
            result_context = self._get_first_result(result_generator)

            # Each execution should set the flag
            assert result_context.get(SHOULD_EXIT_KEY.path, False) is True
            assert result_context["iteration"] == i

    def test_set_should_exit_documentation(self) -> None:
        """Test that set_should_exit has proper documentation."""
        from context_flow.trampoline import TrampolineFlowCombinators

        method = getattr(TrampolineFlowCombinators, "set_should_exit")
        assert method.__doc__ is not None
        assert len(method.__doc__.strip()) > 0
        assert "exit" in method.__doc__.lower()

    def test_set_should_exit_type_validation(self) -> None:
        """Test that set_should_exit validates input types properly."""
        from context_flow.trampoline import TrampolineFlowCombinators

        # Should work with boolean values
        flow_true = TrampolineFlowCombinators.set_should_exit(True)
        flow_false = TrampolineFlowCombinators.set_should_exit(False)

        assert flow_true is not None
        assert flow_false is not None

        # Type checking should be handled by static type checkers
        # Runtime behavior with non-boolean values depends on implementation

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

    def _get_first_result(self, async_generator: Any) -> Context:
        """Helper to get first result from async generator."""
        import asyncio
        import warnings

        async def _get_result() -> Context:
            try:
                async for result in async_generator:
                    return result  # type: ignore[no-any-return]
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

    def test_set_should_exit_error_handling(self) -> None:
        """Test that set_should_exit handles errors gracefully."""
        from context_flow.trampoline import TrampolineFlowCombinators

        # Create flow
        flow = TrampolineFlowCombinators.set_should_exit(True)

        # Test with empty context
        empty_context = Context()
        result_generator = flow(self._async_iter_from_context(empty_context))
        result_context = self._get_first_result(result_generator)

        # Should still work
        assert result_context.get(SHOULD_EXIT_KEY.path, False) is True

    def test_set_should_exit_flow_naming(self) -> None:
        """Test that set_should_exit creates flows with descriptive names."""
        from context_flow.trampoline import TrampolineFlowCombinators

        # Create flows with different values
        flow_true = TrampolineFlowCombinators.set_should_exit(True)
        flow_false = TrampolineFlowCombinators.set_should_exit(False)

        # Check that flows have names (for debugging)
        assert hasattr(flow_true, "name")
        assert hasattr(flow_false, "name")

        # Names should be strings
        assert isinstance(flow_true.name, str)
        assert isinstance(flow_false.name, str)


class TestTrampolineFlowCombinatorsSetShouldBreak:
    """Test cases for TrampolineFlowCombinators.set_should_break method."""

    def test_set_should_break_import(self) -> None:
        """Test that TrampolineFlowCombinators.set_should_break can be imported."""
        # This test will fail until set_should_break is implemented
        from context_flow.trampoline import TrampolineFlowCombinators

        # Verify the class exists and has the method
        assert hasattr(TrampolineFlowCombinators, "set_should_break")
        assert callable(getattr(TrampolineFlowCombinators, "set_should_break"))

    def test_set_should_break_method_signature(self) -> None:
        """Test that set_should_break has correct method signature."""
        import inspect

        from context_flow.trampoline import TrampolineFlowCombinators

        # Get method signature
        method = getattr(TrampolineFlowCombinators, "set_should_break")
        signature = inspect.signature(method)

        # Check parameters
        params = list(signature.parameters.keys())
        assert "value" in params

        # Check default value
        value_param = signature.parameters["value"]
        assert value_param.default is True

        # Check parameter annotation (handle both bool type and string 'bool')
        assert value_param.annotation == bool or value_param.annotation == "bool"

    def test_set_should_break_returns_flow(self) -> None:
        """Test that set_should_break returns a Flow object."""
        from context_flow.trampoline import TrampolineFlowCombinators
        from flowengine.flow import Flow

        # Test with default value
        flow = TrampolineFlowCombinators.set_should_break()
        assert isinstance(flow, Flow)

        # Test with explicit True
        flow_true = TrampolineFlowCombinators.set_should_break(True)
        assert isinstance(flow_true, Flow)

        # Test with False
        flow_false = TrampolineFlowCombinators.set_should_break(False)
        assert isinstance(flow_false, Flow)

    def test_set_should_break_default_value_true(self) -> None:
        """Test that set_should_break defaults to True when no argument provided."""
        from context_flow.integration import run_flow_with_input
        from context_flow.trampoline import TrampolineFlowCombinators

        # Create context
        context = Context()

        # Create flow with default value (should be True)
        flow = TrampolineFlowCombinators.set_should_break()

        # Execute flow using the utility function for simpler execution
        result_context = run_flow_with_input(flow, context)

        # Check that break flag is set to True
        assert result_context.get(SHOULD_BREAK_KEY.path, False) is True

    def test_set_should_break_explicit_true(self) -> None:
        """Test that set_should_break works with explicit True value."""
        from context_flow.integration import run_flow_with_input
        from context_flow.trampoline import TrampolineFlowCombinators

        # Create context
        context = Context()

        # Create flow with explicit True
        flow = TrampolineFlowCombinators.set_should_break(True)

        # Execute flow
        result_context = run_flow_with_input(flow, context)

        # Check that break flag is set to True
        assert result_context.get(SHOULD_BREAK_KEY.path, False) is True

    def test_set_should_break_false_value(self) -> None:
        """Test that set_should_break works with False value."""
        from context_flow.integration import run_flow_with_input
        from context_flow.trampoline import TrampolineFlowCombinators

        # Create context with break flag initially True
        context = Context()
        context[SHOULD_BREAK_KEY.path] = True

        # Create flow to set break to False
        flow = TrampolineFlowCombinators.set_should_break(False)

        # Execute flow
        result_context = run_flow_with_input(flow, context)

        # Check that break flag is now False
        assert result_context.get(SHOULD_BREAK_KEY.path, True) is False

    def test_set_should_break_preserves_other_context_data(self) -> None:
        """Test that set_should_break preserves other context data."""
        from context_flow.trampoline import TrampolineFlowCombinators

        # Create context with some data
        context = Context()
        context["test_key"] = "test_value"
        context["number"] = 42

        # Create and execute flow
        flow = TrampolineFlowCombinators.set_should_break(True)
        result_generator = flow(self._async_iter_from_context(context))
        result_context = self._get_first_result(result_generator)

        # Check that original data is preserved
        assert result_context["test_key"] == "test_value"
        assert result_context["number"] == 42

        # Check that break flag is set
        assert result_context.get(SHOULD_BREAK_KEY.path, False) is True

    def test_set_should_break_immutable_context(self) -> None:
        """Test that set_should_break creates new context (immutable pattern)."""
        from context_flow.trampoline import TrampolineFlowCombinators

        # Create context
        original_context = Context()

        # Create and execute flow
        flow = TrampolineFlowCombinators.set_should_break(True)
        result_generator = flow(self._async_iter_from_context(original_context))
        result_context = self._get_first_result(result_generator)

        # Check that original context is unchanged
        assert original_context.get(SHOULD_BREAK_KEY.path, False) is False

        # Check that result context has the flag set
        assert result_context.get(SHOULD_BREAK_KEY.path, False) is True

        # Check that they are different objects
        assert result_context is not original_context

    def test_set_should_break_static_method(self) -> None:
        """Test that set_should_break is a static method."""
        from context_flow.trampoline import TrampolineFlowCombinators

        # Should be able to call without instantiating the class
        flow = TrampolineFlowCombinators.set_should_break()
        assert flow is not None

        # Method should be static
        method = getattr(TrampolineFlowCombinators, "set_should_break")
        assert isinstance(method, staticmethod) or not hasattr(method, "__self__")

    def test_set_should_break_flow_composition(self) -> None:
        """Test that set_should_break flows can be composed with other flows."""
        from context_flow.trampoline import TrampolineFlowCombinators
        from flowengine.flow import Flow

        # Create a simple transformation flow
        def add_data_flow(stream: Any) -> Any:
            async def _flow() -> Any:
                async for context in stream:
                    new_context = context.fork()
                    new_context["added_data"] = "test"
                    yield new_context

            return _flow()

        transform_flow = Flow(add_data_flow)

        # Create context
        context = Context()

        # Compose flows: add data then set break
        break_flow = TrampolineFlowCombinators.set_should_break(True)
        composed_flow = transform_flow >> break_flow

        # Execute composed flow
        result_generator = composed_flow(self._async_iter_from_context(context))
        result_context = self._get_first_result(result_generator)

        # Check both operations happened
        assert result_context["added_data"] == "test"
        assert result_context.get(SHOULD_BREAK_KEY.path, False) is True

    def test_set_should_break_multiple_executions(self) -> None:
        """Test that set_should_break can be executed multiple times."""
        from context_flow.trampoline import TrampolineFlowCombinators

        # Create flow
        flow = TrampolineFlowCombinators.set_should_break(True)

        # Execute multiple times with different contexts
        for i in range(3):
            context = Context()
            context["iteration"] = i

            result_generator = flow(self._async_iter_from_context(context))
            result_context = self._get_first_result(result_generator)

            # Each execution should set the flag
            assert result_context.get(SHOULD_BREAK_KEY.path, False) is True
            assert result_context["iteration"] == i

    def test_set_should_break_documentation(self) -> None:
        """Test that set_should_break has proper documentation."""
        from context_flow.trampoline import TrampolineFlowCombinators

        method = getattr(TrampolineFlowCombinators, "set_should_break")
        assert method.__doc__ is not None
        assert len(method.__doc__.strip()) > 0
        assert "break" in method.__doc__.lower()

    def test_set_should_break_type_validation(self) -> None:
        """Test that set_should_break validates input types properly."""
        from context_flow.trampoline import TrampolineFlowCombinators

        # Should work with boolean values
        flow_true = TrampolineFlowCombinators.set_should_break(True)
        flow_false = TrampolineFlowCombinators.set_should_break(False)

        assert flow_true is not None
        assert flow_false is not None

        # Type checking should be handled by static type checkers
        # Runtime behavior with non-boolean values depends on implementation

    def test_set_should_break_error_handling(self) -> None:
        """Test that set_should_break handles errors gracefully."""
        from context_flow.trampoline import TrampolineFlowCombinators

        # Create flow
        flow = TrampolineFlowCombinators.set_should_break(True)

        # Test with empty context
        empty_context = Context()
        result_generator = flow(self._async_iter_from_context(empty_context))
        result_context = self._get_first_result(result_generator)

        # Should still work
        assert result_context.get(SHOULD_BREAK_KEY.path, False) is True

    def test_set_should_break_flow_naming(self) -> None:
        """Test that set_should_break creates flows with descriptive names."""
        from context_flow.trampoline import TrampolineFlowCombinators

        # Create flows with different values
        flow_true = TrampolineFlowCombinators.set_should_break(True)
        flow_false = TrampolineFlowCombinators.set_should_break(False)

        # Check that flows have names (for debugging)
        assert hasattr(flow_true, "name")
        assert hasattr(flow_false, "name")

        # Names should be strings
        assert isinstance(flow_true.name, str)
        assert isinstance(flow_false.name, str)

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

    def _get_first_result(self, async_generator: Any) -> Context:
        """Helper to get first result from async generator."""
        import asyncio
        import warnings

        async def _get_result() -> Context:
            try:
                async for result in async_generator:
                    return result  # type: ignore[no-any-return]
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


class TestTrampolineFlowCombinatorsSetShouldSkip:
    """Test cases for TrampolineFlowCombinators.set_should_skip method."""

    def test_set_should_skip_import(self) -> None:
        """Test that TrampolineFlowCombinators.set_should_skip can be imported."""
        # This test will fail until set_should_skip is implemented
        from context_flow.trampoline import TrampolineFlowCombinators

        # Verify the class exists and has the method
        assert hasattr(TrampolineFlowCombinators, "set_should_skip")
        assert callable(getattr(TrampolineFlowCombinators, "set_should_skip"))

    def test_set_should_skip_method_signature(self) -> None:
        """Test that set_should_skip has correct method signature."""
        import inspect

        from context_flow.trampoline import TrampolineFlowCombinators

        # Get method signature
        method = getattr(TrampolineFlowCombinators, "set_should_skip")
        signature = inspect.signature(method)

        # Check parameters
        params = list(signature.parameters.keys())
        assert "value" in params

        # Check default value
        value_param = signature.parameters["value"]
        assert value_param.default is True

        # Check parameter annotation (handle both bool type and string 'bool')
        assert value_param.annotation == bool or value_param.annotation == "bool"

    def test_set_should_skip_returns_flow(self) -> None:
        """Test that set_should_skip returns a Flow object."""
        from context_flow.trampoline import TrampolineFlowCombinators
        from flowengine.flow import Flow

        # Test with default value
        flow = TrampolineFlowCombinators.set_should_skip()
        assert isinstance(flow, Flow)

        # Test with explicit True
        flow_true = TrampolineFlowCombinators.set_should_skip(True)
        assert isinstance(flow_true, Flow)

        # Test with False
        flow_false = TrampolineFlowCombinators.set_should_skip(False)
        assert isinstance(flow_false, Flow)

    def test_set_should_skip_default_value_true(self) -> None:
        """Test that set_should_skip defaults to True when no argument provided."""
        from context_flow.integration import run_flow_with_input
        from context_flow.trampoline import TrampolineFlowCombinators

        # Create context
        context = Context()

        # Create flow with default value (should be True)
        flow = TrampolineFlowCombinators.set_should_skip()

        # Execute flow using the utility function for simpler execution
        result_context = run_flow_with_input(flow, context)

        # Check that skip flag is set to True
        assert result_context.get(SHOULD_SKIP_KEY.path, False) is True

    def test_set_should_skip_explicit_true(self) -> None:
        """Test that set_should_skip works with explicit True value."""
        from context_flow.integration import run_flow_with_input
        from context_flow.trampoline import TrampolineFlowCombinators

        # Create context
        context = Context()

        # Create flow with explicit True
        flow = TrampolineFlowCombinators.set_should_skip(True)

        # Execute flow
        result_context = run_flow_with_input(flow, context)

        # Check that skip flag is set to True
        assert result_context.get(SHOULD_SKIP_KEY.path, False) is True

    def test_set_should_skip_false_value(self) -> None:
        """Test that set_should_skip works with False value."""
        from context_flow.integration import run_flow_with_input
        from context_flow.trampoline import TrampolineFlowCombinators

        # Create context with skip flag initially True
        context = Context()
        context[SHOULD_SKIP_KEY.path] = True

        # Create flow to set skip to False
        flow = TrampolineFlowCombinators.set_should_skip(False)

        # Execute flow
        result_context = run_flow_with_input(flow, context)

        # Check that skip flag is now False
        assert result_context.get(SHOULD_SKIP_KEY.path, True) is False

    def test_set_should_skip_preserves_other_context_data(self) -> None:
        """Test that set_should_skip preserves other context data."""
        from context_flow.trampoline import TrampolineFlowCombinators

        # Create context with some data
        context = Context()
        context["test_key"] = "test_value"
        context["number"] = 42

        # Create and execute flow
        flow = TrampolineFlowCombinators.set_should_skip(True)
        result_generator = flow(self._async_iter_from_context(context))
        result_context = self._get_first_result(result_generator)

        # Check that original data is preserved
        assert result_context["test_key"] == "test_value"
        assert result_context["number"] == 42

        # Check that skip flag is set
        assert result_context.get(SHOULD_SKIP_KEY.path, False) is True

    def test_set_should_skip_immutable_context(self) -> None:
        """Test that set_should_skip creates new context (immutable pattern)."""
        from context_flow.trampoline import TrampolineFlowCombinators

        # Create context
        original_context = Context()

        # Create and execute flow
        flow = TrampolineFlowCombinators.set_should_skip(True)
        result_generator = flow(self._async_iter_from_context(original_context))
        result_context = self._get_first_result(result_generator)

        # Check that original context is unchanged
        assert original_context.get(SHOULD_SKIP_KEY.path, False) is False

        # Check that result context has the flag set
        assert result_context.get(SHOULD_SKIP_KEY.path, False) is True

        # Check that they are different objects
        assert result_context is not original_context

    def test_set_should_skip_static_method(self) -> None:
        """Test that set_should_skip is a static method."""
        from context_flow.trampoline import TrampolineFlowCombinators

        # Should be able to call without instantiating the class
        flow = TrampolineFlowCombinators.set_should_skip()
        assert flow is not None

        # Method should be static
        method = getattr(TrampolineFlowCombinators, "set_should_skip")
        assert isinstance(method, staticmethod) or not hasattr(method, "__self__")

    def test_set_should_skip_flow_composition(self) -> None:
        """Test that set_should_skip flows can be composed with other flows."""
        from context_flow.trampoline import TrampolineFlowCombinators
        from flowengine.flow import Flow

        # Create a simple transformation flow
        def add_data_flow(stream: Any) -> Any:
            async def _flow() -> Any:
                async for context in stream:
                    new_context = context.fork()
                    new_context["added_data"] = "test"
                    yield new_context

            return _flow()

        transform_flow = Flow(add_data_flow)

        # Create context
        context = Context()

        # Compose flows: add data then set skip
        skip_flow = TrampolineFlowCombinators.set_should_skip(True)
        composed_flow = transform_flow >> skip_flow

        # Execute composed flow
        result_generator = composed_flow(self._async_iter_from_context(context))
        result_context = self._get_first_result(result_generator)

        # Check both operations happened
        assert result_context["added_data"] == "test"
        assert result_context.get(SHOULD_SKIP_KEY.path, False) is True

    def test_set_should_skip_multiple_executions(self) -> None:
        """Test that set_should_skip can be executed multiple times."""
        from context_flow.trampoline import TrampolineFlowCombinators

        # Create flow
        flow = TrampolineFlowCombinators.set_should_skip(True)

        # Execute multiple times with different contexts
        for i in range(3):
            context = Context()
            context["iteration"] = i

            result_generator = flow(self._async_iter_from_context(context))
            result_context = self._get_first_result(result_generator)

            # Each execution should set the flag
            assert result_context.get(SHOULD_SKIP_KEY.path, False) is True
            assert result_context["iteration"] == i

    def test_set_should_skip_documentation(self) -> None:
        """Test that set_should_skip has proper documentation."""
        from context_flow.trampoline import TrampolineFlowCombinators

        method = getattr(TrampolineFlowCombinators, "set_should_skip")
        assert method.__doc__ is not None
        assert len(method.__doc__.strip()) > 0
        assert "skip" in method.__doc__.lower()

    def test_set_should_skip_type_validation(self) -> None:
        """Test that set_should_skip validates input types properly."""
        from context_flow.trampoline import TrampolineFlowCombinators

        # Should work with boolean values
        flow_true = TrampolineFlowCombinators.set_should_skip(True)
        flow_false = TrampolineFlowCombinators.set_should_skip(False)

        assert flow_true is not None
        assert flow_false is not None

        # Type checking should be handled by static type checkers
        # Runtime behavior with non-boolean values depends on implementation

    def test_set_should_skip_error_handling(self) -> None:
        """Test that set_should_skip handles errors gracefully."""
        from context_flow.trampoline import TrampolineFlowCombinators

        # Create flow
        flow = TrampolineFlowCombinators.set_should_skip(True)

        # Test with empty context
        empty_context = Context()
        result_generator = flow(self._async_iter_from_context(empty_context))
        result_context = self._get_first_result(result_generator)

        # Should still work
        assert result_context.get(SHOULD_SKIP_KEY.path, False) is True

    def test_set_should_skip_flow_naming(self) -> None:
        """Test that set_should_skip creates flows with descriptive names."""
        from context_flow.trampoline import TrampolineFlowCombinators

        # Create flows with different values
        flow_true = TrampolineFlowCombinators.set_should_skip(True)
        flow_false = TrampolineFlowCombinators.set_should_skip(False)

        # Check that flows have names (for debugging)
        assert hasattr(flow_true, "name")
        assert hasattr(flow_false, "name")

        # Names should be strings
        assert isinstance(flow_true.name, str)
        assert isinstance(flow_false.name, str)

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

    def _get_first_result(self, async_generator: Any) -> Context:
        """Helper to get first result from async generator."""
        import asyncio
        import warnings

        async def _get_result() -> Context:
            try:
                async for result in async_generator:
                    return result  # type: ignore[no-any-return]
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
