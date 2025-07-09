"""Tests for context_flow.integration module."""

from collections.abc import AsyncGenerator, AsyncIterator
from typing import Any

import pytest

from context_flow.integration import (
    ContextFlowError,
    ContextTypeMismatchError,
    MissingRequiredKeyError,
    _single_item_stream,
    extend_flow_with_context,
    run_flow_with_input,
)
from flowengine.flow import Flow


class TestContextFlowError:
    """Test cases for ContextFlowError exception class."""

    def test_context_flow_error_is_exception(self) -> None:
        """Test that ContextFlowError inherits from Exception."""
        assert issubclass(ContextFlowError, Exception)

    def test_context_flow_error_instantiation(self) -> None:
        """Test that ContextFlowError can be instantiated."""
        error = ContextFlowError()
        assert isinstance(error, ContextFlowError)
        assert isinstance(error, Exception)

    def test_context_flow_error_with_message(self) -> None:
        """Test that ContextFlowError can be instantiated with a message."""
        message = "Test error message"
        error = ContextFlowError(message)
        assert str(error) == message

    def test_context_flow_error_can_be_raised(self) -> None:
        """Test that ContextFlowError can be raised and caught."""
        with pytest.raises(ContextFlowError) as exc_info:
            raise ContextFlowError("Test error")

        assert str(exc_info.value) == "Test error"

    def test_context_flow_error_can_be_caught_as_exception(self) -> None:
        """Test that ContextFlowError can be caught as base Exception."""
        with pytest.raises(Exception) as exc_info:
            raise ContextFlowError("Test error")

        assert isinstance(exc_info.value, ContextFlowError)

    def test_context_flow_error_empty_instantiation(self) -> None:
        """Test that ContextFlowError can be instantiated without arguments."""
        error = ContextFlowError()
        assert str(error) == ""

    def test_context_flow_error_multiple_args(self) -> None:
        """Test that ContextFlowError can be instantiated with multiple arguments."""
        error = ContextFlowError("First", "Second", "Third")
        assert error.args == ("First", "Second", "Third")


class TestMissingRequiredKeyError:
    """Test cases for MissingRequiredKeyError exception class."""

    def test_missing_required_key_error_inherits_from_context_flow_error(self) -> None:
        """Test that MissingRequiredKeyError inherits from ContextFlowError."""
        assert issubclass(MissingRequiredKeyError, ContextFlowError)

    def test_missing_required_key_error_inherits_from_exception(self) -> None:
        """Test that MissingRequiredKeyError inherits from Exception."""
        assert issubclass(MissingRequiredKeyError, Exception)

    def test_missing_required_key_error_instantiation(self) -> None:
        """Test that MissingRequiredKeyError can be instantiated."""
        error = MissingRequiredKeyError()
        assert isinstance(error, MissingRequiredKeyError)
        assert isinstance(error, ContextFlowError)
        assert isinstance(error, Exception)

    def test_missing_required_key_error_with_message(self) -> None:
        """Test that MissingRequiredKeyError can be instantiated with a message."""
        message = "Key 'user_id' is required but missing from context"
        error = MissingRequiredKeyError(message)
        assert str(error) == message

    def test_missing_required_key_error_can_be_raised(self) -> None:
        """Test that MissingRequiredKeyError can be raised and caught."""
        with pytest.raises(MissingRequiredKeyError) as exc_info:
            raise MissingRequiredKeyError("Missing key error")

        assert str(exc_info.value) == "Missing key error"

    def test_missing_required_key_error_can_be_caught_as_context_flow_error(
        self,
    ) -> None:
        """Test that MissingRequiredKeyError can be caught as ContextFlowError."""
        with pytest.raises(ContextFlowError) as exc_info:
            raise MissingRequiredKeyError("Missing key error")

        assert isinstance(exc_info.value, MissingRequiredKeyError)

    def test_missing_required_key_error_can_be_caught_as_exception(self) -> None:
        """Test that MissingRequiredKeyError can be caught as base Exception."""
        with pytest.raises(Exception) as exc_info:
            raise MissingRequiredKeyError("Missing key error")

        assert isinstance(exc_info.value, MissingRequiredKeyError)
        assert isinstance(exc_info.value, ContextFlowError)

    def test_missing_required_key_error_empty_instantiation(self) -> None:
        """Test that MissingRequiredKeyError can be instantiated without arguments."""
        error = MissingRequiredKeyError()
        assert str(error) == ""

    def test_missing_required_key_error_multiple_args(self) -> None:
        """Test that MissingRequiredKeyError can be instantiated with multiple arguments."""
        error = MissingRequiredKeyError(
            "Key missing", "Additional info", "More details"
        )
        assert error.args == ("Key missing", "Additional info", "More details")

    def test_missing_required_key_error_with_exception_chaining(self) -> None:
        """Test that MissingRequiredKeyError works with exception chaining."""
        original_error = KeyError("key_name")

        try:
            raise original_error
        except KeyError as e:
            with pytest.raises(MissingRequiredKeyError) as exc_info:
                raise MissingRequiredKeyError("Required key missing") from e

        assert exc_info.value.__cause__ == original_error
        assert str(exc_info.value) == "Required key missing"


