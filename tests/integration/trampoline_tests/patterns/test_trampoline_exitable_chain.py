"""Tests for context_flow.trampoline TrampolineFlowCombinators.exitable_chain method."""

from typing import TYPE_CHECKING, Any

import pytest

from context.main import Context
from context_flow.trampoline import SHOULD_BREAK_KEY, SHOULD_EXIT_KEY

if TYPE_CHECKING:
    from flow.flow import Flow


class TestTrampolineFlowCombinatorsExitableChain:
    """Test cases for TrampolineFlowCombinators.exitable_chain method."""

    def test_exitable_chain_import(self) -> None:
        """Test that TrampolineFlowCombinators.exitable_chain can be imported."""
        from context_flow.trampoline import TrampolineFlowCombinators

        # Verify the class exists and has the method
        assert hasattr(TrampolineFlowCombinators, "exitable_chain")
        assert callable(getattr(TrampolineFlowCombinators, "exitable_chain"))

    def test_exitable_chain_method_signature(self) -> None:
        """Test that exitable_chain has correct method signature."""
        import inspect

        from context_flow.trampoline import TrampolineFlowCombinators

        # Get method signature
        method = getattr(TrampolineFlowCombinators, "exitable_chain")
        signature = inspect.signature(method)

        # Check that it accepts variable arguments
        params = list(signature.parameters.values())
        assert len(params) == 1
        assert params[0].kind == inspect.Parameter.VAR_POSITIONAL

    def test_exitable_chain_returns_flow(self) -> None:
        """Test that exitable_chain returns a Flow object."""
        from context_flow.trampoline import TrampolineFlowCombinators
        from flow.flow import Flow

        # Test that it returns a Flow
        flow = TrampolineFlowCombinators.exitable_chain()
        assert isinstance(flow, Flow)

    def test_exitable_chain_empty_flows(self) -> None:
        """Test that exitable_chain with no flows returns identity."""
        from context_flow.integration import run_flow_with_input
        from context_flow.trampoline import TrampolineFlowCombinators

        # Create empty chain
        chain = TrampolineFlowCombinators.exitable_chain()

        # Create context
        context = Context()
        context["test"] = "value"

        # Execute chain - should return unchanged context
        result = run_flow_with_input(chain, context)
        assert result["test"] == "value"

    def test_exitable_chain_single_flow(self) -> None:
        """Test that exitable_chain with single flow executes correctly."""
        from context_flow.integration import run_flow_with_input
        from context_flow.trampoline import TrampolineFlowCombinators
        from flow.flow import Flow

        # Create single flow that modifies context
        def flow1_fn(ctx: Context) -> Context:
            result = ctx.fork()
            result["step"] = 1
            return result

        flow1 = Flow.from_sync_fn(flow1_fn)

        # Create chain
        chain = TrampolineFlowCombinators.exitable_chain(flow1)

        # Execute chain
        context = Context()
        result = run_flow_with_input(chain, context)
        assert result["step"] == 1

    def test_exitable_chain_multiple_flows_sequential(self) -> None:
        """Test that exitable_chain executes flows sequentially."""
        from context_flow.integration import run_flow_with_input
        from context_flow.trampoline import TrampolineFlowCombinators
        from flow.flow import Flow

        # Create flows that modify context sequentially
        def flow1_fn(ctx: Context) -> Context:
            result = ctx.fork()
            result["step"] = 1
            return result

        def flow2_fn(ctx: Context) -> Context:
            result = ctx.fork()
            result["step"] = ctx["step"] + 1
            return result

        def flow3_fn(ctx: Context) -> Context:
            result = ctx.fork()
            result["step"] = ctx["step"] + 1
            return result

        flow1 = Flow.from_sync_fn(flow1_fn)
        flow2 = Flow.from_sync_fn(flow2_fn)
        flow3 = Flow.from_sync_fn(flow3_fn)

        # Create chain
        chain = TrampolineFlowCombinators.exitable_chain(flow1, flow2, flow3)

        # Execute chain
        context = Context()
        result = run_flow_with_input(chain, context)
        assert result["step"] == 3

    def test_exitable_chain_exit_signal_early_termination(self) -> None:
        """Test that exitable_chain exits early when exit signal is set."""
        from context_flow.integration import run_flow_with_input
        from context_flow.trampoline import TrampolineFlowCombinators
        from flow.flow import Flow

        # Create flows where second flow sets exit signal
        def flow1_fn(ctx: Context) -> Context:
            result = ctx.fork()
            result["step"] = 1
            return result

        def flow2_fn(ctx: Context) -> Context:
            result = ctx.fork()
            result["step"] = 2
            result[SHOULD_EXIT_KEY.path] = True
            return result

        def flow3_fn(ctx: Context) -> Context:
            result = ctx.fork()
            result["step"] = 3
            return result

        flow1 = Flow.from_sync_fn(flow1_fn)
        flow2 = Flow.from_sync_fn(flow2_fn)
        flow3 = Flow.from_sync_fn(flow3_fn)  # Should not execute

        # Create chain
        chain = TrampolineFlowCombinators.exitable_chain(flow1, flow2, flow3)

        # Execute chain
        context = Context()
        result = run_flow_with_input(chain, context)
        assert result["step"] == 2  # flow3 should not have executed
        assert result[SHOULD_EXIT_KEY.path] is True

    def test_exitable_chain_break_signal_restart(self) -> None:
        """Test that exitable_chain restarts when break signal is set."""
        from context_flow.integration import run_flow_with_input
        from context_flow.trampoline import TrampolineFlowCombinators

        # Create counting flows and execute
        flow1, flow2, execution_count = self._create_counting_flows()
        chain = TrampolineFlowCombinators.exitable_chain(flow1, flow2)
        context = Context()
        result = run_flow_with_input(chain, context)

        # Verify restart behavior
        assert execution_count["flow1"] == 2
        assert execution_count["flow2"] == 2
        assert result["step"] == 2
        assert result.get(SHOULD_BREAK_KEY.path, False) is False

    def test_exitable_chain_preserves_context_data(self) -> None:
        """Test that exitable_chain preserves context data across flows."""
        from context_flow.integration import run_flow_with_input
        from context_flow.trampoline import TrampolineFlowCombinators

        # Create flows using helper method
        flow1, flow2, flow3 = self._create_data_flows()

        # Create chain and execute
        chain = TrampolineFlowCombinators.exitable_chain(flow1, flow2, flow3)
        context = Context()
        context["initial"] = "preserved"
        result = run_flow_with_input(chain, context)

        # Verify all data is preserved
        assert result["initial"] == "preserved"
        assert result["data1"] == "value1"
        assert result["data2"] == "value2"
        assert result["data3"] == "value3"

    def test_exitable_chain_static_method(self) -> None:
        """Test that exitable_chain is a static method."""
        from context_flow.trampoline import TrampolineFlowCombinators

        # Should be able to call without instantiating the class
        chain = TrampolineFlowCombinators.exitable_chain()
        assert chain is not None

        # Method should be static
        method = getattr(TrampolineFlowCombinators, "exitable_chain")
        assert isinstance(method, staticmethod) or not hasattr(method, "__self__")

    def test_exitable_chain_flow_composition(self) -> None:
        """Test that exitable_chain can be composed with other flows."""
        from context_flow.trampoline import TrampolineFlowCombinators

        # Create flows using helper methods
        flow1, flow2 = self._create_step_flows()
        prefix_flow, suffix_flow = self._create_composition_flows()

        # Create chain and compose
        chain = TrampolineFlowCombinators.exitable_chain(flow1, flow2)
        composed = prefix_flow >> chain >> suffix_flow

        # Execute and verify
        context = Context()
        result_generator = composed(self._async_iter_from_context(context))
        result = self._get_first_result(result_generator)

        assert result["prefix"] == "start"
        assert result["step"] == 2
        assert result["suffix"] == "end"

    def test_exitable_chain_documentation(self) -> None:
        """Test that exitable_chain has proper documentation."""
        from context_flow.trampoline import TrampolineFlowCombinators

        method = getattr(TrampolineFlowCombinators, "exitable_chain")
        assert method.__doc__ is not None
        assert len(method.__doc__.strip()) > 0
        assert "chain" in method.__doc__.lower()
        assert "exit" in method.__doc__.lower()

    def test_exitable_chain_flow_naming(self) -> None:
        """Test that exitable_chain creates flows with descriptive names."""
        from context_flow.trampoline import TrampolineFlowCombinators

        # Create chain
        chain = TrampolineFlowCombinators.exitable_chain()

        # Check that flow has a name (for debugging)
        assert hasattr(chain, "name")
        assert isinstance(chain.name, str)
        assert len(chain.name) > 0

    def test_exitable_chain_context_immutability(self) -> None:
        """Test that exitable_chain maintains context immutability."""
        from context_flow.integration import run_flow_with_input
        from context_flow.trampoline import TrampolineFlowCombinators
        from flow.flow import Flow

        # Create flow that modifies context
        def flow1_fn(ctx: Context) -> Context:
            result = ctx.fork()
            result["modified"] = True
            return result

        flow1 = Flow.from_sync_fn(flow1_fn)

        # Create chain
        chain = TrampolineFlowCombinators.exitable_chain(flow1)

        # Execute with original context
        original_context = Context()
        original_context["original"] = "value"

        result = run_flow_with_input(chain, original_context)

        # Original context should be unchanged
        assert "modified" not in original_context
        assert original_context["original"] == "value"

        # Result should have modifications
        assert result["modified"] is True
        assert result["original"] == "value"

    def test_exitable_chain_multiple_breaks_and_restart(self) -> None:
        """Test complex scenario with multiple breaks and restarts."""
        from context_flow.integration import run_flow_with_input
        from context_flow.trampoline import TrampolineFlowCombinators

        # Create execution tracking and flows
        execution_log: list[str] = []
        flow1 = self._create_logging_flow("step1", execution_log)
        flow2 = self._create_logging_flow("step2", execution_log, break_on_count=1)
        flow3 = self._create_logging_flow("step3", execution_log)

        # Execute chain
        chain = TrampolineFlowCombinators.exitable_chain(flow1, flow2, flow3)
        context = Context()
        result = run_flow_with_input(chain, context)

        # Verify execution pattern and results
        expected_log = ["step1", "step2", "step1", "step2", "step3"]
        assert execution_log == expected_log
        assert result["executed_step1"] == 2
        assert result["executed_step2"] == 2
        assert result["executed_step3"] == 1

    # Helper methods for flow creation
    def _create_step_flows(
        self,
    ) -> tuple["Flow[Context, Context]", "Flow[Context, Context]"]:
        """Create simple step flows for testing."""
        from flow.flow import Flow

        def flow1_fn(ctx: Context) -> Context:
            result = ctx.fork()
            result["step"] = 1
            return result

        def flow2_fn(ctx: Context) -> Context:
            result = ctx.fork()
            result["step"] = 2
            return result

        return Flow.from_sync_fn(flow1_fn), Flow.from_sync_fn(flow2_fn)

    def _create_composition_flows(
        self,
    ) -> tuple["Flow[Context, Context]", "Flow[Context, Context]"]:
        """Create prefix and suffix flows for composition testing."""
        from flow.flow import Flow

        def prefix_fn(ctx: Context) -> Context:
            result = ctx.fork()
            result["prefix"] = "start"
            return result

        def suffix_fn(ctx: Context) -> Context:
            result = ctx.fork()
            result["suffix"] = "end"
            return result

        return Flow.from_sync_fn(prefix_fn), Flow.from_sync_fn(suffix_fn)

    def _create_data_flows(
        self,
    ) -> tuple[
        "Flow[Context, Context]", "Flow[Context, Context]", "Flow[Context, Context]"
    ]:
        """Create flows that add data to context."""
        from flow.flow import Flow

        def flow1_fn(ctx: Context) -> Context:
            result = ctx.fork()
            result["data1"] = "value1"
            return result

        def flow2_fn(ctx: Context) -> Context:
            result = ctx.fork()
            result["data2"] = "value2"
            return result

        def flow3_fn(ctx: Context) -> Context:
            result = ctx.fork()
            result["data3"] = "value3"
            return result

        return (
            Flow.from_sync_fn(flow1_fn),
            Flow.from_sync_fn(flow2_fn),
            Flow.from_sync_fn(flow3_fn),
        )

    def _create_logging_flow(
        self, step_name: str, execution_log: list[str], break_on_count: int = 0
    ) -> "Flow[Context, Context]":
        """Create a logging flow that tracks execution and optionally breaks."""
        from flow.flow import Flow

        def flow_fn(ctx: Context) -> Context:
            count = len([x for x in execution_log if x == step_name])
            execution_log.append(step_name)

            result_ctx = ctx.fork()
            result_ctx[f"executed_{step_name}"] = count + 1

            # Set break signal on specific execution count
            if break_on_count > 0 and count + 1 == break_on_count:
                result_ctx[SHOULD_BREAK_KEY.path] = True

            return result_ctx

        return Flow.from_sync_fn(flow_fn)

    def _create_counting_flows(
        self,
    ) -> tuple["Flow[Context, Context]", "Flow[Context, Context]", dict[str, int]]:
        """Create flows that count executions and break on first flow2 execution."""
        from flow.flow import Flow

        execution_count = {"flow1": 0, "flow2": 0}

        def flow1_fn(ctx: Context) -> Context:
            execution_count["flow1"] += 1
            result = ctx.fork()
            result["step"] = 1
            return result

        def flow2_fn(ctx: Context) -> Context:
            execution_count["flow2"] += 1
            result = ctx.fork()
            result["step"] = 2
            if execution_count["flow2"] == 1:
                result[SHOULD_BREAK_KEY.path] = True
            return result

        return Flow.from_sync_fn(flow1_fn), Flow.from_sync_fn(flow2_fn), execution_count

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
