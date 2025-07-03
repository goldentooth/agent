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
