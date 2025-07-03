from __future__ import annotations

from typing import Any, AsyncGenerator

import pytest

from flowengine.flow import Flow


def get_mock_flow(overrides: dict[str, Any] | None = None) -> Flow[int, str]:
    """Factory for creating test flows."""
    base_metadata = {"test": True}

    async def default_fn(
        stream: AsyncGenerator[int, None]
    ) -> AsyncGenerator[str, None]:
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

        async def test_fn(
            stream: AsyncGenerator[int, None]
        ) -> AsyncGenerator[str, None]:
            async for item in stream:
                yield str(item)

        flow = Flow(test_fn)

        assert flow.fn is test_fn
        assert flow.name == "<anonymous>"
        assert flow.metadata == {}
        assert flow.__name__ == "<anonymous>"

    def test_init_with_name(self) -> None:
        """Test Flow initialization with a name."""

        async def test_fn(
            stream: AsyncGenerator[int, None]
        ) -> AsyncGenerator[str, None]:
            async for item in stream:
                yield str(item)

        flow = Flow(test_fn, name="my_flow")

        assert flow.fn is test_fn
        assert flow.name == "my_flow"
        assert flow.metadata == {}
        assert flow.__name__ == "my_flow"

    def test_init_with_metadata(self) -> None:
        """Test Flow initialization with metadata."""

        async def test_fn(
            stream: AsyncGenerator[int, None]
        ) -> AsyncGenerator[str, None]:
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

        async def test_fn(
            stream: AsyncGenerator[int, None]
        ) -> AsyncGenerator[str, None]:
            async for item in stream:
                yield str(item)

        flow = Flow(test_fn, metadata=None)

        assert flow.fn is test_fn
        assert flow.name == "<anonymous>"
        assert flow.metadata == {}
        assert flow.__name__ == "<anonymous>"

    def test_init_with_all_parameters(self) -> None:
        """Test Flow initialization with all parameters."""

        async def test_fn(
            stream: AsyncGenerator[int, None]
        ) -> AsyncGenerator[str, None]:
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

        async def test_fn(
            stream: AsyncGenerator[int, None]
        ) -> AsyncGenerator[str, None]:
            async for item in stream:
                yield str(item)

        flow = Flow(test_fn)

        async def test_stream() -> AsyncGenerator[int, None]:
            for i in [1, 2, 3]:
                yield i

        result = flow(test_stream())

        # Should return an async iterator
        assert hasattr(result, "__aiter__")
        assert hasattr(result, "__anext__")

    @pytest.mark.asyncio
    async def test_call_processes_stream(self) -> None:
        """Test that calling a flow processes the input stream correctly."""

        async def double_fn(
            stream: AsyncGenerator[int, None]
        ) -> AsyncGenerator[int, None]:
            async for item in stream:
                yield item * 2

        flow = Flow(double_fn)

        async def test_stream() -> AsyncGenerator[int, None]:
            for i in [1, 2, 3]:
                yield i

        result = flow(test_stream())
        items = [item async for item in result]

        assert items == [2, 4, 6]

    @pytest.mark.asyncio
    async def test_call_empty_stream(self) -> None:
        """Test that calling a flow with empty stream works correctly."""

        async def test_fn(
            stream: AsyncGenerator[int, None]
        ) -> AsyncGenerator[str, None]:
            async for item in stream:
                yield str(item)

        flow = Flow(test_fn)

        async def empty_stream() -> AsyncGenerator[int, None]:
            return
            yield  # pragma: no cover

        result = flow(empty_stream())
        items = [item async for item in result]

        assert items == []

    @pytest.mark.asyncio
    async def test_call_delegates_to_fn(self) -> None:
        """Test that __call__ properly delegates to the internal function."""

        async def transform_fn(
            stream: AsyncGenerator[int, None]
        ) -> AsyncGenerator[str, None]:
            async for item in stream:
                yield f"item_{item}"

        flow = Flow(transform_fn)

        async def test_stream() -> AsyncGenerator[int, None]:
            for i in [10, 20]:
                yield i

        result = flow(test_stream())
        items = [item async for item in result]

        assert items == ["item_10", "item_20"]


