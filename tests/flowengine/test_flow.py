from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Any

import pytest

from flowengine.flow import Flow


def get_mock_flow(overrides: dict[str, Any] | None = None) -> Flow[int, str]:
    """Factory for creating test flows."""
    base_metadata = {"test": True}

    async def default_fn(stream: AsyncIterator[int]) -> AsyncIterator[str]:
        async for item in stream:
            yield str(item)

    fn = default_fn
    name = "test_flow"
    metadata = base_metadata

    if overrides:
        fn = overrides.get("fn", default_fn)
        name = overrides.get("name", "test_flow")
        metadata = overrides.get("metadata", base_metadata)

    return Flow(fn, name, metadata)


class TestFlowInit:
    """Tests for Flow.__init__ method."""

    def test_init_with_function_only(self) -> None:
        """Test Flow initialization with just a function."""

        async def test_fn(stream: AsyncIterator[int]) -> AsyncIterator[str]:
            async for item in stream:
                yield str(item)

        flow = Flow(test_fn)

        assert flow.fn is test_fn
        assert flow.name == "<anonymous>"
        assert flow.metadata == {}
        assert flow.__name__ == "<anonymous>"

    def test_init_with_name(self) -> None:
        """Test Flow initialization with a name."""

        async def test_fn(stream: AsyncIterator[int]) -> AsyncIterator[str]:
            async for item in stream:
                yield str(item)

        flow = Flow(test_fn, name="my_flow")

        assert flow.fn is test_fn
        assert flow.name == "my_flow"
        assert flow.metadata == {}
        assert flow.__name__ == "my_flow"

    def test_init_with_metadata(self) -> None:
        """Test Flow initialization with metadata."""

        async def test_fn(stream: AsyncIterator[int]) -> AsyncIterator[str]:
            async for item in stream:
                yield str(item)

        metadata = {"key": "value", "number": 42}
        flow = Flow(test_fn, metadata=metadata)

        assert flow.fn is test_fn
        assert flow.name == "<anonymous>"
        assert flow.metadata == metadata
        assert flow.__name__ == "<anonymous>"

    def test_init_with_none_metadata(self) -> None:
        """Test Flow initialization with explicit None metadata."""

        async def test_fn(stream: AsyncIterator[int]) -> AsyncIterator[str]:
            async for item in stream:
                yield str(item)

        flow = Flow(test_fn, metadata=None)

        assert flow.fn is test_fn
        assert flow.name == "<anonymous>"
        assert flow.metadata == {}
        assert flow.__name__ == "<anonymous>"

    def test_init_with_all_parameters(self) -> None:
        """Test Flow initialization with all parameters."""

        async def test_fn(stream: AsyncIterator[int]) -> AsyncIterator[str]:
            async for item in stream:
                yield str(item)

        metadata = {"description": "test flow", "version": 1}
        flow = Flow(test_fn, name="complete_flow", metadata=metadata)

        assert flow.fn is test_fn
        assert flow.name == "complete_flow"
        assert flow.metadata == metadata
        assert flow.__name__ == "complete_flow"


class TestFlowCall:
    """Tests for Flow.__call__ method."""

    @pytest.mark.asyncio
    async def test_call_returns_async_iterator(self) -> None:
        """Test that calling a flow returns an async iterator."""

        async def test_fn(stream: AsyncIterator[int]) -> AsyncIterator[str]:
            async for item in stream:
                yield str(item)

        flow = Flow(test_fn)

        async def test_stream() -> AsyncIterator[int]:
            for i in [1, 2, 3]:
                yield i

        result = flow(test_stream())

        # Should return an async iterator
        assert hasattr(result, "__aiter__")
        assert hasattr(result, "__anext__")

    @pytest.mark.asyncio
    async def test_call_processes_stream(self) -> None:
        """Test that calling a flow processes the input stream correctly."""

        async def double_fn(stream: AsyncIterator[int]) -> AsyncIterator[int]:
            async for item in stream:
                yield item * 2

        flow = Flow(double_fn)

        async def test_stream() -> AsyncIterator[int]:
            for i in [1, 2, 3]:
                yield i

        result = flow(test_stream())
        items = [item async for item in result]

        assert items == [2, 4, 6]

    @pytest.mark.asyncio
    async def test_call_empty_stream(self) -> None:
        """Test that calling a flow with empty stream works correctly."""

        async def test_fn(stream: AsyncIterator[int]) -> AsyncIterator[str]:
            async for item in stream:
                yield str(item)

        flow = Flow(test_fn)

        async def empty_stream() -> AsyncIterator[int]:
            return
            yield  # pragma: no cover

        result = flow(empty_stream())
        items = [item async for item in result]

        assert items == []

    @pytest.mark.asyncio
    async def test_call_delegates_to_fn(self) -> None:
        """Test that __call__ properly delegates to the internal function."""

        async def transform_fn(stream: AsyncIterator[int]) -> AsyncIterator[str]:
            async for item in stream:
                yield f"item_{item}"

        flow = Flow(transform_fn)

        async def test_stream() -> AsyncIterator[int]:
            for i in [10, 20]:
                yield i

        result = flow(test_stream())
        items = [item async for item in result]

        assert items == ["item_10", "item_20"]


