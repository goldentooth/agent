"""Tests for context_flow.trampoline TrampolineFlowCombinators.trampoline_chain method."""

from typing import TYPE_CHECKING, Any

import pytest

from context.main import Context
from context_flow.trampoline import SHOULD_BREAK_KEY, SHOULD_EXIT_KEY

if TYPE_CHECKING:
    from flow.flow import Flow


class TestTrampolineFlowCombinatorsTramplineChain:
    """Test cases for TrampolineFlowCombinators.trampoline_chain method."""

    def test_trampoline_chain_import(self) -> None:
        """Test that TrampolineFlowCombinators.trampoline_chain can be imported."""
        from context_flow.trampoline import TrampolineFlowCombinators

        # Verify the class exists and has the method
        assert hasattr(TrampolineFlowCombinators, "trampoline_chain")
        assert callable(getattr(TrampolineFlowCombinators, "trampoline_chain"))

    def test_trampoline_chain_method_signature(self) -> None:
        """Test that trampoline_chain has correct method signature."""
        import inspect

        from context_flow.trampoline import TrampolineFlowCombinators

        # Get method signature
        method = getattr(TrampolineFlowCombinators, "trampoline_chain")
        signature = inspect.signature(method)

        # Check that it accepts variable arguments
        params = list(signature.parameters.values())
        assert len(params) == 1
        assert params[0].kind == inspect.Parameter.VAR_POSITIONAL

    def test_trampoline_chain_returns_flow(self) -> None:
        """Test that trampoline_chain returns a Flow object."""
        from context_flow.trampoline import TrampolineFlowCombinators
        from flow.flow import Flow

        # Create test flows
        flow1: "Flow[Context, Context]" = Flow.from_sync_fn(lambda ctx: ctx)
        flow2: "Flow[Context, Context]" = Flow.from_sync_fn(lambda ctx: ctx)

        # Test that it returns a Flow
        result = TrampolineFlowCombinators.trampoline_chain(flow1, flow2)
        assert isinstance(result, Flow)

    def test_trampoline_chain_empty_flows(self) -> None:
        """Test that trampoline_chain with no flows returns identity."""
        from context_flow.integration import run_flow_with_input
        from context_flow.trampoline import TrampolineFlowCombinators

        # Create empty chain
        chain = TrampolineFlowCombinators.trampoline_chain()

        # Create context
        context = Context()
        context["test"] = "value"

        # Execute chain - should return unchanged context
        result = run_flow_with_input(chain, context)
        assert result["test"] == "value"

    def test_trampoline_chain_single_flow_cycle(self) -> None:
        """Test trampoline_chain with single flow that cycles until exit."""
        from context_flow.integration import run_flow_with_input
        from context_flow.trampoline import TrampolineFlowCombinators
        from flow.flow import Flow

        # Create flow that increments counter and exits at 5
        def counting_flow(ctx: Context) -> Context:
            result = ctx.fork()
            count = (ctx.get("count", 0) or 0) + 1
            result["count"] = count
            if count >= 5:
                result[SHOULD_EXIT_KEY.path] = True
            return result

        flow = Flow.from_sync_fn(counting_flow)
        chain = TrampolineFlowCombinators.trampoline_chain(flow)

        # Execute
        context = Context()
        context["count"] = 0
        result = run_flow_with_input(chain, context)

        assert result["count"] == 5
        assert result[SHOULD_EXIT_KEY.path] is True

    def test_trampoline_chain_multiple_flows_cycle(self) -> None:
        """Test trampoline_chain cycling through multiple flows."""
        from context_flow.integration import run_flow_with_input
        from context_flow.trampoline import TrampolineFlowCombinators

        # Create flows using helper method
        execution_log: list[str] = []
        flow1, flow2, flow3 = self._create_abc_flows(execution_log)
        chain = TrampolineFlowCombinators.trampoline_chain(flow1, flow2, flow3)

        # Execute
        context = Context()
        result = run_flow_with_input(chain, context)

        # Should execute: A → B → C → A → B → C (2 complete cycles)
        assert execution_log == ["A", "B", "C", "A", "B", "C"]
        assert result["step"] == "C"  # Last executed flow

    def test_trampoline_chain_break_signal_restart(self) -> None:
        """Test that trampoline_chain restarts cycle on break signal."""
        from context_flow.integration import run_flow_with_input
        from context_flow.trampoline import TrampolineFlowCombinators

        # Create flows using helper method
        execution_log: list[str] = []
        flow1, flow2, flow3 = self._create_break_restart_flows(execution_log)
        chain = TrampolineFlowCombinators.trampoline_chain(flow1, flow2, flow3)

        # Execute
        context = Context()
        result = run_flow_with_input(chain, context)

        # Should execute: A → B → C → A → B (break) → A → B → C
        # Total: A(3), B(3), C(2) due to break restarting at A
        assert execution_log == ["A", "B", "C", "A", "B", "A", "B", "C"]
        assert result["last_flow"] == "C"

    def test_trampoline_chain_preserves_context_data(self) -> None:
        """Test that trampoline_chain preserves and accumulates context data."""
        from context_flow.integration import run_flow_with_input
        from context_flow.trampoline import TrampolineFlowCombinators

        # Create flows using helper method
        flow1, flow2, flow3 = self._create_stage_flows()
        chain = TrampolineFlowCombinators.trampoline_chain(flow1, flow2, flow3)

        # Execute with initial data
        context = Context()
        context["initial"] = "preserved"
        context["processed"] = []
        result = run_flow_with_input(chain, context)

        # Check data preservation and accumulation
        assert result["initial"] == "preserved"
        assert result["current_stage"] == 3
        assert result["processed"] == [
            "stage1",
            "stage2",
            "stage3",
            "stage1",
            "stage2",
            "stage3",
        ]

    def test_trampoline_chain_static_method(self) -> None:
        """Test that trampoline_chain is a static method."""
        from context_flow.trampoline import TrampolineFlowCombinators

        # Method should be static
        method = getattr(TrampolineFlowCombinators, "trampoline_chain")
        assert isinstance(method, staticmethod) or not hasattr(method, "__self__")

    def test_trampoline_chain_flow_composition(self) -> None:
        """Test that trampoline_chain can be composed with other flows."""
        from context_flow.trampoline import TrampolineFlowCombinators

        # Create flows using helper methods
        cycle_flows = self._create_cycle_flows()
        prefix, suffix = self._create_setup_cleanup_flows()

        # Compose flows
        chain = TrampolineFlowCombinators.trampoline_chain(*cycle_flows)
        composed = prefix >> chain >> suffix

        # Execute
        context = Context()
        result_generator = composed(self._async_iter_from_context(context))
        result = self._get_first_result(result_generator)

        assert result["setup"] == "completed"
        assert result["cycles"] == 2
        assert result["cleanup"] == "completed"

    def test_trampoline_chain_documentation(self) -> None:
        """Test that trampoline_chain has proper documentation."""
        from context_flow.trampoline import TrampolineFlowCombinators

        method = getattr(TrampolineFlowCombinators, "trampoline_chain")
        assert method.__doc__ is not None
        assert len(method.__doc__.strip()) > 0
        assert "trampoline_chain" in method.__doc__.lower()
        assert "cycle" in method.__doc__.lower()

    def test_trampoline_chain_flow_naming(self) -> None:
        """Test that trampoline_chain creates flows with descriptive names."""
        from context_flow.trampoline import TrampolineFlowCombinators
        from flow.flow import Flow

        # Create test flows
        flow1: "Flow[Context, Context]" = Flow.from_sync_fn(lambda ctx: ctx)
        flow2: "Flow[Context, Context]" = Flow.from_sync_fn(lambda ctx: ctx)
        chain = TrampolineFlowCombinators.trampoline_chain(flow1, flow2)

        # Check that flow has a name
        assert hasattr(chain, "name")
        assert isinstance(chain.name, str)
        assert "trampoline_chain" in chain.name

    def test_trampoline_chain_context_immutability(self) -> None:
        """Test that trampoline_chain maintains context immutability."""
        from context_flow.integration import run_flow_with_input
        from context_flow.trampoline import TrampolineFlowCombinators
        from flow.flow import Flow

        def modifying_flow(ctx: Context) -> Context:
            result = ctx.fork()
            result["modified"] = True
            result[SHOULD_EXIT_KEY.path] = True
            return result

        flow = Flow.from_sync_fn(modifying_flow)
        chain = TrampolineFlowCombinators.trampoline_chain(flow)

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

    def test_trampoline_chain_state_machine_pattern(self) -> None:
        """Test trampoline_chain implementing a multi-state machine."""
        from context_flow.integration import run_flow_with_input
        from context_flow.trampoline import TrampolineFlowCombinators
        from flow.flow import Flow

        def state_init(ctx: Context) -> Context:
            result = ctx.fork()
            result["state"] = "initialized"
            result["transitions"] = (ctx.get("transitions", []) or []) + ["init"]
            return result

        def state_process(ctx: Context) -> Context:
            result = ctx.fork()
            result["state"] = "processed"
            transitions = ctx.get("transitions", []) or []
            result["transitions"] = transitions + ["process"]
            return result

        def state_validate(ctx: Context) -> Context:
            result = ctx.fork()
            result["state"] = "validated"
            transitions = ctx.get("transitions", []) or []
            result["transitions"] = transitions + ["validate"]
            # Exit after 2 complete state cycles
            if len(transitions) >= 5:  # Will be 6 after this transition
                result[SHOULD_EXIT_KEY.path] = True
            return result

        flow1 = Flow.from_sync_fn(state_init)
        flow2 = Flow.from_sync_fn(state_process)
        flow3 = Flow.from_sync_fn(state_validate)

        chain = TrampolineFlowCombinators.trampoline_chain(flow1, flow2, flow3)

        # Execute state machine
        context = Context()
        result = run_flow_with_input(chain, context)

        assert result["state"] == "validated"
        assert result["transitions"] == [
            "init",
            "process",
            "validate",
            "init",
            "process",
            "validate",
        ]

    def test_trampoline_chain_optimization_pattern(self) -> None:
        """Test trampoline_chain for multi-phase optimization algorithm."""
        from context_flow.integration import run_flow_with_input
        from context_flow.trampoline import TrampolineFlowCombinators

        # Create optimization flows using helper method
        flow1, flow2, flow3 = self._create_optimization_flows()
        chain = TrampolineFlowCombinators.trampoline_chain(flow1, flow2, flow3)

        # Execute optimization
        context = Context()
        context["value"] = 100.0
        result = run_flow_with_input(chain, context)

        # Should converge after several cycles
        assert result["value"] < 20.0
        assert result["last_phase"] == "refine"
        assert result[SHOULD_EXIT_KEY.path] is True

    # Helper methods for flow creation
    def _create_cycle_flows(self) -> list["Flow[Context, Context]"]:
        """Create flows that cycle and exit after 2 cycles."""
        from flow.flow import Flow

        def flow_1(ctx: Context) -> Context:
            result = ctx.fork()
            cycles = (ctx.get("cycles", 0) or 0) + 1
            result["cycles"] = cycles
            result["current"] = 1
            return result

        def flow_2(ctx: Context) -> Context:
            result = ctx.fork()
            result["current"] = 2
            cycles = ctx.get("cycles", 0) or 0
            if cycles >= 2:
                result[SHOULD_EXIT_KEY.path] = True
            return result

        return [Flow.from_sync_fn(flow_1), Flow.from_sync_fn(flow_2)]

    def _create_setup_cleanup_flows(
        self,
    ) -> tuple["Flow[Context, Context]", "Flow[Context, Context]"]:
        """Create setup and cleanup flows for composition testing."""
        from flow.flow import Flow

        def setup_flow(ctx: Context) -> Context:
            result = ctx.fork()
            result["setup"] = "completed"
            result["cycles"] = 0
            return result

        def cleanup_flow(ctx: Context) -> Context:
            result = ctx.fork()
            result["cleanup"] = "completed"
            return result

        return Flow.from_sync_fn(setup_flow), Flow.from_sync_fn(cleanup_flow)

    def _create_stage_flows(
        self,
    ) -> tuple[
        "Flow[Context, Context]", "Flow[Context, Context]", "Flow[Context, Context]"
    ]:
        """Create stage flows for data preservation testing."""
        from flow.flow import Flow

        def stage_1(ctx: Context) -> Context:
            result = ctx.fork()
            processed = ctx.get("processed", []) or []
            result["processed"] = processed + ["stage1"]
            result["current_stage"] = 1
            return result

        def stage_2(ctx: Context) -> Context:
            result = ctx.fork()
            processed = ctx.get("processed", []) or []
            result["processed"] = processed + ["stage2"]
            result["current_stage"] = 2
            return result

        def stage_3(ctx: Context) -> Context:
            result = ctx.fork()
            processed = ctx.get("processed", []) or []
            result["processed"] = processed + ["stage3"]
            result["current_stage"] = 3
            # Exit after 2 complete cycles
            if len(processed) >= 5:  # Will be 6 after this addition
                result[SHOULD_EXIT_KEY.path] = True
            return result

        return (
            Flow.from_sync_fn(stage_1),
            Flow.from_sync_fn(stage_2),
            Flow.from_sync_fn(stage_3),
        )

    def _create_optimization_flows(
        self,
    ) -> tuple[
        "Flow[Context, Context]", "Flow[Context, Context]", "Flow[Context, Context]"
    ]:
        """Create optimization flows for algorithm testing."""
        from flow.flow import Flow

        def analyze_phase(ctx: Context) -> Context:
            result = ctx.fork()
            value = ctx.get("value", 100.0) or 100.0
            # Analysis reduces value by 10%
            result["value"] = value * 0.9
            result["last_phase"] = "analyze"
            return result

        def optimize_phase(ctx: Context) -> Context:
            result = ctx.fork()
            value = ctx.get("value", 100.0) or 100.0
            # Optimization reduces value by 15%
            result["value"] = value * 0.85
            result["last_phase"] = "optimize"
            return result

        def refine_phase(ctx: Context) -> Context:
            result = ctx.fork()
            value = ctx.get("value", 100.0) or 100.0
            # Refinement reduces value by 5%
            result["value"] = value * 0.95
            result["last_phase"] = "refine"
            # Exit when value converges below threshold
            if value < 20.0:
                result[SHOULD_EXIT_KEY.path] = True
            return result

        return (
            Flow.from_sync_fn(analyze_phase),
            Flow.from_sync_fn(optimize_phase),
            Flow.from_sync_fn(refine_phase),
        )

    def _create_abc_flows(
        self, execution_log: list[str]
    ) -> tuple[
        "Flow[Context, Context]", "Flow[Context, Context]", "Flow[Context, Context]"
    ]:
        """Create ABC flows that log execution and exit after 6 executions."""
        from flow.flow import Flow

        def flow_a(ctx: Context) -> Context:
            execution_log.append("A")
            result = ctx.fork()
            result["step"] = "A"
            return result

        def flow_b(ctx: Context) -> Context:
            execution_log.append("B")
            result = ctx.fork()
            result["step"] = "B"
            return result

        def flow_c(ctx: Context) -> Context:
            execution_log.append("C")
            result = ctx.fork()
            result["step"] = "C"
            # Exit after 2 complete cycles (6 total executions)
            if len(execution_log) >= 6:
                result[SHOULD_EXIT_KEY.path] = True
            return result

        return (
            Flow.from_sync_fn(flow_a),
            Flow.from_sync_fn(flow_b),
            Flow.from_sync_fn(flow_c),
        )

    def _create_break_restart_flows(
        self, execution_log: list[str]
    ) -> tuple[
        "Flow[Context, Context]", "Flow[Context, Context]", "Flow[Context, Context]"
    ]:
        """Create flows that test break/restart behavior."""
        from flow.flow import Flow

        def flow_a(ctx: Context) -> Context:
            execution_log.append("A")
            result = ctx.fork()
            result["last_flow"] = "A"
            return result

        def flow_b(ctx: Context) -> Context:
            execution_log.append("B")
            result = ctx.fork()
            result["last_flow"] = "B"
            # Break on second execution of B to restart cycle
            if execution_log.count("B") == 2:
                result[SHOULD_BREAK_KEY.path] = True
            return result

        def flow_c(ctx: Context) -> Context:
            execution_log.append("C")
            result = ctx.fork()
            result["last_flow"] = "C"
            # Exit after sufficient iterations
            if len(execution_log) >= 7:
                result[SHOULD_EXIT_KEY.path] = True
            return result

        return (
            Flow.from_sync_fn(flow_a),
            Flow.from_sync_fn(flow_b),
            Flow.from_sync_fn(flow_c),
        )

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