class TestFlowRepr:
    """Tests for Flow.__repr__ method."""

    def test_repr_with_anonymous_flow(self) -> None:
        """Test __repr__ with default anonymous flow name."""

        async def test_fn(
            stream: AsyncGenerator[int, None]
        ) -> AsyncGenerator[str, None]:
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

        async def transform_data(
            stream: AsyncGenerator[int, None]
        ) -> AsyncGenerator[str, None]:
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

        async def process_fn(
            stream: AsyncGenerator[int, None]
        ) -> AsyncGenerator[str, None]:
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

        async def example_fn(
            stream: AsyncGenerator[int, None]
        ) -> AsyncGenerator[str, None]:
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

        async def test_fn(
            stream: AsyncGenerator[int, None]
        ) -> AsyncGenerator[str, None]:
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

        async def transform_fn(
            stream: AsyncGenerator[int, None]
        ) -> AsyncGenerator[str, None]:
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

        async def simple_fn(
            stream: AsyncGenerator[int, None]
        ) -> AsyncGenerator[int, None]:
            async for item in stream:
                yield item * 2

        flow = Flow(simple_fn)

        # This should raise TypeError when trying to use flow directly
        with pytest.raises(TypeError):
            # This would attempt to call __aiter__(flow) internally
            # We have to trigger it with aiter() since async comprehension
            # syntax checking happens at compile time
            # The following is an acceptable use of an ignore comment - Nate
            async for item in flow:  # type: ignore[attr-defined]
                pass


