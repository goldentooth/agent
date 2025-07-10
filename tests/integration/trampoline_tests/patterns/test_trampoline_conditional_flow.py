"""Tests for context_flow.trampoline TrampolineFlowCombinators.conditional_flow method."""

from typing import TYPE_CHECKING, Any, Callable

import pytest

from context.main import Context

if TYPE_CHECKING:
    from flowengine.flow import Flow


class TestTrampolineFlowCombinatorsConditionalFlow:
    """Test cases for TrampolineFlowCombinators.conditional_flow method."""

    def test_conditional_flow_import(self) -> None:
        """Test that TrampolineFlowCombinators.conditional_flow can be imported."""
        from context_flow.trampoline import TrampolineFlowCombinators

        # Verify the class exists and has the method
        assert hasattr(TrampolineFlowCombinators, "conditional_flow")
        assert callable(getattr(TrampolineFlowCombinators, "conditional_flow"))

    def test_conditional_flow_method_signature(self) -> None:
        """Test that conditional_flow has correct method signature."""
        import inspect

        from context_flow.trampoline import TrampolineFlowCombinators

        # Get method signature
        method = getattr(TrampolineFlowCombinators, "conditional_flow")
        signature = inspect.signature(method)

        # Check parameters
        params = list(signature.parameters.keys())
        assert "predicate" in params
        assert "then_flow" in params
        assert "else_flow" in params

    def test_conditional_flow_returns_flow(self) -> None:
        """Test that conditional_flow returns a Flow object."""
        from context_flow.trampoline import TrampolineFlowCombinators
        from flowengine.flow import Flow

        # Create test flows
        then_flow: "Flow[Context, Context]" = Flow.from_sync_fn(lambda ctx: ctx)
        predicate = lambda ctx: True

        # Test that it returns a Flow
        result = TrampolineFlowCombinators.conditional_flow(predicate, then_flow)
        assert isinstance(result, Flow)

    def test_conditional_flow_predicate_true_executes_then_flow(self) -> None:
        """Test that conditional_flow executes then_flow when predicate is True."""
        from context_flow.integration import run_flow_with_input
        from context_flow.trampoline import TrampolineFlowCombinators
        from flowengine.flow import Flow

        # Create predicate that always returns True
        def always_true(ctx: Context) -> bool:
            return True

        # Create then_flow that adds a marker
        def then_fn(ctx: Context) -> Context:
            result = ctx.fork()
            result["then_executed"] = True
            return result

        then_flow = Flow.from_sync_fn(then_fn)

        # Create conditional flow
        conditional = TrampolineFlowCombinators.conditional_flow(always_true, then_flow)

        # Execute
        context = Context()
        result = run_flow_with_input(conditional, context)

        assert result["then_executed"] is True

    def test_conditional_flow_predicate_false_executes_else_flow(self) -> None:
        """Test that conditional_flow executes else_flow when predicate is False."""
        from context_flow.integration import run_flow_with_input
        from context_flow.trampoline import TrampolineFlowCombinators
        from flowengine.flow import Flow

        # Create predicate that always returns False
        def always_false(ctx: Context) -> bool:
            return False

        # Create flows
        def then_fn(ctx: Context) -> Context:
            result = ctx.fork()
            result["then_executed"] = True
            return result

        def else_fn(ctx: Context) -> Context:
            result = ctx.fork()
            result["else_executed"] = True
            return result

        then_flow = Flow.from_sync_fn(then_fn)
        else_flow = Flow.from_sync_fn(else_fn)

        # Create conditional flow
        conditional = TrampolineFlowCombinators.conditional_flow(
            always_false, then_flow, else_flow
        )

        # Execute
        context = Context()
        result = run_flow_with_input(conditional, context)

        assert "then_executed" not in result
        assert result["else_executed"] is True

    def test_conditional_flow_predicate_false_no_else_flow_passthrough(self) -> None:
        """Test that conditional_flow passes through context when predicate is False and no else_flow."""
        from context_flow.integration import run_flow_with_input
        from context_flow.trampoline import TrampolineFlowCombinators
        from flowengine.flow import Flow

        # Create predicate that always returns False
        def always_false(ctx: Context) -> bool:
            return False

        # Create then_flow that would modify context
        def then_fn(ctx: Context) -> Context:
            result = ctx.fork()
            result["then_executed"] = True
            return result

        then_flow = Flow.from_sync_fn(then_fn)

        # Create conditional flow without else_flow
        conditional = TrampolineFlowCombinators.conditional_flow(
            always_false, then_flow
        )

        # Execute
        context = Context()
        context["original"] = "value"
        result = run_flow_with_input(conditional, context)

        # Should be unchanged
        assert "then_executed" not in result
        assert result["original"] == "value"

    def test_conditional_flow_context_based_predicate(self) -> None:
        """Test conditional_flow with context-based predicate logic."""
        from context_flow.integration import run_flow_with_input
        from context_flow.trampoline import TrampolineFlowCombinators

        # Create flows using helper method
        predicate, process_flow, skip_flow = self._create_status_flows()
        conditional = TrampolineFlowCombinators.conditional_flow(
            predicate, process_flow, skip_flow
        )

        # Test both pending and completed statuses
        test_cases = [
            ("pending", "completed", True, False),
            ("completed", "completed", False, True),
        ]

        for initial_status, final_status, has_processed, has_skipped in test_cases:
            context = Context()
            context["status"] = initial_status
            result = run_flow_with_input(conditional, context)

            assert result["status"] == final_status
            assert ("processed" in result) == has_processed
            assert ("skipped" in result) == has_skipped

    def test_conditional_flow_preserves_context_data(self) -> None:
        """Test that conditional_flow preserves existing context data."""
        from context_flow.integration import run_flow_with_input
        from context_flow.trampoline import TrampolineFlowCombinators
        from flowengine.flow import Flow

        # Create simple predicate and flows
        predicate = lambda ctx: ctx.get("execute", False)

        def add_data_fn(ctx: Context) -> Context:
            result = ctx.fork()
            result["added"] = "data"
            return result

        then_flow = Flow.from_sync_fn(add_data_fn)

        # Create conditional flow
        conditional = TrampolineFlowCombinators.conditional_flow(predicate, then_flow)

        # Execute with existing data
        context = Context()
        context["existing"] = "value"
        context["execute"] = True
        result = run_flow_with_input(conditional, context)

        # Both original and new data should be present
        assert result["existing"] == "value"
        assert result["added"] == "data"

    def test_conditional_flow_static_method(self) -> None:
        """Test that conditional_flow is a static method."""
        from context_flow.trampoline import TrampolineFlowCombinators

        # Method should be static
        method = getattr(TrampolineFlowCombinators, "conditional_flow")
        assert isinstance(method, staticmethod) or not hasattr(method, "__self__")

    def test_conditional_flow_flow_composition(self) -> None:
        """Test that conditional_flow can be composed with other flows."""
        from context_flow.trampoline import TrampolineFlowCombinators

        # Create flows using helper methods
        predicate, then_flow, else_flow = self._create_composition_flows()
        prefix_flow, suffix_flow = self._create_wrapper_flows()

        # Create conditional flow and compose
        conditional = TrampolineFlowCombinators.conditional_flow(
            predicate, then_flow, else_flow
        )
        composed = prefix_flow >> conditional >> suffix_flow

        # Execute and verify
        context = Context()
        context["condition"] = True
        result_generator = composed(self._async_iter_from_context(context))
        result = self._get_first_result(result_generator)

        assert result["prefix"] == "start"
        assert result["then_executed"] is True
        assert result["suffix"] == "end"

    def test_conditional_flow_documentation(self) -> None:
        """Test that conditional_flow has proper documentation."""
        from context_flow.trampoline import TrampolineFlowCombinators

        method = getattr(TrampolineFlowCombinators, "conditional_flow")
        assert method.__doc__ is not None
        assert len(method.__doc__.strip()) > 0
        assert "conditional" in method.__doc__.lower()
        assert "predicate" in method.__doc__.lower()

    def test_conditional_flow_flow_naming(self) -> None:
        """Test that conditional_flow creates flows with descriptive names."""
        from context_flow.trampoline import TrampolineFlowCombinators
        from flowengine.flow import Flow

        # Create test flows
        predicate = lambda ctx: True
        then_flow: "Flow[Context, Context]" = Flow.from_sync_fn(lambda ctx: ctx)
        conditional = TrampolineFlowCombinators.conditional_flow(predicate, then_flow)

        # Check that flow has a name
        assert hasattr(conditional, "name")
        assert isinstance(conditional.name, str)
        assert "conditional_flow" in conditional.name

    def test_conditional_flow_context_immutability(self) -> None:
        """Test that conditional_flow maintains context immutability."""
        from context_flow.integration import run_flow_with_input
        from context_flow.trampoline import TrampolineFlowCombinators
        from flowengine.flow import Flow

        # Create flow that modifies context
        def modify_fn(ctx: Context) -> Context:
            result = ctx.fork()
            result["modified"] = True
            return result

        predicate = lambda ctx: True
        then_flow = Flow.from_sync_fn(modify_fn)
        conditional = TrampolineFlowCombinators.conditional_flow(predicate, then_flow)

        # Execute with original context
        original_context = Context()
        original_context["original"] = "value"

        result = run_flow_with_input(conditional, original_context)

        # Original context should be unchanged
        assert "modified" not in original_context
        assert original_context["original"] == "value"

        # Result should have modifications
        assert result["modified"] is True
        assert result["original"] == "value"

    def test_conditional_flow_complex_predicates(self) -> None:
        """Test conditional_flow with complex predicate logic."""
        from context_flow.integration import run_flow_with_input
        from context_flow.trampoline import TrampolineFlowCombinators

        # Create flows using helper method
        predicate, high_priority_flow, normal_flow = self._create_priority_flows()
        conditional = TrampolineFlowCombinators.conditional_flow(
            predicate, high_priority_flow, normal_flow
        )

        # Test all priority combinations
        test_cases = [
            (10, "pending", "high_priority"),
            (3, "pending", "normal"),
            (10, "completed", "normal"),
        ]

        for priority, status, expected in test_cases:
            context = Context()
            context["priority"] = priority
            context["status"] = status
            result = run_flow_with_input(conditional, context)
            assert result["processing"] == expected

    def test_conditional_flow_error_handling(self) -> None:
        """Test conditional_flow behavior with predicate errors."""
        from context_flow.integration import run_flow_with_input
        from context_flow.trampoline import TrampolineFlowCombinators
        from flowengine.flow import Flow

        # Create predicate that may raise exception
        def error_predicate(ctx: Context) -> bool:
            value = ctx.get("value")
            if value is None:
                raise ValueError("Missing required value")
            return bool(value > 0)

        # Create flows
        then_flow: "Flow[Context, Context]" = Flow.from_sync_fn(lambda ctx: ctx.fork())
        conditional = TrampolineFlowCombinators.conditional_flow(
            error_predicate, then_flow
        )

        # Test that predicate errors propagate
        context = Context()  # No "value" key
        with pytest.raises(ValueError, match="Missing required value"):
            run_flow_with_input(conditional, context)

    def test_conditional_flow_multiple_contexts(self) -> None:
        """Test conditional_flow processing multiple contexts in stream."""
        from context_flow.trampoline import TrampolineFlowCombinators

        # Create flows using helper method
        predicate, double_flow, triple_flow = self._create_math_flows()
        conditional = TrampolineFlowCombinators.conditional_flow(
            predicate, double_flow, triple_flow
        )

        # Test with multiple contexts
        contexts = []
        for i in range(5):
            ctx = Context()
            ctx["number"] = i
            contexts.append(ctx)

        # Process through conditional flow
        results = []
        for ctx in contexts:
            result_generator = conditional(self._async_iter_from_context(ctx))
            result = self._get_first_result(result_generator)
            results.append(result)

        # Verify results: even numbers doubled, odd numbers tripled
        assert results[0]["result"] == 0  # 0 * 2 = 0 (even)
        assert results[1]["result"] == 3  # 1 * 3 = 3 (odd)
        assert results[2]["result"] == 4  # 2 * 2 = 4 (even)
        assert results[3]["result"] == 9  # 3 * 3 = 9 (odd)
        assert results[4]["result"] == 8  # 4 * 2 = 8 (even)

    # Helper methods for flow creation
    def _create_composition_flows(
        self,
    ) -> tuple[
        Callable[[Context], bool], "Flow[Context, Context]", "Flow[Context, Context]"
    ]:
        """Create flows for composition testing."""
        from flowengine.flow import Flow

        def predicate(ctx: Context) -> bool:
            return bool(ctx.get("condition", False) or False)

        def then_fn(ctx: Context) -> Context:
            result = ctx.fork()
            result["then_executed"] = True
            return result

        def else_fn(ctx: Context) -> Context:
            result = ctx.fork()
            result["else_executed"] = True
            return result

        return predicate, Flow.from_sync_fn(then_fn), Flow.from_sync_fn(else_fn)

    def _create_wrapper_flows(
        self,
    ) -> tuple["Flow[Context, Context]", "Flow[Context, Context]"]:
        """Create prefix and suffix flows for composition testing."""
        from flowengine.flow import Flow

        def prefix_fn(ctx: Context) -> Context:
            result = ctx.fork()
            result["prefix"] = "start"
            return result

        def suffix_fn(ctx: Context) -> Context:
            result = ctx.fork()
            result["suffix"] = "end"
            return result

        return Flow.from_sync_fn(prefix_fn), Flow.from_sync_fn(suffix_fn)

    def _create_priority_flows(
        self,
    ) -> tuple[
        Callable[[Context], bool], "Flow[Context, Context]", "Flow[Context, Context]"
    ]:
        """Create priority-based predicate and flows for testing."""
        from flowengine.flow import Flow

        def complex_predicate(ctx: Context) -> bool:
            priority = ctx.get("priority", 0) or 0
            status = ctx.get("status", "") or ""
            return priority > 5 and status == "pending"

        def high_priority_fn(ctx: Context) -> Context:
            result = ctx.fork()
            result["processing"] = "high_priority"
            return result

        def normal_fn(ctx: Context) -> Context:
            result = ctx.fork()
            result["processing"] = "normal"
            return result

        high_priority_flow = Flow.from_sync_fn(high_priority_fn)
        normal_flow = Flow.from_sync_fn(normal_fn)

        return complex_predicate, high_priority_flow, normal_flow

    def _create_status_flows(
        self,
    ) -> tuple[
        Callable[[Context], bool], "Flow[Context, Context]", "Flow[Context, Context]"
    ]:
        """Create status-based predicate and flows for testing."""
        from flowengine.flow import Flow

        def needs_processing(ctx: Context) -> bool:
            return ctx.get("status", "") == "pending"

        def process_fn(ctx: Context) -> Context:
            result = ctx.fork()
            result["status"] = "completed"
            result["processed"] = True
            return result

        def skip_fn(ctx: Context) -> Context:
            result = ctx.fork()
            result["skipped"] = True
            return result

        process_flow = Flow.from_sync_fn(process_fn)
        skip_flow = Flow.from_sync_fn(skip_fn)

        return needs_processing, process_flow, skip_flow

    def _create_math_flows(
        self,
    ) -> tuple[
        Callable[[Context], bool], "Flow[Context, Context]", "Flow[Context, Context]"
    ]:
        """Create math-based predicate and flows for testing."""
        from flowengine.flow import Flow

        def is_even(ctx: Context) -> bool:
            number = ctx.get("number", 0) or 0
            return (number % 2) == 0

        def double_fn(ctx: Context) -> Context:
            result = ctx.fork()
            number = ctx.get("number", 0) or 0
            result["result"] = number * 2
            return result

        def triple_fn(ctx: Context) -> Context:
            result = ctx.fork()
            number = ctx.get("number", 0) or 0
            result["result"] = number * 3
            return result

        double_flow = Flow.from_sync_fn(double_fn)
        triple_flow = Flow.from_sync_fn(triple_fn)

        return is_even, double_flow, triple_flow

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