class TestFlowRepr:
    """Tests for Flow.__repr__ method."""

    def test_repr_with_anonymous_flow(self) -> None:
        """Test __repr__ with default anonymous flow name."""

        async def test_fn(stream: AsyncIterator[int]) -> AsyncIterator[str]:
            async for item in stream:
                yield str(item)

        flow = Flow(test_fn)
        repr_str = repr(flow)

        assert "Flow" in repr_str
        assert "name='<anonymous>'" in repr_str
        assert "fn=test_fn" in repr_str
        assert "metadata={}" in repr_str

    def test_repr_with_named_flow(self) -> None:
        """Test __repr__ with custom flow name."""

        async def transform_data(stream: AsyncIterator[int]) -> AsyncIterator[str]:
            async for item in stream:
                yield f"data_{item}"

        flow = Flow(transform_data, name="my_transformer")
        repr_str = repr(flow)

        assert "Flow" in repr_str
        assert "name='my_transformer'" in repr_str
        assert "fn=transform_data" in repr_str
        assert "metadata={}" in repr_str

    def test_repr_with_metadata(self) -> None:
        """Test __repr__ with metadata included."""

        async def process_fn(stream: AsyncIterator[int]) -> AsyncIterator[str]:
            async for item in stream:
                yield str(item * 2)

        metadata = {"version": 1, "type": "processor"}
        flow = Flow(process_fn, name="processor", metadata=metadata)
        repr_str = repr(flow)

        assert "Flow" in repr_str
        assert "name='processor'" in repr_str
        assert "fn=process_fn" in repr_str
        assert "metadata={'version': 1, 'type': 'processor'}" in repr_str

    def test_repr_format_structure(self) -> None:
        """Test that __repr__ follows the expected format structure."""

        async def example_fn(stream: AsyncIterator[int]) -> AsyncIterator[str]:
            async for item in stream:
                yield str(item)

        flow = Flow(example_fn, name="test", metadata={"key": "value"})
        repr_str = repr(flow)

        # Should start with <Flow and end with >
        assert repr_str.startswith("<Flow")
        assert repr_str.endswith(">")

        # Should contain all required components
        assert "name=" in repr_str
        assert "fn=" in repr_str
        assert "metadata=" in repr_str


class TestFlowAiter:
    """Tests for Flow.__aiter__ method."""

    def test_aiter_raises_type_error(self) -> None:
        """Test that __aiter__ raises TypeError to prevent direct iteration."""

        async def test_fn(stream: AsyncIterator[int]) -> AsyncIterator[str]:
            async for item in stream:
                yield str(item)

        flow = Flow(test_fn)

        with pytest.raises(TypeError) as exc_info:
            aiter(flow)

        error_message = str(exc_info.value)
        assert "Flows must be called with a stream" in error_message
        assert "flow(stream)" in error_message

    def test_aiter_error_message_content(self) -> None:
        """Test that __aiter__ provides helpful error message."""

        async def transform_fn(stream: AsyncIterator[int]) -> AsyncIterator[str]:
            async for item in stream:
                yield f"transformed_{item}"

        flow = Flow(transform_fn, name="transformer")

        with pytest.raises(TypeError) as exc_info:
            aiter(flow)

        error_message = str(exc_info.value)
        # Check that error message explains the correct usage
        assert "Flows must be called with a stream to get an iterator" in error_message
        assert "e.g., flow(stream)" in error_message

    @pytest.mark.asyncio
    async def test_aiter_prevents_async_for_direct_usage(self) -> None:
        """Test that flows cannot be used directly in async for loops."""

        async def simple_fn(stream: AsyncIterator[int]) -> AsyncIterator[int]:
            async for item in stream:
                yield item * 2

        flow = Flow(simple_fn)

        # This should raise TypeError when trying to use flow directly
        with pytest.raises(TypeError):
            # This would attempt to call __aiter__(flow) internally
            # We have to trigger it with aiter() since async comprehension
            # syntax checking happens at compile time
            async for item in flow:  # type: ignore[attr-defined]
                pass