class TestFlowRshift:
    """Tests for Flow.__rshift__ method (pipe operator)."""

    @pytest.mark.asyncio
    async def test_rshift_pipes_flow_output_to_another_flow(self) -> None:
        """Test that >> operator pipes output from one flow to another."""

        async def double_fn(
            stream: AsyncGenerator[int, None]
        ) -> AsyncGenerator[int, None]:
            async for item in stream:
                yield item * 2

        async def add_ten_fn(
            stream: AsyncGenerator[int, None]
        ) -> AsyncGenerator[int, None]:
            async for item in stream:
                yield item + 10

        flow1 = Flow(double_fn, name="double")
        flow2 = Flow(add_ten_fn, name="add_ten")
        piped_flow = flow1 >> flow2

        async def int_stream() -> AsyncGenerator[int, None]:
            for i in [1, 2, 3]:
                yield i

        result = piped_flow(int_stream())
        items = [item async for item in result]

        assert items == [12, 14, 16]  # (1*2)+10, (2*2)+10, (3*2)+10

    @pytest.mark.asyncio
    async def test_rshift_preserves_original_flows(self) -> None:
        """Test that >> operator doesn't modify original flows."""

        async def identity_fn(
            stream: AsyncGenerator[str, None]
        ) -> AsyncGenerator[str, None]:
            async for item in stream:
                yield item

        async def upper_fn(
            stream: AsyncGenerator[str, None]
        ) -> AsyncGenerator[str, None]:
            async for item in stream:
                yield item.upper()

        flow1 = Flow(identity_fn, name="identity")
        flow2 = Flow(upper_fn, name="upper")
        piped_flow = flow1 >> flow2

        # Original flows should be unmodified
        assert flow1.name == "identity"
        assert flow2.name == "upper"
        assert flow1 is not piped_flow
        assert flow2 is not piped_flow

    def test_rshift_creates_descriptive_name(self) -> None:
        """Test that >> operator creates flow with descriptive name."""

        async def fn1(stream: AsyncGenerator[int, None]) -> AsyncGenerator[str, None]:
            async for item in stream:
                yield str(item)

        async def fn2(stream: AsyncGenerator[str, None]) -> AsyncGenerator[int, None]:
            async for item in stream:
                yield len(item)

        flow1 = Flow(fn1, name="stringify")
        flow2 = Flow(fn2, name="length")
        piped_flow = flow1 >> flow2

        assert piped_flow.name == "stringify >> length"

    @pytest.mark.asyncio
    async def test_rshift_with_type_transformation(self) -> None:
        """Test that >> operator works with flows that transform types."""

        async def int_to_str(
            stream: AsyncGenerator[int, None]
        ) -> AsyncGenerator[str, None]:
            async for item in stream:
                yield f"num_{item}"

        async def str_to_len(
            stream: AsyncGenerator[str, None]
        ) -> AsyncGenerator[int, None]:
            async for item in stream:
                yield len(item)

        flow1 = Flow(int_to_str, name="to_string")
        flow2 = Flow(str_to_len, name="to_length")
        piped_flow = flow1 >> flow2

        async def int_stream() -> AsyncGenerator[int, None]:
            for i in [1, 10, 100]:
                yield i

        result = piped_flow(int_stream())
        items = [item async for item in result]

        assert items == [5, 6, 7]  # len("num_1"), len("num_10"), len("num_100")

    @pytest.mark.asyncio
    async def test_rshift_chaining_multiple_flows(self) -> None:
        """Test chaining multiple flows with >> operator."""

        async def add_one(
            stream: AsyncGenerator[int, None]
        ) -> AsyncGenerator[int, None]:
            async for item in stream:
                yield item + 1

        async def double(
            stream: AsyncGenerator[int, None]
        ) -> AsyncGenerator[int, None]:
            async for item in stream:
                yield item * 2

        async def subtract_five(
            stream: AsyncGenerator[int, None]
        ) -> AsyncGenerator[int, None]:
            async for item in stream:
                yield item - 5

        flow1 = Flow(add_one, name="add_one")
        flow2 = Flow(double, name="double")
        flow3 = Flow(subtract_five, name="subtract_five")

        chained = flow1 >> flow2 >> flow3

        async def int_stream() -> AsyncGenerator[int, None]:
            for i in [5, 10]:
                yield i

        result = chained(int_stream())
        items = [item async for item in result]

        assert items == [7, 17]  # ((5+1)*2)-5, ((10+1)*2)-5

    @pytest.mark.asyncio
    async def test_rshift_with_empty_stream(self) -> None:
        """Test that >> operator works correctly with empty streams."""

        async def passthrough(
            stream: AsyncGenerator[int, None]
        ) -> AsyncGenerator[int, None]:
            async for item in stream:
                yield item

        flow1 = Flow(passthrough, name="pass1")
        flow2 = Flow(passthrough, name="pass2")
        piped = flow1 >> flow2

        async def empty_stream() -> AsyncGenerator[int, None]:
            return
            yield  # pragma: no cover

        result = piped(empty_stream())
        items = [item async for item in result]

        assert items == []