class TestContextTypeMismatchError:
    """Test cases for ContextTypeMismatchError exception class."""

    def test_context_type_mismatch_error_inherits_from_context_flow_error(self) -> None:
        """Test that ContextTypeMismatchError inherits from ContextFlowError."""
        assert issubclass(ContextTypeMismatchError, ContextFlowError)

    def test_context_type_mismatch_error_inherits_from_exception(self) -> None:
        """Test that ContextTypeMismatchError inherits from Exception."""
        assert issubclass(ContextTypeMismatchError, Exception)

    def test_context_type_mismatch_error_instantiation(self) -> None:
        """Test that ContextTypeMismatchError can be instantiated."""
        error = ContextTypeMismatchError()
        assert isinstance(error, ContextTypeMismatchError)
        assert isinstance(error, ContextFlowError)
        assert isinstance(error, Exception)

    def test_context_type_mismatch_error_with_message(self) -> None:
        """Test that ContextTypeMismatchError can be instantiated with a message."""
        message = "Key 'user_id' expected str, got int"
        error = ContextTypeMismatchError(message)
        assert str(error) == message

    def test_context_type_mismatch_error_with_formatted_message(self) -> None:
        """Test that ContextTypeMismatchError works with formatted type messages."""
        key_path = "user.profile.age"
        expected_type = "int"
        actual_type = "str"
        message = f"Key '{key_path}' expected {expected_type}, got {actual_type}"
        error = ContextTypeMismatchError(message)
        assert str(error) == message

    def test_context_type_mismatch_error_can_be_raised(self) -> None:
        """Test that ContextTypeMismatchError can be raised and caught."""
        with pytest.raises(ContextTypeMismatchError) as exc_info:
            raise ContextTypeMismatchError("Type mismatch error")

        assert str(exc_info.value) == "Type mismatch error"

    def test_context_type_mismatch_error_can_be_caught_as_context_flow_error(
        self,
    ) -> None:
        """Test that ContextTypeMismatchError can be caught as ContextFlowError."""
        with pytest.raises(ContextFlowError) as exc_info:
            raise ContextTypeMismatchError("Type mismatch error")

        assert isinstance(exc_info.value, ContextTypeMismatchError)

    def test_context_type_mismatch_error_can_be_caught_as_exception(self) -> None:
        """Test that ContextTypeMismatchError can be caught as base Exception."""
        with pytest.raises(Exception) as exc_info:
            raise ContextTypeMismatchError("Type mismatch error")

        assert isinstance(exc_info.value, ContextTypeMismatchError)
        assert isinstance(exc_info.value, ContextFlowError)

    def test_context_type_mismatch_error_empty_instantiation(self) -> None:
        """Test that ContextTypeMismatchError can be instantiated without arguments."""
        error = ContextTypeMismatchError()
        assert str(error) == ""

    def test_context_type_mismatch_error_multiple_args(self) -> None:
        """Test that ContextTypeMismatchError can be instantiated with multiple arguments."""
        error = ContextTypeMismatchError("Type mismatch", "Expected int", "Got str")
        assert error.args == ("Type mismatch", "Expected int", "Got str")

    def test_context_type_mismatch_error_with_exception_chaining(self) -> None:
        """Test that ContextTypeMismatchError works with exception chaining."""
        original_error = TypeError("Invalid type conversion")

        try:
            raise original_error
        except TypeError as e:
            with pytest.raises(ContextTypeMismatchError) as exc_info:
                raise ContextTypeMismatchError("Context type mismatch") from e

        assert exc_info.value.__cause__ == original_error
        assert str(exc_info.value) == "Context type mismatch"

    def test_context_type_mismatch_error_with_type_names(self) -> None:
        """Test that ContextTypeMismatchError works with actual type names."""
        expected_type = int
        actual_type = str
        message = f"Expected {expected_type.__name__}, got {actual_type.__name__}"

        error = ContextTypeMismatchError(message)
        assert str(error) == "Expected int, got str"


