"""Tests for context_flow.integration flow extensions and decorators."""

from typing import Any

import pytest

from context_flow.integration import (
    context_flow,
    extend_flow_with_context,
    run_flow_with_input,
)
from flowengine.flow import Flow


class TestExtendFlowWithContext:
    """Test cases for extend_flow_with_context function."""

    def test_extend_flow_with_context_adds_methods_to_flow(self) -> None:
        """Test that extend_flow_with_context adds methods to Flow class."""
        from flowengine.flow import Flow

        # Before extending, Flow should not have added methods
        assert not hasattr(Flow, "run")
        assert not hasattr(Flow, "then")

        # Extend Flow with context methods
        extend_flow_with_context()

        # After extending, Flow should have added methods
        assert hasattr(Flow, "run")
        assert hasattr(Flow, "then")
        assert callable(getattr(Flow, "run"))
        assert callable(getattr(Flow, "then"))

    def test_extend_flow_with_context_run_method(self) -> None:
        """Test that the added run method works correctly."""
        from flowengine.flow import Flow

        extend_flow_with_context()

        # Create a simple flow
        flow: Flow[int, int] = Flow.from_sync_fn(lambda x: x * 2)

        # Test that run method works
        result: int = flow.run(5)  # type: ignore[attr-defined]
        assert result == 10

    def test_extend_flow_with_context_then_method(self) -> None:
        """Test that the added then method works correctly."""
        from flowengine.flow import Flow

        extend_flow_with_context()

        # Create two flows
        flow1: Flow[int, int] = Flow.from_sync_fn(lambda x: x * 2)
        flow2: Flow[int, int] = Flow.from_sync_fn(lambda x: x + 1)

        # Test that then method works as alias for >>
        chained_with_then: Flow[int, int] = flow1.then(flow2)  # type: ignore[attr-defined]
        chained_with_operator: Flow[int, int] = flow1 >> flow2

        # Both should produce the same result
        result1: int = chained_with_then.run(5)  # type: ignore[attr-defined]
        result2: int = chained_with_operator.run(5)  # type: ignore[attr-defined]
        assert result1 == result2 == 11  # (5 * 2) + 1

    def test_extend_flow_with_context_run_with_different_types(self) -> None:
        """Test that the run method works with different input/output types."""
        from flowengine.flow import Flow

        extend_flow_with_context()

        # Test with string input/output
        string_flow: Flow[str, str] = Flow.from_sync_fn(lambda x: x.upper())
        result_str: str = string_flow.run("hello")  # type: ignore[attr-defined]
        assert result_str == "HELLO"

        # Test with type transformation
        transform_flow: Flow[int, str] = Flow.from_sync_fn(lambda x: str(x))
        result_transform: str = transform_flow.run(42)  # type: ignore[attr-defined]
        assert result_transform == "42"

    def test_extend_flow_with_context_chaining_with_run(self) -> None:
        """Test that chaining flows with then method and run works correctly."""
        from flowengine.flow import Flow

        extend_flow_with_context()

        # Create a chain of flows
        flow1: Flow[int, int] = Flow.from_sync_fn(lambda x: x * 2)
        flow2: Flow[int, int] = Flow.from_sync_fn(lambda x: x + 3)
        flow3: Flow[int, int] = Flow.from_sync_fn(lambda x: x * 10)

        # Chain them using then method
        chained_flow: Flow[int, int] = flow1.then(flow2).then(flow3)  # type: ignore[attr-defined]

        # Test the result
        result: int = chained_flow.run(5)  # type: ignore[attr-defined]
        assert result == 130  # ((5 * 2) + 3) * 10

    def test_extend_flow_with_context_multiple_calls(self) -> None:
        """Test that calling extend_flow_with_context multiple times is safe."""
        from flowengine.flow import Flow

        # Call extend_flow_with_context multiple times
        extend_flow_with_context()
        extend_flow_with_context()
        extend_flow_with_context()

        # Should still work correctly
        flow: Flow[int, int] = Flow.from_sync_fn(lambda x: x * 2)
        result: int = flow.run(5)  # type: ignore[attr-defined]
        assert result == 10

    def test_extend_flow_with_context_async_flows(self) -> None:
        """Test that the extended methods work with async flows."""
        from flowengine.flow import Flow

        extend_flow_with_context()

        # Create an async flow
        async def async_double(x: int) -> int:
            return x * 2

        flow: Flow[int, int] = Flow.from_value_fn(async_double)

        # Test that run method works with async flows
        result: int = flow.run(5)  # type: ignore[attr-defined]
        assert result == 10

    def test_extend_flow_with_context_preserves_existing_methods(self) -> None:
        """Test that extending Flow preserves existing methods."""
        from flowengine.flow import Flow

        # Check that original methods exist before extending
        assert hasattr(Flow, "from_sync_fn")
        assert hasattr(Flow, "__rshift__")
        assert hasattr(Flow, "map")
        assert hasattr(Flow, "filter")

        extend_flow_with_context()

        # Check that original methods still exist after extending
        assert hasattr(Flow, "from_sync_fn")
        assert hasattr(Flow, "__rshift__")
        assert hasattr(Flow, "map")
        assert hasattr(Flow, "filter")

        # Test that original methods still work
        flow: Flow[int, int] = Flow.from_sync_fn(lambda x: x * 2)
        mapped_flow: Flow[int, str] = flow.map(str)
        result: str = mapped_flow.run(5)  # type: ignore[attr-defined]
        assert result == "10"