class TestFlowMap:
    """Tests for Flow.map method."""

    @pytest.mark.asyncio
    async def test_map_transforms_values(self) -> None:
        """Test that map applies function to each item in the stream."""

        async def source_fn(stream: AsyncIterator[None]) -> AsyncIterator[int]:
            for i in [1, 2, 3]:
                yield i

        def double(x: int) -> int:
            return x * 2

        flow = Flow(source_fn, name="source")
        mapped_flow = flow.map(double)

        async def empty_stream() -> AsyncIterator[None]:
            return
            yield  # pragma: no cover

        result = mapped_flow(empty_stream())
        items = [item async for item in result]

        assert items == [2, 4, 6]

    @pytest.mark.asyncio
    async def test_map_changes_output_type(self) -> None:
        """Test that map can change the output type of the flow."""

        async def int_source(stream: AsyncIterator[None]) -> AsyncIterator[int]:
            for i in [10, 20, 30]:
                yield i

        def int_to_string(x: int) -> str:
            return f"value_{x}"

        flow = Flow(int_source, name="int_source")
        string_flow = flow.map(int_to_string)

        async def empty_stream() -> AsyncIterator[None]:
            return
            yield  # pragma: no cover

        result = string_flow(empty_stream())
        items = [item async for item in result]

        assert items == ["value_10", "value_20", "value_30"]

    @pytest.mark.asyncio
    async def test_map_preserves_input_type(self) -> None:
        """Test that map preserves the input type of the original flow."""

        async def transform_fn(stream: AsyncIterator[str]) -> AsyncIterator[int]:
            async for item in stream:
                yield len(item)

        def square(x: int) -> int:
            return x * x

        flow = Flow(transform_fn, name="transform")
        mapped_flow = flow.map(square)

        async def string_stream() -> AsyncIterator[str]:
            for s in ["hi", "test", "hello"]:
                yield s

        result = mapped_flow(string_stream())
        items = [item async for item in result]

        assert items == [4, 16, 25]  # len("hi")^2, len("test")^2, len("hello")^2

    def test_map_creates_new_flow_with_descriptive_name(self) -> None:
        """Test that map creates a new flow with a descriptive name."""

        async def test_fn(stream: AsyncIterator[int]) -> AsyncIterator[str]:
            async for item in stream:
                yield str(item)

        def upper_fn(s: str) -> str:
            return s.upper()

        flow = Flow(test_fn, name="stringify")
        mapped_flow = flow.map(upper_fn)

        assert mapped_flow.name == "stringify.map(upper_fn)"
        assert mapped_flow is not flow  # Should be a new flow instance

    @pytest.mark.asyncio
    async def test_map_with_empty_stream(self) -> None:
        """Test that map works correctly with empty streams."""

        async def empty_source(stream: AsyncIterator[None]) -> AsyncIterator[int]:
            return
            yield  # pragma: no cover

        def multiply_by_ten(x: int) -> int:
            return x * 10

        flow = Flow(empty_source, name="empty")
        mapped_flow = flow.map(multiply_by_ten)

        async def empty_stream() -> AsyncIterator[None]:
            return
            yield  # pragma: no cover

        result = mapped_flow(empty_stream())
        items = [item async for item in result]

        assert items == []

    @pytest.mark.asyncio
    async def test_map_chaining(self) -> None:
        """Test that multiple maps can be chained together."""

        async def source_fn(stream: AsyncIterator[None]) -> AsyncIterator[int]:
            for i in [1, 2, 3]:
                yield i

        def add_one(x: int) -> int:
            return x + 1

        def multiply_by_three(x: int) -> int:
            return x * 3

        flow = Flow(source_fn, name="source")
        chained_flow = flow.map(add_one).map(multiply_by_three)

        async def empty_stream() -> AsyncIterator[None]:
            return
            yield  # pragma: no cover

        result = chained_flow(empty_stream())
        items = [item async for item in result]

        assert items == [6, 9, 12]  # (1+1)*3, (2+1)*3, (3+1)*3