class TestSingleItemStream:
    """Test cases for _single_item_stream function."""

    @pytest.mark.asyncio
    async def test_single_item_stream_basic_functionality(self) -> None:
        """Test that _single_item_stream yields exactly one item."""
        item = "test_item"

        stream = _single_item_stream(item)

        # Collect all items from the stream
        items = []
        async for result in stream:
            items.append(result)

        assert len(items) == 1
        assert items[0] == "test_item"

    @pytest.mark.asyncio
    async def test_single_item_stream_with_string(self) -> None:
        """Test _single_item_stream with string input."""
        item = "hello world"

        stream = _single_item_stream(item)

        async for result in stream:
            assert result == "hello world"
            assert isinstance(result, str)
            break

    @pytest.mark.asyncio
    async def test_single_item_stream_with_integer(self) -> None:
        """Test _single_item_stream with integer input."""
        item = 42

        stream = _single_item_stream(item)

        async for result in stream:
            assert result == 42
            assert isinstance(result, int)
            break

    @pytest.mark.asyncio
    async def test_single_item_stream_with_none(self) -> None:
        """Test _single_item_stream with None input."""
        item = None

        stream = _single_item_stream(item)

        async for result in stream:
            assert result is None
            break

    @pytest.mark.asyncio
    async def test_single_item_stream_with_list(self) -> None:
        """Test _single_item_stream with list input."""
        item = [1, 2, 3, "test"]

        stream = _single_item_stream(item)

        async for result in stream:
            assert result == [1, 2, 3, "test"]
            assert isinstance(result, list)
            break

    @pytest.mark.asyncio
    async def test_single_item_stream_with_dict(self) -> None:
        """Test _single_item_stream with dictionary input."""
        item = {"key": "value", "number": 42}

        stream = _single_item_stream(item)

        async for result in stream:
            assert result == {"key": "value", "number": 42}
            assert isinstance(result, dict)
            break

    @pytest.mark.asyncio
    async def test_single_item_stream_with_custom_object(self) -> None:
        """Test _single_item_stream with custom object input."""

        class CustomObject:
            def __init__(self, value: str):
                super().__init__()
                self.value = value

            def __eq__(self, other: object) -> bool:
                return isinstance(other, CustomObject) and self.value == other.value

        item = CustomObject("test_value")

        stream = _single_item_stream(item)

        async for result in stream:
            assert result == item
            assert isinstance(result, CustomObject)
            assert result.value == "test_value"
            break

    @pytest.mark.asyncio
    async def test_single_item_stream_exhaustible(self) -> None:
        """Test that _single_item_stream is properly exhaustible."""
        item = "test"

        stream = _single_item_stream(item)

        # First iteration should yield the item
        first_result = await stream.__anext__()
        assert first_result == "test"

        # Second iteration should raise StopAsyncIteration
        with pytest.raises(StopAsyncIteration):
            await stream.__anext__()

    @pytest.mark.asyncio
    async def test_single_item_stream_multiple_iterations(self) -> None:
        """Test that _single_item_stream can be iterated multiple times."""
        item = "test"

        # First iteration
        stream1 = _single_item_stream(item)
        async for result in stream1:
            assert result == "test"
            break

        # Second iteration with new stream
        stream2 = _single_item_stream(item)
        async for result in stream2:
            assert result == "test"
            break

    @pytest.mark.asyncio
    async def test_single_item_stream_type_preservation(self) -> None:
        """Test that _single_item_stream preserves the type of the input."""
        # Test with different types
        test_cases = [
            ("string", str),
            (123, int),
            (45.67, float),
            (True, bool),
            ([1, 2, 3], list),
            ({"key": "value"}, dict),
            ((1, 2, 3), tuple),
        ]

        for item, expected_type in test_cases:
            stream = _single_item_stream(item)
            async for result in stream:
                assert isinstance(result, expected_type)
                assert result == item
                break

    @pytest.mark.asyncio
    async def test_single_item_stream_with_empty_string(self) -> None:
        """Test _single_item_stream with empty string."""
        item = ""

        stream = _single_item_stream(item)

        async for result in stream:
            assert result == ""
            assert isinstance(result, str)
            break

    @pytest.mark.asyncio
    async def test_single_item_stream_with_zero(self) -> None:
        """Test _single_item_stream with zero value."""
        item = 0

        stream = _single_item_stream(item)

        async for result in stream:
            assert result == 0
            assert isinstance(result, int)
            break

    @pytest.mark.asyncio
    async def test_single_item_stream_with_false(self) -> None:
        """Test _single_item_stream with False boolean."""
        item = False

        stream = _single_item_stream(item)

        async for result in stream:
            assert result is False
            assert isinstance(result, bool)
            break

    @pytest.mark.asyncio
    async def test_single_item_stream_with_empty_list(self) -> None:
        """Test _single_item_stream with empty list."""
        item: list[int] = []

        stream = _single_item_stream(item)

        async for result in stream:
            assert result == []
            assert isinstance(result, list)
            break

    @pytest.mark.asyncio
    async def test_single_item_stream_reference_preservation(self) -> None:
        """Test that _single_item_stream preserves object references."""
        item = {"mutable": "object"}

        stream = _single_item_stream(item)

        async for result in stream:
            assert result is item  # Same object reference
            assert result == item  # Same content
            break


