"""Tests for context_flow.integration utility functions."""

from collections.abc import AsyncGenerator
from typing import Any

import pytest

from context_flow.integration import _single_item_stream, run_flow_with_input
from flow.flow import Flow


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
            stream: AsyncGenerator[str, None],
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
            stream: AsyncGenerator[int, None],
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
            stream: AsyncGenerator[str, None],
        ) -> AsyncGenerator[str, None]:
            async for item in stream:
                yield item
                yield item  # Yield the same item twice

        flow: Flow[str, str] = Flow(duplicate_output)

        result: str = run_flow_with_input(flow, "test")

        # Should return the first result only
        assert result == "test"