class TestFlowFilter:
    """Tests for Flow.filter method."""

    @pytest.mark.asyncio
    async def test_filter_removes_items_not_matching_predicate(self) -> None:
        """Test that filter removes items that don't match the predicate."""

        async def source_fn(stream: AsyncIterator[None]) -> AsyncIterator[int]:
            for i in [1, 2, 3, 4, 5, 6]:
                yield i

        def is_even(x: int) -> bool:
            return x % 2 == 0

        flow = Flow(source_fn, name="source")
        filtered_flow = flow.filter(is_even)

        async def empty_stream() -> AsyncIterator[None]:
            return
            yield  # pragma: no cover

        result = filtered_flow(empty_stream())
        items = [item async for item in result]

        assert items == [2, 4, 6]

    @pytest.mark.asyncio
    async def test_filter_preserves_output_type(self) -> None:
        """Test that filter preserves the output type of the flow."""

        async def string_source(stream: AsyncIterator[None]) -> AsyncIterator[str]:
            for s in ["apple", "banana", "cherry", "date"]:
                yield s

        def starts_with_a_or_c(s: str) -> bool:
            return s.startswith("a") or s.startswith("c")

        flow = Flow(string_source, name="strings")
        filtered_flow = flow.filter(starts_with_a_or_c)

        async def empty_stream() -> AsyncIterator[None]:
            return
            yield  # pragma: no cover

        result = filtered_flow(empty_stream())
        items = [item async for item in result]

        assert items == ["apple", "cherry"]

    @pytest.mark.asyncio
    async def test_filter_preserves_input_type(self) -> None:
        """Test that filter preserves the input type of the original flow."""

        async def transform_fn(stream: AsyncIterator[str]) -> AsyncIterator[int]:
            async for item in stream:
                yield len(item)

        def is_short(length: int) -> bool:
            return length <= 3

        flow = Flow(transform_fn, name="length_transform")
        filtered_flow = flow.filter(is_short)

        async def string_stream() -> AsyncIterator[str]:
            for s in ["hi", "test", "a", "hello", "ok"]:
                yield s

        result = filtered_flow(string_stream())
        items = [item async for item in result]

        assert items == [2, 1, 2]  # len("hi"), len("a"), len("ok")

    def test_filter_creates_new_flow_with_descriptive_name(self) -> None:
        """Test that filter creates a new flow with a descriptive name."""

        async def test_fn(stream: AsyncIterator[int]) -> AsyncIterator[int]:
            async for item in stream:
                yield item * 2

        def greater_than_five(x: int) -> bool:
            return x > 5

        flow = Flow(test_fn, name="doubler")
        filtered_flow = flow.filter(greater_than_five)

        assert filtered_flow.name == "doubler.filter(greater_than_five)"
        assert filtered_flow is not flow  # Should be a new flow instance

    @pytest.mark.asyncio
    async def test_filter_with_empty_stream(self) -> None:
        """Test that filter works correctly with empty streams."""

        async def empty_source(stream: AsyncIterator[None]) -> AsyncIterator[int]:
            return
            yield  # pragma: no cover

        def always_true(x: int) -> bool:
            return True

        flow = Flow(empty_source, name="empty")
        filtered_flow = flow.filter(always_true)

        async def empty_stream() -> AsyncIterator[None]:
            return
            yield  # pragma: no cover

        result = filtered_flow(empty_stream())
        items = [item async for item in result]

        assert items == []

    @pytest.mark.asyncio
    async def test_filter_with_no_matches(self) -> None:
        """Test that filter returns empty stream when no items match."""

        async def source_fn(stream: AsyncIterator[None]) -> AsyncIterator[int]:
            for i in [1, 3, 5, 7, 9]:
                yield i

        def is_even(x: int) -> bool:
            return x % 2 == 0

        flow = Flow(source_fn, name="odds")
        filtered_flow = flow.filter(is_even)

        async def empty_stream() -> AsyncIterator[None]:
            return
            yield  # pragma: no cover

        result = filtered_flow(empty_stream())
        items = [item async for item in result]

        assert items == []

    @pytest.mark.asyncio
    async def test_filter_chaining_with_map(self) -> None:
        """Test that filter can be chained with map operations."""

        async def source_fn(stream: AsyncIterator[None]) -> AsyncIterator[int]:
            for i in [1, 2, 3, 4, 5]:
                yield i

        def is_odd(x: int) -> bool:
            return x % 2 == 1

        def square(x: int) -> int:
            return x * x

        flow = Flow(source_fn, name="source")
        chained_flow = flow.filter(is_odd).map(square)

        async def empty_stream() -> AsyncIterator[None]:
            return
            yield  # pragma: no cover

        result = chained_flow(empty_stream())
        items = [item async for item in result]

        assert items == [1, 9, 25]  # 1^2, 3^2, 5^2