class TestContextFlowDecorator:
    """Test cases for context_flow decorator function."""

    def test_context_flow_basic_functionality(self) -> None:
        """Test that context_flow decorator creates a working flow."""
        from context.main import Context

        @context_flow()
        async def simple_processor(item: int, context: Context) -> int:
            return item * 2

        # Test that decorator returns a Flow instance
        assert isinstance(simple_processor, Flow)

        # Test that the flow works with run_flow_with_input
        result: int = run_flow_with_input(simple_processor, 5)
        assert result == 10

    def test_context_flow_with_name(self) -> None:
        """Test that context_flow decorator uses custom name."""

        @context_flow(name="custom_flow")
        async def processor(item: int, context: Any) -> int:
            return item * 2

        # Test that flow has the custom name
        assert processor.name == "custom_flow"

    def test_context_flow_with_required_keys_success(self) -> None:
        """Test that context_flow works when required keys are present."""
        from context.main import Context

        @context_flow(required_keys=["user_id"])
        async def user_processor(item: str, context: Context) -> str:
            # Set the required key in context
            context["user_id"] = "test_user"
            user_id = context.get("user_id", "unknown")
            return f"{item}_{user_id}"

        # This should work without error since we set the required key
        result: str = run_flow_with_input(user_processor, "test")
        assert result == "test_test_user"

    def test_context_flow_with_required_keys_missing(self) -> None:
        """Test that context_flow raises error when required keys are missing."""
        from context_flow.integration import MissingRequiredKeyError

        @context_flow(required_keys=["user_id"])
        async def user_processor(item: str, context: Any) -> str:
            return item

        # This should raise MissingRequiredKeyError
        with pytest.raises(
            MissingRequiredKeyError, match="Required context key 'user_id' is missing"
        ):
            run_flow_with_input(user_processor, "test")

    def test_context_flow_with_type_hints_success(self) -> None:
        """Test that context_flow validates types correctly when they match."""
        from context.main import Context

        @context_flow(type_hints={"count": int})
        async def count_processor(item: str, context: Context) -> str:
            # Set a context value that matches the type hint
            context["count"] = 42
            count = context.get("count", 0)
            return f"{item}_{count}"

        # This should work without error
        result: str = run_flow_with_input(count_processor, "test")
        assert result == "test_42"

    def test_context_flow_with_type_hints_mismatch(self) -> None:
        """Test that context_flow raises error when types don't match."""
        from context.main import Context
        from context_flow.integration import ContextTypeMismatchError

        @context_flow(type_hints={"count": int})
        async def count_processor(item: str, context: Context) -> str:
            # Set a context value that doesn't match the type hint
            context["count"] = "not_an_int"
            return item

        # This should raise ContextTypeMismatchError
        with pytest.raises(
            ContextTypeMismatchError, match="Context key 'count' expected int, got str"
        ):
            run_flow_with_input(count_processor, "test")

    def test_context_flow_with_context_keys_filtering(self) -> None:
        """Test that context_flow filters context keys correctly."""
        from context.main import Context

        @context_flow(context_keys=["user_id", "session_id"])
        async def filtered_processor(item: str, context: Context) -> str:
            # Context should only contain the specified keys
            available_keys = list(context.keys())
            return f"{item}_{len(available_keys)}"

        # Test that the flow works with filtered context
        result: str = run_flow_with_input(filtered_processor, "test")
        assert result == "test_0"  # Empty context, so 0 keys

    def test_context_flow_integration_with_flow_operations(self) -> None:
        """Test that context_flow works with standard flow operations."""
        from context.main import Context

        @context_flow()
        async def double_processor(item: int, context: Context) -> int:
            return item * 2

        @context_flow()
        async def add_processor(item: int, context: Context) -> int:
            return item + 1

        # Test chaining context flows
        chained_flow = double_processor >> add_processor
        result: int = run_flow_with_input(chained_flow, 5)
        assert result == 11  # (5 * 2) + 1

    def test_context_flow_preserves_function_name(self) -> None:
        """Test that context_flow preserves function name when no custom name is provided."""

        @context_flow()
        async def my_processor(item: int, context: Any) -> int:
            return item * 2

        # Test that flow has the function name
        assert my_processor.name == "my_processor"

    def test_context_flow_with_complex_type_validation(self) -> None:
        """Test that context_flow works with complex type validations."""
        from context.main import Context

        @context_flow(
            required_keys=["user_id"],
            type_hints={"user_id": str, "score": int},
            context_keys=["user_id", "score"],
        )
        async def complex_processor(item: str, context: Context) -> str:
            # Set context values that match type hints
            context["user_id"] = "user123"
            context["score"] = 100
            return f"{item}_{context.get('user_id')}_{context.get('score')}"

        # This should work without error
        result: str = run_flow_with_input(complex_processor, "test")
        assert result == "test_user123_100"

    def test_context_flow_error_propagation(self) -> None:
        """Test that context_flow properly propagates errors from decorated functions."""

        @context_flow()
        async def error_processor(item: str, context: Any) -> str:
            if item == "error":
                raise ValueError("Test error")
            return item

        # Test that errors are propagated correctly
        with pytest.raises(ValueError, match="Test error"):
            run_flow_with_input(error_processor, "error")

        # Test that normal processing still works
        result: str = run_flow_with_input(error_processor, "success")
        assert result == "success"
