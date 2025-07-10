"""Tests for context_flow.trampoline TrampolineFlowCombinators.trampoline method."""

from typing import TYPE_CHECKING, Any

import pytest

from context.main import Context
from context_flow.trampoline import SHOULD_BREAK_KEY, SHOULD_EXIT_KEY

if TYPE_CHECKING:
    from flowengine.flow import Flow


class TestTrampolineFlowCombinatorsTrampoline:
    """Test cases for TrampolineFlowCombinators.trampoline method."""

    def test_trampoline_import(self) -> None:
        """Test that TrampolineFlowCombinators.trampoline can be imported."""
        from context_flow.trampoline import TrampolineFlowCombinators

        # Verify the class exists and has the method
        assert hasattr(TrampolineFlowCombinators, "trampoline")
        assert callable(getattr(TrampolineFlowCombinators, "trampoline"))

    def test_trampoline_method_signature(self) -> None:
        """Test that trampoline has correct method signature."""
        import inspect

        from context_flow.trampoline import TrampolineFlowCombinators

        # Get method signature
        method = getattr(TrampolineFlowCombinators, "trampoline")
        signature = inspect.signature(method)

        # Check parameters
        params = list(signature.parameters.values())
        assert len(params) == 1
        assert params[0].name == "flow"

    def test_trampoline_returns_flow(self) -> None:
        """Test that trampoline returns a Flow object."""
        from context_flow.trampoline import TrampolineFlowCombinators
        from flowengine.flow import Flow

        # Create a simple flow
        test_flow: "Flow[Context, Context]" = Flow.from_sync_fn(lambda ctx: ctx)

        # Test that it returns a Flow
        result = TrampolineFlowCombinators.trampoline(test_flow)
        assert isinstance(result, Flow)

    def test_trampoline_single_iteration_with_exit(self) -> None:
        """Test trampoline with flow that exits on first iteration."""
        from context_flow.integration import run_flow_with_input
        from context_flow.trampoline import TrampolineFlowCombinators
        from flowengine.flow import Flow

        # Create flow that sets exit immediately
        def exit_flow(ctx: Context) -> Context:
            result = ctx.fork()
            result["executed"] = True
            result[SHOULD_EXIT_KEY.path] = True
            return result

        flow = Flow.from_sync_fn(exit_flow)
        trampoline = TrampolineFlowCombinators.trampoline(flow)

        # Execute
        context = Context()
        result = run_flow_with_input(trampoline, context)

        assert result["executed"] is True
        assert result[SHOULD_EXIT_KEY.path] is True

    def test_trampoline_multiple_iterations(self) -> None:
        """Test trampoline that executes multiple iterations before exit."""
        from context_flow.integration import run_flow_with_input
        from context_flow.trampoline import TrampolineFlowCombinators
        from flowengine.flow import Flow

        # Create counting flow that exits at 5
        def counting_flow(ctx: Context) -> Context:
            result = ctx.fork()
            count = (ctx.get("count", 0) or 0) + 1
            result["count"] = count
            if count >= 5:
                result[SHOULD_EXIT_KEY.path] = True
            return result

        flow = Flow.from_sync_fn(counting_flow)
        trampoline = TrampolineFlowCombinators.trampoline(flow)

        # Execute
        context = Context()
        context["count"] = 0
        result = run_flow_with_input(trampoline, context)

        assert result["count"] == 5
        assert result[SHOULD_EXIT_KEY.path] is True

    def test_trampoline_break_signal_restart(self) -> None:
        """Test that trampoline restarts with original context on break signal."""
        from context_flow.integration import run_flow_with_input
        from context_flow.trampoline import TrampolineFlowCombinators
        from flowengine.flow import Flow

        # Track execution history
        execution_log: list[int] = []

        def break_and_count_flow(ctx: Context) -> Context:
            result = ctx.fork()
            count = (ctx.get("count", 0) or 0) + 1
            result["count"] = count
            execution_log.append(count)

            # Break on count 3 (first time only)
            if count == 3 and len(execution_log) <= 3:
                result[SHOULD_BREAK_KEY.path] = True
            # Exit on count 5
            elif count >= 5:
                result[SHOULD_EXIT_KEY.path] = True

            return result

        flow = Flow.from_sync_fn(break_and_count_flow)
        trampoline = TrampolineFlowCombinators.trampoline(flow)

        # Execute with initial count
        context = Context()
        context["count"] = 0
        result = run_flow_with_input(trampoline, context)

        # Should have: 1, 2, 3 (break), then restart: 1, 2, 3, 4, 5 (exit)
        assert execution_log == [1, 2, 3, 1, 2, 3, 4, 5]
        assert result["count"] == 5
        assert result[SHOULD_EXIT_KEY.path] is True

    def test_trampoline_preserves_context_data(self) -> None:
        """Test that trampoline preserves context data across iterations."""
        from context_flow.integration import run_flow_with_input
        from context_flow.trampoline import TrampolineFlowCombinators
        from flowengine.flow import Flow

        # Create flow that accumulates data
        def accumulator_flow(ctx: Context) -> Context:
            result = ctx.fork()

            # Increment counter
            counter = (ctx.get("counter", 0) or 0) + 1
            result["counter"] = counter

            # Accumulate values in list
            values = ctx.get("values", []) or []
            result["values"] = values + [counter]

            # Exit after 3 iterations
            if counter >= 3:
                result[SHOULD_EXIT_KEY.path] = True

            return result

        flow = Flow.from_sync_fn(accumulator_flow)
        trampoline = TrampolineFlowCombinators.trampoline(flow)

        # Execute with initial data
        context = Context()
        context["initial"] = "preserved"
        context["counter"] = 0
        context["values"] = []
        result = run_flow_with_input(trampoline, context)

        # Check all data is preserved and accumulated
        assert result["initial"] == "preserved"
        assert result["counter"] == 3
        assert result["values"] == [1, 2, 3]

    def test_trampoline_static_method(self) -> None:
        """Test that trampoline is a static method."""
        from context_flow.trampoline import TrampolineFlowCombinators

        # Method should be static
        method = getattr(TrampolineFlowCombinators, "trampoline")
        assert isinstance(method, staticmethod) or not hasattr(method, "__self__")

    def test_trampoline_flow_composition(self) -> None:
        """Test that trampoline can be composed with other flows."""
        from context_flow.trampoline import TrampolineFlowCombinators

        # Create flows using helper methods
        increment = self._create_increment_flow()
        prefix, suffix = self._create_prefix_suffix_flows()

        # Compose and execute
        trampoline = TrampolineFlowCombinators.trampoline(increment)
        composed = prefix >> trampoline >> suffix
        context = Context()
        result_generator = composed(self._async_iter_from_context(context))
        result = self._get_first_result(result_generator)

        # Verify results
        assert result["prefix"] == "start"
        assert result["count"] == 3
        assert result["suffix"] == "end"

    def test_trampoline_documentation(self) -> None:
        """Test that trampoline has proper documentation."""
        from context_flow.trampoline import TrampolineFlowCombinators

        method = getattr(TrampolineFlowCombinators, "trampoline")
        assert method.__doc__ is not None
        assert len(method.__doc__.strip()) > 0
        assert "trampoline" in method.__doc__.lower()
        assert "repeatedly" in method.__doc__.lower()

    def test_trampoline_flow_naming(self) -> None:
        """Test that trampoline creates flows with descriptive names."""
        from context_flow.trampoline import TrampolineFlowCombinators
        from flowengine.flow import Flow

        # Create test flow
        test_flow: "Flow[Context, Context]" = Flow.from_sync_fn(lambda ctx: ctx)
        trampoline = TrampolineFlowCombinators.trampoline(test_flow)

        # Check that flow has a name
        assert hasattr(trampoline, "name")
        assert isinstance(trampoline.name, str)
        assert "trampoline" in trampoline.name

    def test_trampoline_context_immutability(self) -> None:
        """Test that trampoline maintains context immutability."""
        from context_flow.integration import run_flow_with_input
        from context_flow.trampoline import TrampolineFlowCombinators
        from flowengine.flow import Flow

        # Create flow that modifies context
        def modifying_flow(ctx: Context) -> Context:
            result = ctx.fork()
            result["modified"] = True
            result[SHOULD_EXIT_KEY.path] = True
            return result

        flow = Flow.from_sync_fn(modifying_flow)
        trampoline = TrampolineFlowCombinators.trampoline(flow)

        # Execute with original context
        original_context = Context()
        original_context["original"] = "value"

        result = run_flow_with_input(trampoline, original_context)

        # Original context should be unchanged
        assert "modified" not in original_context
        assert original_context["original"] == "value"

        # Result should have modifications
        assert result["modified"] is True
        assert result["original"] == "value"

    def test_trampoline_state_machine_pattern(self) -> None:
        """Test trampoline implementing a simple state machine."""
        from context_flow.integration import run_flow_with_input
        from context_flow.trampoline import TrampolineFlowCombinators
        from flowengine.flow import Flow

        # Create state machine flow
        def state_machine_flow(ctx: Context) -> Context:
            result = ctx.fork()
            state = ctx.get("state", "start")

            # State transitions
            if state == "start":
                result["state"] = "processing"
                result["steps"] = ["start"]
            elif state == "processing":
                steps = ctx.get("steps", []) or []
                result["state"] = "finishing"
                result["steps"] = steps + ["processing"]
            elif state == "finishing":
                steps = ctx.get("steps", []) or []
                result["state"] = "done"
                result["steps"] = steps + ["finishing"]
                result[SHOULD_EXIT_KEY.path] = True

            return result

        flow = Flow.from_sync_fn(state_machine_flow)
        trampoline = TrampolineFlowCombinators.trampoline(flow)

        # Execute state machine
        context = Context()
        result = run_flow_with_input(trampoline, context)

        assert result["state"] == "done"
        assert result["steps"] == ["start", "processing", "finishing"]

    def test_trampoline_convergence_pattern(self) -> None:
        """Test trampoline for iterative convergence algorithm."""
        from context_flow.integration import run_flow_with_input
        from context_flow.trampoline import TrampolineFlowCombinators
        from flowengine.flow import Flow

        # Create flow that converges to a value
        def convergence_flow(ctx: Context) -> Context:
            result = ctx.fork()

            # Get current value and iteration count
            value = ctx.get("value", 100.0) or 100.0
            iterations = ctx.get("iterations", 0) or 0

            # Apply convergence step (divide by 2)
            new_value = value / 2.0
            result["value"] = new_value
            result["iterations"] = iterations + 1

            # Check convergence (value less than 1.0)
            if new_value < 1.0:
                result[SHOULD_EXIT_KEY.path] = True
                result["converged"] = True

            return result

        flow = Flow.from_sync_fn(convergence_flow)
        trampoline = TrampolineFlowCombinators.trampoline(flow)

        # Execute convergence
        context = Context()
        context["value"] = 100.0
        result = run_flow_with_input(trampoline, context)

        # Should converge in 7 iterations: 100 -> 50 -> 25 -> 12.5 -> 6.25 -> 3.125 -> 1.5625 -> 0.78125
        assert result["iterations"] == 7
        assert result["value"] < 1.0
        assert result["converged"] is True

    # Helper methods for flow creation
    def _create_increment_flow(self) -> "Flow[Context, Context]":
        """Create flow that increments count and exits at 3."""
        from flowengine.flow import Flow

        def increment_flow(ctx: Context) -> Context:
            result = ctx.fork()
            count = (ctx.get("count", 0) or 0) + 1
            result["count"] = count
            if count >= 3:
                result[SHOULD_EXIT_KEY.path] = True
            return result

        return Flow.from_sync_fn(increment_flow)

    def _create_prefix_suffix_flows(
        self,
    ) -> tuple["Flow[Context, Context]", "Flow[Context, Context]"]:
        """Create prefix and suffix flows for composition testing."""
        from flowengine.flow import Flow

        def prefix_flow(ctx: Context) -> Context:
            result = ctx.fork()
            result["prefix"] = "start"
            result["count"] = 0
            return result

        def suffix_flow(ctx: Context) -> Context:
            result = ctx.fork()
            result["suffix"] = "end"
            return result

        return Flow.from_sync_fn(prefix_flow), Flow.from_sync_fn(suffix_flow)

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
                    return result  # Return first result
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
