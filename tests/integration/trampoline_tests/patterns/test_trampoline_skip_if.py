"""Tests for context_flow.trampoline TrampolineFlowCombinators.skip_if method."""

from typing import TYPE_CHECKING, Any, Callable

import pytest

from context.main import Context

if TYPE_CHECKING:
    from flowengine.flow import Flow


class TestTrampolineFlowCombinatorsSkipIf:
    """Test cases for TrampolineFlowCombinators.skip_if method."""

    def test_skip_if_import(self) -> None:
        """Test that TrampolineFlowCombinators.skip_if can be imported."""
        from context_flow.trampoline import TrampolineFlowCombinators

        # Verify the class exists and has the method
        assert hasattr(TrampolineFlowCombinators, "skip_if")
        assert callable(getattr(TrampolineFlowCombinators, "skip_if"))

    def test_skip_if_method_signature(self) -> None:
        """Test that skip_if has correct method signature."""
        import inspect

        from context_flow.trampoline import TrampolineFlowCombinators

        # Get method signature
        method = getattr(TrampolineFlowCombinators, "skip_if")
        signature = inspect.signature(method)

        # Check parameters
        params = list(signature.parameters.keys())
        assert "predicate" in params
        assert "flow" in params
        assert len(params) == 2  # Only predicate and flow

    def test_skip_if_returns_flow(self) -> None:
        """Test that skip_if returns a Flow object."""
        from context_flow.trampoline import TrampolineFlowCombinators
        from flowengine.flow import Flow

        # Create test flow
        test_flow: "Flow[Context, Context]" = Flow.from_sync_fn(lambda ctx: ctx)
        predicate = lambda ctx: True

        # Test that it returns a Flow
        result = TrampolineFlowCombinators.skip_if(predicate, test_flow)
        assert isinstance(result, Flow)

    def test_skip_if_predicate_true_skips_flow(self) -> None:
        """Test that skip_if skips flow execution when predicate is True."""
        from context_flow.integration import run_flow_with_input
        from context_flow.trampoline import TrampolineFlowCombinators
        from flowengine.flow import Flow

        # Create predicate that always returns True (always skip)
        def always_skip(ctx: Context) -> bool:
            return True

        # Create flow that would modify context if executed
        def modify_fn(ctx: Context) -> Context:
            result = ctx.fork()
            result["executed"] = True
            return result

        test_flow = Flow.from_sync_fn(modify_fn)

        # Create skip_if flow
        skip_flow = TrampolineFlowCombinators.skip_if(always_skip, test_flow)

        # Execute
        context = Context()
        context["original"] = "value"
        result = run_flow_with_input(skip_flow, context)

        # Should be unchanged (flow was skipped)
        assert "executed" not in result
        assert result["original"] == "value"

    def test_skip_if_predicate_false_executes_flow(self) -> None:
        """Test that skip_if executes flow when predicate is False."""
        from context_flow.integration import run_flow_with_input
        from context_flow.trampoline import TrampolineFlowCombinators
        from flowengine.flow import Flow

        # Create predicate that always returns False (never skip)
        def never_skip(ctx: Context) -> bool:
            return False

        # Create flow that modifies context
        def modify_fn(ctx: Context) -> Context:
            result = ctx.fork()
            result["executed"] = True
            return result

        test_flow = Flow.from_sync_fn(modify_fn)

        # Create skip_if flow
        skip_flow = TrampolineFlowCombinators.skip_if(never_skip, test_flow)

        # Execute
        context = Context()
        context["original"] = "value"
        result = run_flow_with_input(skip_flow, context)

        # Should be modified (flow was executed)
        assert result["executed"] is True
        assert result["original"] == "value"

    def test_skip_if_context_based_predicate(self) -> None:
        """Test skip_if with context-based predicate logic."""
        from context_flow.trampoline import TrampolineFlowCombinators

        # Create flows using helper method
        predicate, process_flow = self._create_cache_flows()
        skip_flow = TrampolineFlowCombinators.skip_if(predicate, process_flow)

        # Test both skip and execute cases
        self._test_skip_case(skip_flow)
        self._test_execute_case(skip_flow)

    def test_skip_if_preserves_context_data(self) -> None:
        """Test that skip_if preserves existing context data in both cases."""
        from context_flow.integration import run_flow_with_input
        from context_flow.trampoline import TrampolineFlowCombinators
        from flowengine.flow import Flow

        # Create flow that adds data
        def add_data_fn(ctx: Context) -> Context:
            result = ctx.fork()
            result["added"] = "new_data"
            return result

        test_flow = Flow.from_sync_fn(add_data_fn)

        # Test both skip and execute cases
        for should_skip in [True, False]:
            predicate = lambda ctx: should_skip
            skip_flow = TrampolineFlowCombinators.skip_if(predicate, test_flow)

            context = Context()
            context["existing"] = "preserved"
            result = run_flow_with_input(skip_flow, context)

            # Existing data should always be preserved
            assert result["existing"] == "preserved"
            # New data added only when not skipped
            assert ("added" in result) == (not should_skip)

    def test_skip_if_static_method(self) -> None:
        """Test that skip_if is a static method."""
        from context_flow.trampoline import TrampolineFlowCombinators

        # Method should be static
        method = getattr(TrampolineFlowCombinators, "skip_if")
        assert isinstance(method, staticmethod) or not hasattr(method, "__self__")

    def test_skip_if_flow_composition(self) -> None:
        """Test that skip_if can be composed with other flows."""
        from context_flow.trampoline import TrampolineFlowCombinators

        # Create flows using helper methods
        predicate, process_flow = self._create_simple_flows()
        prefix_flow, suffix_flow = self._create_wrapper_flows()

        # Create skip_if flow and compose
        skip_flow = TrampolineFlowCombinators.skip_if(predicate, process_flow)
        composed = prefix_flow >> skip_flow >> suffix_flow

        # Execute and verify composition works
        context = Context()
        context["should_skip"] = False  # Will execute
        result_generator = composed(self._async_iter_from_context(context))
        result = self._get_first_result(result_generator)

        assert result["prefix"] == "start"
        assert result["processed"] is True
        assert result["suffix"] == "end"

    def test_skip_if_documentation(self) -> None:
        """Test that skip_if has proper documentation."""
        from context_flow.trampoline import TrampolineFlowCombinators

        method = getattr(TrampolineFlowCombinators, "skip_if")
        assert method.__doc__ is not None
        assert len(method.__doc__.strip()) > 0
        assert "skip" in method.__doc__.lower()
        assert "predicate" in method.__doc__.lower()

    def test_skip_if_flow_naming(self) -> None:
        """Test that skip_if creates flows with descriptive names."""
        from context_flow.trampoline import TrampolineFlowCombinators
        from flowengine.flow import Flow

        # Create test flows
        predicate = lambda ctx: True
        test_flow: "Flow[Context, Context]" = Flow.from_sync_fn(lambda ctx: ctx)
        skip_flow = TrampolineFlowCombinators.skip_if(predicate, test_flow)

        # Check that flow has a name
        assert hasattr(skip_flow, "name")
        assert isinstance(skip_flow.name, str)
        assert "skip_if" in skip_flow.name

    def test_skip_if_context_immutability(self) -> None:
        """Test that skip_if maintains context immutability."""
        from context_flow.integration import run_flow_with_input
        from context_flow.trampoline import TrampolineFlowCombinators
        from flowengine.flow import Flow

        # Create flow that modifies context
        def modify_fn(ctx: Context) -> Context:
            result = ctx.fork()
            result["modified"] = True
            return result

        test_flow = Flow.from_sync_fn(modify_fn)

        # Test both skip and execute cases
        for should_skip in [True, False]:
            predicate = lambda ctx: should_skip
            skip_flow = TrampolineFlowCombinators.skip_if(predicate, test_flow)

            # Execute with original context
            original_context = Context()
            original_context["original"] = "value"

            result = run_flow_with_input(skip_flow, original_context)

            # Original context should be unchanged
            assert "modified" not in original_context
            assert original_context["original"] == "value"

            # Result should have modifications only when not skipped
            assert ("modified" in result) == (not should_skip)
            assert result["original"] == "value"

    def test_skip_if_expensive_operation_pattern(self) -> None:
        """Test skip_if for avoiding expensive operations."""
        from context_flow.integration import run_flow_with_input
        from context_flow.trampoline import TrampolineFlowCombinators

        # Track whether expensive operation was called
        operation_calls = {"count": 0}

        # Create flows using helper method
        predicate, expensive_flow = self._create_expensive_flows(operation_calls)
        skip_flow = TrampolineFlowCombinators.skip_if(predicate, expensive_flow)

        # Test cases
        test_cases = [
            ("cached", 0),  # Skip expensive operation
            ("pending", 1),  # Execute expensive operation
            ("cached", 1),  # Skip again (no additional calls)
        ]

        for status, expected_calls in test_cases:
            context = Context()
            context["status"] = status
            result = run_flow_with_input(skip_flow, context)

            assert operation_calls["count"] == expected_calls
            if status == "cached":
                assert result["status"] == "cached"  # Unchanged
            else:
                assert result["status"] == "completed"  # Modified

    def test_skip_if_error_handling(self) -> None:
        """Test skip_if behavior with predicate errors."""
        from context_flow.integration import run_flow_with_input
        from context_flow.trampoline import TrampolineFlowCombinators
        from flowengine.flow import Flow

        # Create predicate that may raise exception
        def error_predicate(ctx: Context) -> bool:
            value = ctx.get("check_value")
            if value is None:
                raise ValueError("Missing required check_value")
            return bool(value)

        # Create test flow
        test_flow: "Flow[Context, Context]" = Flow.from_sync_fn(lambda ctx: ctx.fork())
        skip_flow = TrampolineFlowCombinators.skip_if(error_predicate, test_flow)

        # Test that predicate errors propagate
        context = Context()  # No "check_value" key
        with pytest.raises(ValueError, match="Missing required check_value"):
            run_flow_with_input(skip_flow, context)

    def test_skip_if_multiple_contexts(self) -> None:
        """Test skip_if processing multiple contexts in stream."""
        from context_flow.trampoline import TrampolineFlowCombinators

        # Create flows using helper method
        predicate, process_flow = self._create_toggle_flows()
        skip_flow = TrampolineFlowCombinators.skip_if(predicate, process_flow)

        # Test multiple contexts with different skip conditions
        test_data = [
            (True, "original"),  # Skip
            (False, "processed"),  # Execute
            (True, "original"),  # Skip
            (False, "processed"),  # Execute
        ]

        for skip_flag, expected_value in test_data:
            context = Context()
            context["skip"] = skip_flag
            context["value"] = "original"

            result_generator = skip_flow(self._async_iter_from_context(context))
            result = self._get_first_result(result_generator)

            assert result["value"] == expected_value

    def test_skip_if_caching_pattern(self) -> None:
        """Test skip_if implementing caching-like behavior."""
        from context_flow.integration import run_flow_with_input
        from context_flow.trampoline import TrampolineFlowCombinators

        # Create flows using helper method
        predicate, compute_flow = self._create_caching_flows()
        cached_flow = TrampolineFlowCombinators.skip_if(predicate, compute_flow)

        # Test caching behavior
        test_cases = [
            (None, "computed_value", True),  # Compute
            ("cached_value", "cached_value", False),  # Skip (cached)
            (None, "computed_value", True),  # Compute again
        ]

        for initial_value, expected_value, should_compute in test_cases:
            context = Context()
            if initial_value is not None:
                context["result"] = initial_value
            result = run_flow_with_input(cached_flow, context)

            assert result["result"] == expected_value
            assert ("computed" in result) == should_compute

    # Helper methods for flow creation
    def _create_cache_flows(
        self,
    ) -> tuple[Callable[[Context], bool], "Flow[Context, Context]"]:
        """Create cache-checking flows for testing."""
        from flowengine.flow import Flow

        def is_cached(ctx: Context) -> bool:
            return ctx.get("status", "") == "cached"

        def process_fn(ctx: Context) -> Context:
            result = ctx.fork()
            status = ctx.get("status", "")

            if status == "cached":
                # If already cached, set cached value
                result["value"] = "cached_value"
            else:
                # Process and set processed value
                result["value"] = "processed_value"
                result["processed"] = True

            return result

        return is_cached, Flow.from_sync_fn(process_fn)

    def _create_simple_flows(
        self,
    ) -> tuple[Callable[[Context], bool], "Flow[Context, Context]"]:
        """Create simple predicate and flow for testing."""
        from flowengine.flow import Flow

        def should_skip(ctx: Context) -> bool:
            return bool(ctx.get("should_skip", False))

        def process_fn(ctx: Context) -> Context:
            result = ctx.fork()
            result["processed"] = True
            return result

        return should_skip, Flow.from_sync_fn(process_fn)

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

    def _create_expensive_flows(
        self, operation_calls: dict[str, int]
    ) -> tuple[Callable[[Context], bool], "Flow[Context, Context]"]:
        """Create expensive operation flows for testing."""
        from flowengine.flow import Flow

        def is_cached(ctx: Context) -> bool:
            return ctx.get("status", "") == "cached"

        def expensive_fn(ctx: Context) -> Context:
            operation_calls["count"] += 1
            result = ctx.fork()
            result["status"] = "completed"
            result["expensive_result"] = "computed"
            return result

        return is_cached, Flow.from_sync_fn(expensive_fn)

    def _create_toggle_flows(
        self,
    ) -> tuple[Callable[[Context], bool], "Flow[Context, Context]"]:
        """Create toggle-based flows for testing."""
        from flowengine.flow import Flow

        def should_skip(ctx: Context) -> bool:
            return bool(ctx.get("skip", False))

        def process_fn(ctx: Context) -> Context:
            result = ctx.fork()
            result["value"] = "processed"
            return result

        return should_skip, Flow.from_sync_fn(process_fn)

    def _create_caching_flows(
        self,
    ) -> tuple[Callable[[Context], bool], "Flow[Context, Context]"]:
        """Create caching pattern flows for testing."""
        from flowengine.flow import Flow

        def has_result(ctx: Context) -> bool:
            return "result" in ctx

        def compute_fn(ctx: Context) -> Context:
            result = ctx.fork()
            result["result"] = "computed_value"
            result["computed"] = True
            return result

        return has_result, Flow.from_sync_fn(compute_fn)

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

    def _test_skip_case(self, skip_flow: Any) -> None:
        """Test case where predicate=True, should skip execution."""
        from context_flow.integration import run_flow_with_input

        context = Context()
        context["status"] = "cached"
        result = run_flow_with_input(skip_flow, context)

        # Should skip processing, return original context unchanged
        assert result["status"] == "cached"
        assert "value" not in result  # No processing occurred
        assert "processed" not in result

    def _test_execute_case(self, skip_flow: Any) -> None:
        """Test case where predicate=False, should execute flow."""
        from context_flow.integration import run_flow_with_input

        context = Context()
        context["status"] = "pending"
        result = run_flow_with_input(skip_flow, context)

        # Should execute processing
        assert result["value"] == "processed_value"
        assert result["processed"] is True