class TestFlowLabel:
    """Tests for Flow.label method."""

    @pytest.mark.asyncio
    async def test_label_prints_debug_info(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Test that label prints debug information."""

        async def source_fn(
            stream: AsyncGenerator[None, None]
        ) -> AsyncGenerator[str, None]:
            for s in ["hello", "world"]:
                yield s

        flow = Flow(source_fn, name="source")
        labeled_flow = flow.label("debug")

        async def empty_stream() -> AsyncGenerator[None, None]:
            return
            yield  # pragma: no cover

        result = labeled_flow(empty_stream())
        items = [item async for item in result]

        # Check output
        captured = capsys.readouterr()
        assert "[Flow:debug] starting" in captured.out
        assert "[Flow:debug] yield: hello" in captured.out
        assert "[Flow:debug] yield: world" in captured.out

        # Check items are unchanged
        assert items == ["hello", "world"]

    def test_label_creates_new_flow_with_descriptive_name(self) -> None:
        """Test that label creates a new flow with descriptive name."""

        async def test_fn(
            stream: AsyncGenerator[int, None]
        ) -> AsyncGenerator[int, None]:
            async for item in stream:
                yield item * 2

        flow = Flow(test_fn, name="double")
        labeled_flow = flow.label("my_label")

        assert labeled_flow.name == "double.label(my_label)"
        assert labeled_flow is not flow

    @pytest.mark.asyncio
    async def test_label_with_empty_stream(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Test that label works correctly with empty streams."""

        async def empty_source(
            stream: AsyncGenerator[None, None]
        ) -> AsyncGenerator[int, None]:
            return
            yield  # pragma: no cover

        flow = Flow(empty_source, name="empty")
        labeled_flow = flow.label("empty_test")

        async def empty_stream() -> AsyncGenerator[None, None]:
            return
            yield  # pragma: no cover

        result = labeled_flow(empty_stream())
        items = [item async for item in result]

        # Check output
        captured = capsys.readouterr()
        assert "[Flow:empty_test] starting" in captured.out
        # Should not have any yield messages
        assert "[Flow:empty_test] yield:" not in captured.out

        assert items == []

    @pytest.mark.asyncio
    async def test_label_preserves_type_signature(self) -> None:
        """Test that label preserves the flow's type signature."""

        async def typed_fn(
            stream: AsyncGenerator[str, None]
        ) -> AsyncGenerator[int, None]:
            async for item in stream:
                yield len(item)

        flow = Flow(typed_fn, name="length")
        labeled_flow = flow.label("type_test")

        async def string_stream() -> AsyncGenerator[str, None]:
            for s in ["a", "bb", "ccc"]:
                yield s

        result = labeled_flow(string_stream())
        items = [item async for item in result]

        assert items == [1, 2, 3]

    @pytest.mark.asyncio
    async def test_label_chaining_with_other_operations(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Test that label can be chained with other flow operations."""

        async def source_fn(
            stream: AsyncGenerator[None, None]
        ) -> AsyncGenerator[int, None]:
            for i in [1, 2, 3, 4, 5]:
                yield i

        def is_even(x: int) -> bool:
            return x % 2 == 0

        def square(x: int) -> int:
            return x * x

        flow = Flow(source_fn, name="source")
        processed_flow = flow.filter(is_even).label("even_numbers").map(square)

        async def empty_stream() -> AsyncGenerator[None, None]:
            return
            yield  # pragma: no cover

        result = processed_flow(empty_stream())
        items = [item async for item in result]

        # Check output
        captured = capsys.readouterr()
        assert "[Flow:even_numbers] starting" in captured.out
        assert "[Flow:even_numbers] yield: 2" in captured.out
        assert "[Flow:even_numbers] yield: 4" in captured.out

        # Check final result
        assert items == [4, 16]  # 2^2, 4^2

    @pytest.mark.asyncio
    async def test_multiple_labels_in_chain(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Test multiple labels in a flow chain."""

        async def source_fn(
            stream: AsyncGenerator[None, None]
        ) -> AsyncGenerator[int, None]:
            for i in [1, 2]:
                yield i

        def double(x: int) -> int:
            return x * 2

        flow = Flow(source_fn, name="source")
        labeled_flow = flow.label("input").map(double).label("output")

        async def empty_stream() -> AsyncGenerator[None, None]:
            return
            yield  # pragma: no cover

        result = labeled_flow(empty_stream())
        items = [item async for item in result]

        # Check output
        captured = capsys.readouterr()
        assert "[Flow:input] starting" in captured.out
        assert "[Flow:input] yield: 1" in captured.out
        assert "[Flow:input] yield: 2" in captured.out
        assert "[Flow:output] starting" in captured.out
        assert "[Flow:output] yield: 2" in captured.out
        assert "[Flow:output] yield: 4" in captured.out

        assert items == [2, 4]