class TestRunFlowWithInput:
    """Test cases for run_flow_with_input function."""

    def test_run_flow_with_input_basic_functionality(self) -> None:
        """Test that run_flow_with_input runs a flow with a single input and returns the result."""
        # Create a simple flow that doubles the input
        flow: Flow[int, int] = Flow.from_sync_fn(lambda x: x * 2)

        result: int = run_flow_with_input(flow, 5)

        assert result == 10

    def test_run_flow_with_input_with_string(self) -> None:
        """Test run_flow_with_input with string input and output."""
        flow: Flow[str, str] = Flow.from_sync_fn(lambda x: x.upper())

        result: str = run_flow_with_input(flow, "hello")

        assert result == "HELLO"

    def test_run_flow_with_input_with_type_transformation(self) -> None:
        """Test run_flow_with_input with type transformation."""
        flow: Flow[int, str] = Flow.from_sync_fn(lambda x: str(x))

        result: str = run_flow_with_input(flow, 42)

        assert result == "42"
        assert isinstance(result, str)

    def test_run_flow_with_input_with_identity_flow(self) -> None:
        """Test run_flow_with_input with identity flow."""
        flow: Flow[str, str] = Flow.from_sync_fn(lambda x: x)

        result: str = run_flow_with_input(flow, "test")

        assert result == "test"

    def test_run_flow_with_input_with_none_input(self) -> None:
        """Test run_flow_with_input with None input."""
        flow: Flow[Any, bool] = Flow.from_sync_fn(lambda x: x is None)

        result: bool = run_flow_with_input(flow, None)

        assert result is True

    def test_run_flow_with_input_with_complex_object(self) -> None:
        """Test run_flow_with_input with complex object input."""

        class TestObject:
            def __init__(self, value: int):
                super().__init__()
                self.value = value

            def __eq__(self, other: object) -> bool:
                return isinstance(other, TestObject) and self.value == other.value

        flow: Flow[TestObject, TestObject] = Flow.from_sync_fn(
            lambda obj: TestObject(obj.value * 2)
        )
        input_obj = TestObject(5)

        result: TestObject = run_flow_with_input(flow, input_obj)

        assert isinstance(result, TestObject)
        assert result.value == 10

    def test_run_flow_with_input_with_async_flow(self) -> None:
        """Test run_flow_with_input with async flow."""

        async def async_transform(x: int) -> int:
            return x * 3

        flow: Flow[int, int] = Flow.from_value_fn(async_transform)

        result: int = run_flow_with_input(flow, 4)

        assert result == 12

    def test_run_flow_with_input_with_chained_flows(self) -> None:
        """Test run_flow_with_input with chained flows."""
        flow1: Flow[int, int] = Flow.from_sync_fn(lambda x: x * 2)
        flow2: Flow[int, int] = Flow.from_sync_fn(lambda x: x + 1)

        chained_flow = flow1 >> flow2

        result: int = run_flow_with_input(chained_flow, 3)

        assert result == 7  # (3 * 2) + 1

    def test_run_flow_with_input_with_exception_in_flow(self) -> None:
        """Test run_flow_with_input properly propagates exceptions from flows."""

        def failing_transform(x: int) -> int:
            if x == 0:
                raise ValueError("Cannot process zero")
            return x * 2

        flow: Flow[int, int] = Flow.from_sync_fn(failing_transform)

        with pytest.raises(ValueError, match="Cannot process zero"):
            run_flow_with_input(flow, 0)

    def test_run_flow_with_input_with_empty_flow(self) -> None:
        """Test run_flow_with_input with a flow that produces no output."""

        async def empty_flow(
            stream: AsyncGenerator[str, None]
        ) -> AsyncGenerator[str, None]:
            async for _ in stream:
                pass  # Consume input but yield nothing
            return
            yield  # This line is never reached, making it a generator

        flow: Flow[str, str] = Flow(empty_flow)

        with pytest.raises(RuntimeError, match="Flow produced no output"):
            run_flow_with_input(flow, "test")

    def test_run_flow_with_input_type_preservation(self) -> None:
        """Test that run_flow_with_input preserves types correctly."""
        # Test with different input/output type combinations
        test_cases = [
            (lambda x: x, "string", str),
            (lambda x: x, 42, int),
            (lambda x: x, 3.14, float),
            (lambda x: x, True, bool),
            (lambda x: x, [1, 2, 3], list),
            (lambda x: x, {"key": "value"}, dict),
        ]

        for transform_fn, input_val, expected_type in test_cases:
            flow: Flow[Any, Any] = Flow.from_sync_fn(transform_fn)
            result: Any = run_flow_with_input(flow, input_val)

            assert isinstance(result, expected_type)
            assert result == input_val

    def test_run_flow_with_input_with_filtering_flow(self) -> None:
        """Test run_flow_with_input with a flow that filters items."""

        async def filter_even(
            stream: AsyncGenerator[int, None]
        ) -> AsyncGenerator[int, None]:
            async for item in stream:
                if item % 2 == 0:
                    yield item

        flow: Flow[int, int] = Flow(filter_even)

        # Test with even number (should return the number)
        result: int = run_flow_with_input(flow, 4)
        assert result == 4

        # Test with odd number (should raise RuntimeError)
        with pytest.raises(RuntimeError, match="Flow produced no output"):
            run_flow_with_input(flow, 3)

    def test_run_flow_with_input_with_multiple_output_flow(self) -> None:
        """Test run_flow_with_input with a flow that produces multiple outputs."""

        async def duplicate_output(
            stream: AsyncGenerator[str, None]
        ) -> AsyncGenerator[str, None]:
            async for item in stream:
                yield item
                yield item  # Yield the same item twice

        flow: Flow[str, str] = Flow(duplicate_output)

        result: str = run_flow_with_input(flow, "test")

        # Should return the first result only
        assert result == "test"


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
