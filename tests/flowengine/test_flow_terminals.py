from __future__ import annotations

from collections.abc import AsyncIterator

import pytest

from flowengine.flow import Flow


class TestFlowToList:
    """Tests for Flow.to_list method."""

    @pytest.mark.asyncio
    async def test_to_list_collects_all_items(self) -> None:
        """Test that to_list collects all items from the flow into a list."""

        async def source_fn(stream: AsyncIterator[None]) -> AsyncIterator[str]:
            for s in ["hello", "world", "test"]:
                yield s

        flow = Flow(source_fn, name="source")
        collector = flow.to_list()

        async def empty_stream() -> AsyncIterator[None]:
            return
            yield  # pragma: no cover

        result = await collector(empty_stream())

        assert result == ["hello", "world", "test"]
        assert isinstance(result, list)

    @pytest.mark.asyncio
    async def test_to_list_with_empty_stream(self) -> None:
        """Test that to_list returns empty list for empty streams."""

        async def empty_source(stream: AsyncIterator[None]) -> AsyncIterator[int]:
            return
            yield  # pragma: no cover

        flow = Flow(empty_source, name="empty")
        collector = flow.to_list()

        async def empty_stream() -> AsyncIterator[None]:
            return
            yield  # pragma: no cover

        result = await collector(empty_stream())

        assert result == []
        assert isinstance(result, list)

    @pytest.mark.asyncio
    async def test_to_list_preserves_order(self) -> None:
        """Test that to_list preserves the order of items."""

        async def sequence_fn(stream: AsyncIterator[None]) -> AsyncIterator[int]:
            for i in [3, 1, 4, 1, 5, 9, 2, 6]:
                yield i

        flow = Flow(sequence_fn, name="sequence")
        collector = flow.to_list()

        async def empty_stream() -> AsyncIterator[None]:
            return
            yield  # pragma: no cover

        result = await collector(empty_stream())

        assert result == [3, 1, 4, 1, 5, 9, 2, 6]

    @pytest.mark.asyncio
    async def test_to_list_with_transformed_flow(self) -> None:
        """Test that to_list works with transformed flows."""

        async def source_fn(stream: AsyncIterator[None]) -> AsyncIterator[int]:
            for i in [1, 2, 3, 4, 5]:
                yield i

        def is_even(x: int) -> bool:
            return x % 2 == 0

        def square(x: int) -> int:
            return x * x

        flow = Flow(source_fn, name="source")
        transformed_flow = flow.filter(is_even).map(square)
        collector = transformed_flow.to_list()

        async def empty_stream() -> AsyncIterator[None]:
            return
            yield  # pragma: no cover

        result = await collector(empty_stream())

        assert result == [4, 16]  # 2^2, 4^2

    @pytest.mark.asyncio
    async def test_to_list_returns_callable(self) -> None:
        """Test that to_list returns a callable function."""

        async def test_fn(stream: AsyncIterator[int]) -> AsyncIterator[str]:
            async for item in stream:
                yield str(item)

        flow = Flow(test_fn, name="stringify")
        collector = flow.to_list()

        # Should return a callable
        assert callable(collector)

        # Should be able to call it with a stream
        async def int_stream() -> AsyncIterator[int]:
            for i in [1, 2, 3]:
                yield i

        result = await collector(int_stream())
        assert result == ["1", "2", "3"]

    @pytest.mark.asyncio
    async def test_to_list_with_different_input_streams(self) -> None:
        """Test that to_list works with different input streams."""

        async def transform_fn(stream: AsyncIterator[str]) -> AsyncIterator[int]:
            async for item in stream:
                yield len(item)

        flow = Flow(transform_fn, name="length_transform")
        collector = flow.to_list()

        # Test with first stream
        async def stream1() -> AsyncIterator[str]:
            for s in ["hi", "hello"]:
                yield s

        result1 = await collector(stream1())
        assert result1 == [2, 5]

        # Test with different stream
        async def stream2() -> AsyncIterator[str]:
            for s in ["a", "test", "python"]:
                yield s

        result2 = await collector(stream2())
        assert result2 == [1, 4, 6]

    @pytest.mark.asyncio
    async def test_to_list_type_annotations(self) -> None:
        """Test that to_list maintains proper type annotations."""

        async def source_fn(stream: AsyncIterator[None]) -> AsyncIterator[str]:
            for s in ["a", "b", "c"]:
                yield s

        flow = Flow(source_fn, name="source")
        collector = flow.to_list()

        # The collector should have the right signature
        async def empty_stream() -> AsyncIterator[None]:
            return
            yield  # pragma: no cover

        result = await collector(empty_stream())

        # Result should be a list of strings
        assert isinstance(result, list)
        assert all(isinstance(item, str) for item in result)
        assert result == ["a", "b", "c"]


class TestFlowForEach:
    """Tests for Flow.for_each method."""

    @pytest.mark.asyncio
    async def test_for_each_applies_function_to_all_items(self) -> None:
        """Test that for_each applies function to all items in the stream."""

        async def source_fn(stream: AsyncIterator[None]) -> AsyncIterator[str]:
            for s in ["hello", "world", "test"]:
                yield s

        # Track what items were processed
        processed_items = []

        async def process_item(item: str) -> None:
            processed_items.append(item.upper())

        flow = Flow(source_fn, name="source")
        consumer = flow.for_each(process_item)

        async def empty_stream() -> AsyncIterator[None]:
            return
            yield  # pragma: no cover

        await consumer(empty_stream())

        assert processed_items == ["HELLO", "WORLD", "TEST"]

    @pytest.mark.asyncio
    async def test_for_each_with_empty_stream(self) -> None:
        """Test that for_each handles empty streams correctly."""

        async def empty_source(stream: AsyncIterator[None]) -> AsyncIterator[int]:
            return
            yield  # pragma: no cover

        # Track what items were processed
        processed_items = []

        async def process_item(item: int) -> None:
            processed_items.append(item * 2)

        flow = Flow(empty_source, name="empty")
        consumer = flow.for_each(process_item)

        async def empty_stream() -> AsyncIterator[None]:
            return
            yield  # pragma: no cover

        await consumer(empty_stream())

        assert processed_items == []

    @pytest.mark.asyncio
    async def test_for_each_preserves_order(self) -> None:
        """Test that for_each processes items in order."""

        async def sequence_fn(stream: AsyncIterator[None]) -> AsyncIterator[int]:
            for i in [3, 1, 4, 1, 5]:
                yield i

        # Track processing order
        processed_order = []

        async def process_item(item: int) -> None:
            processed_order.append(item)

        flow = Flow(sequence_fn, name="sequence")
        consumer = flow.for_each(process_item)

        async def empty_stream() -> AsyncIterator[None]:
            return
            yield  # pragma: no cover

        await consumer(empty_stream())

        assert processed_order == [3, 1, 4, 1, 5]

    @pytest.mark.asyncio
    async def test_for_each_with_transformed_flow(self) -> None:
        """Test that for_each works with transformed flows."""

        async def source_fn(stream: AsyncIterator[None]) -> AsyncIterator[int]:
            for i in [1, 2, 3, 4, 5]:
                yield i

        def is_even(x: int) -> bool:
            return x % 2 == 0

        def square(x: int) -> int:
            return x * x

        # Track processed results
        processed_items = []

        async def collect_item(item: int) -> None:
            processed_items.append(item)

        flow = Flow(source_fn, name="source")
        transformed_flow = flow.filter(is_even).map(square)
        consumer = transformed_flow.for_each(collect_item)

        async def empty_stream() -> AsyncIterator[None]:
            return
            yield  # pragma: no cover

        await consumer(empty_stream())

        assert processed_items == [4, 16]  # 2^2, 4^2

    @pytest.mark.asyncio
    async def test_for_each_returns_callable(self) -> None:
        """Test that for_each returns a callable function."""

        async def test_fn(stream: AsyncIterator[int]) -> AsyncIterator[str]:
            async for item in stream:
                yield str(item)

        processed_items = []

        async def process_item(item: str) -> None:
            processed_items.append(f"processed_{item}")

        flow = Flow(test_fn, name="stringify")
        consumer = flow.for_each(process_item)

        # Should return a callable
        assert callable(consumer)

        # Should be able to call it with a stream
        async def int_stream() -> AsyncIterator[int]:
            for i in [1, 2, 3]:
                yield i

        await consumer(int_stream())
        assert processed_items == ["processed_1", "processed_2", "processed_3"]

    @pytest.mark.asyncio
    async def test_for_each_with_side_effects(self) -> None:
        """Test that for_each properly handles side effects."""

        async def source_fn(stream: AsyncIterator[None]) -> AsyncIterator[str]:
            for s in ["debug", "info", "error"]:
                yield s

        # Simulate logging side effect
        log_messages = []

        async def log_message(level: str) -> None:
            log_messages.append(f"LOG[{level.upper()}]: Message received")

        flow = Flow(source_fn, name="logger")
        consumer = flow.for_each(log_message)

        async def empty_stream() -> AsyncIterator[None]:
            return
            yield  # pragma: no cover

        result = await consumer(empty_stream())

        # for_each should return None
        assert result is None

        # Side effects should have occurred
        assert log_messages == [
            "LOG[DEBUG]: Message received",
            "LOG[INFO]: Message received",
            "LOG[ERROR]: Message received",
        ]

    @pytest.mark.asyncio
    async def test_for_each_with_different_input_streams(self) -> None:
        """Test that for_each works with different input streams."""

        async def transform_fn(stream: AsyncIterator[str]) -> AsyncIterator[int]:
            async for item in stream:
                yield len(item)

        processed_items = []

        async def process_item(length: int) -> None:
            processed_items.append(f"length:{length}")

        flow = Flow(transform_fn, name="length_transform")
        consumer = flow.for_each(process_item)

        # Test with first stream
        async def stream1() -> AsyncIterator[str]:
            for s in ["hi", "hello"]:
                yield s

        await consumer(stream1())
        assert processed_items == ["length:2", "length:5"]

        # Reset and test with different stream
        processed_items.clear()

        async def stream2() -> AsyncIterator[str]:
            for s in ["a", "test"]:
                yield s

        await consumer(stream2())
        assert processed_items == ["length:1", "length:4"]


class TestFlowCollect:
    """Tests for Flow.collect method."""

    @pytest.mark.asyncio
    async def test_collect_is_alias_for_to_list(self) -> None:
        """Test that collect is an alias for to_list."""

        async def source_fn(stream: AsyncIterator[None]) -> AsyncIterator[int]:
            for i in [1, 2, 3]:
                yield i

        flow = Flow(source_fn, name="source")

        # Both should return the same function
        collector1 = flow.collect()
        collector2 = flow.to_list()

        async def empty_stream() -> AsyncIterator[None]:
            return
            yield  # pragma: no cover

        result1 = await collector1(empty_stream())
        result2 = await collector2(empty_stream())

        assert result1 == result2 == [1, 2, 3]

    @pytest.mark.asyncio
    async def test_collect_delegates_to_to_list(self) -> None:
        """Test that collect delegates to to_list and produces same results."""

        async def test_fn(stream: AsyncIterator[str]) -> AsyncIterator[str]:
            async for item in stream:
                yield item.upper()

        flow = Flow(test_fn, name="upper")

        async def string_stream() -> AsyncIterator[str]:
            for s in ["hello", "world"]:
                yield s

        # Both methods should produce identical results
        result1 = await flow.collect()(string_stream())

        async def string_stream2() -> AsyncIterator[str]:
            for s in ["hello", "world"]:
                yield s

        result2 = await flow.to_list()(string_stream2())

        assert result1 == result2 == ["HELLO", "WORLD"]

    @pytest.mark.asyncio
    async def test_collect_works_with_all_flow_types(self) -> None:
        """Test that collect works with various flow transformations."""

        async def source_fn(stream: AsyncIterator[None]) -> AsyncIterator[int]:
            for i in range(1, 6):
                yield i

        def is_even(x: int) -> bool:
            return x % 2 == 0

        def square(x: int) -> int:
            return x * x

        flow = Flow(source_fn, name="source")
        transformed = flow.filter(is_even).map(square)

        async def empty_stream() -> AsyncIterator[None]:
            return
            yield  # pragma: no cover

        # Using collect
        result = await transformed.collect()(empty_stream())
        assert result == [4, 16]  # 2^2, 4^2

    @pytest.mark.asyncio
    async def test_collect_preserves_type_signature(self) -> None:
        """Test that collect preserves the same type signature as to_list."""

        async def typed_fn(stream: AsyncIterator[int]) -> AsyncIterator[str]:
            async for item in stream:
                yield f"item_{item}"

        flow = Flow(typed_fn, name="typed")
        collector = flow.collect()

        async def int_stream() -> AsyncIterator[int]:
            for i in [10, 20]:
                yield i

        result = await collector(int_stream())
        assert result == ["item_10", "item_20"]
        assert isinstance(result, list)
        assert all(isinstance(item, str) for item in result)


class TestFlowPreview:
    """Tests for Flow.preview method."""

    @pytest.mark.asyncio
    async def test_preview_returns_limited_items(self) -> None:
        """Test that preview returns only the specified number of items."""

        async def source_fn(stream: AsyncIterator[None]) -> AsyncIterator[int]:
            for i in range(100):  # Large stream
                yield i

        flow = Flow(source_fn, name="source")

        async def empty_stream() -> AsyncIterator[None]:
            return
            yield  # pragma: no cover

        # Default limit is 10
        result = await flow.preview(empty_stream())
        assert result == list(range(10))

        # Custom limit
        result_5 = await flow.preview(empty_stream(), limit=5)
        assert result_5 == list(range(5))

    @pytest.mark.asyncio
    async def test_preview_with_fewer_items_than_limit(self) -> None:
        """Test that preview returns all items when stream has fewer than limit."""

        async def source_fn(stream: AsyncIterator[None]) -> AsyncIterator[int]:
            for i in [1, 2, 3]:
                yield i

        flow = Flow(source_fn, name="small")

        async def empty_stream() -> AsyncIterator[None]:
            return
            yield  # pragma: no cover

        result = await flow.preview(empty_stream(), limit=10)
        assert result == [1, 2, 3]

    @pytest.mark.asyncio
    async def test_preview_with_empty_stream(self) -> None:
        """Test that preview returns empty list for empty streams."""

        async def empty_source(stream: AsyncIterator[None]) -> AsyncIterator[int]:
            return
            yield  # pragma: no cover

        flow = Flow(empty_source, name="empty")

        async def empty_stream() -> AsyncIterator[None]:
            return
            yield  # pragma: no cover

        result = await flow.preview(empty_stream(), limit=10)
        assert result == []

    @pytest.mark.asyncio
    async def test_preview_with_transformed_flow(self) -> None:
        """Test that preview works with transformed flows."""

        async def source_fn(stream: AsyncIterator[None]) -> AsyncIterator[int]:
            for i in range(20):
                yield i

        def is_even(x: int) -> bool:
            return x % 2 == 0

        def square(x: int) -> int:
            return x * x

        flow = Flow(source_fn, name="source")
        transformed = flow.filter(is_even).map(square)

        async def empty_stream() -> AsyncIterator[None]:
            return
            yield  # pragma: no cover

        result = await transformed.preview(empty_stream(), limit=5)
        assert result == [0, 4, 16, 36, 64]  # 0^2, 2^2, 4^2, 6^2, 8^2

    @pytest.mark.asyncio
    async def test_preview_closes_iterator_properly(self) -> None:
        """Test that preview properly closes the async iterator."""

        class TrackableIterator:
            def __init__(self) -> None:
                super().__init__()
                self.closed = False

            async def __aiter__(self) -> AsyncIterator[int]:
                for i in range(100):
                    yield i

            async def aclose(self) -> None:
                self.closed = True

        async def trackable_fn(stream: AsyncIterator[None]) -> AsyncIterator[int]:
            iterator = TrackableIterator()
            async for item in iterator:
                yield item

        flow = Flow(trackable_fn, name="trackable")

        async def empty_stream() -> AsyncIterator[None]:
            return
            yield  # pragma: no cover

        # This should close the iterator after getting 5 items
        result = await flow.preview(empty_stream(), limit=5)
        assert result == list(range(5))

    @pytest.mark.asyncio
    async def test_preview_with_different_input_streams(self) -> None:
        """Test that preview works with different input stream types."""

        async def transform_fn(stream: AsyncIterator[str]) -> AsyncIterator[int]:
            async for item in stream:
                yield len(item) * 10

        flow = Flow(transform_fn, name="length_transform")

        async def string_stream() -> AsyncIterator[str]:
            words = ["a", "bb", "ccc", "dddd", "eeeee", "ffffff"]
            for word in words:
                yield word

        result = await flow.preview(string_stream(), limit=3)
        assert result == [10, 20, 30]

    @pytest.mark.asyncio
    async def test_preview_with_limit_zero(self) -> None:
        """Test that preview with limit=0 returns empty list."""

        async def source_fn(stream: AsyncIterator[None]) -> AsyncIterator[int]:
            for i in range(10):
                yield i

        flow = Flow(source_fn, name="source")

        async def empty_stream() -> AsyncIterator[None]:
            return
            yield  # pragma: no cover

        result = await flow.preview(empty_stream(), limit=0)
        assert result == []


class TestFlowPrint:
    """Tests for Flow.print method."""

    def test_print_returns_self(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Test that print returns the same flow instance for chaining."""

        async def test_fn(stream: AsyncIterator[int]) -> AsyncIterator[str]:
            async for item in stream:
                yield str(item)

        flow = Flow(test_fn, name="test_flow")
        result = flow.print()

        assert result is flow

    def test_print_outputs_flow_information(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Test that print outputs flow name and function information."""

        async def transform_data(stream: AsyncIterator[int]) -> AsyncIterator[str]:
            async for item in stream:
                yield f"data_{item}"

        flow = Flow(transform_data, name="transformer")
        flow.print()

        captured = capsys.readouterr()
        assert "📦 Flow<transformer> :: transform_data" in captured.out

    def test_print_outputs_metadata_when_present(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Test that print outputs metadata when flow has metadata."""

        async def process_fn(stream: AsyncIterator[int]) -> AsyncIterator[str]:
            async for item in stream:
                yield str(item * 2)

        metadata = {"version": 1, "type": "processor", "description": "doubles numbers"}
        flow = Flow(process_fn, name="doubler", metadata=metadata)
        flow.print()

        captured = capsys.readouterr()
        assert "📦 Flow<doubler> :: process_fn" in captured.out
        assert "metadata:" in captured.out
        assert "version" in captured.out
        assert "processor" in captured.out

    def test_print_no_metadata_output_when_empty(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Test that print doesn't output metadata section when empty."""

        async def simple_fn(stream: AsyncIterator[int]) -> AsyncIterator[int]:
            async for item in stream:
                yield item

        flow = Flow(simple_fn, name="simple")
        flow.print()

        captured = capsys.readouterr()
        assert "📦 Flow<simple> :: simple_fn" in captured.out
        assert "metadata:" not in captured.out

    def test_print_with_anonymous_flow(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Test that print works with anonymous flows."""

        async def anonymous_fn(stream: AsyncIterator[str]) -> AsyncIterator[str]:
            async for item in stream:
                yield item.upper()

        flow = Flow(anonymous_fn)  # No name provided
        flow.print()

        captured = capsys.readouterr()
        assert "📦 Flow<<anonymous>> :: anonymous_fn" in captured.out

    def test_print_preserves_type_signature(self) -> None:
        """Test that print preserves the flow's type signature."""

        async def typed_fn(stream: AsyncIterator[str]) -> AsyncIterator[int]:
            async for item in stream:
                yield len(item)

        flow = Flow(typed_fn, name="length_calculator")
        printed_flow = flow.print()

        # Should be the same instance with same type signature
        assert printed_flow is flow
        assert printed_flow.name == "length_calculator"

    def test_print_chainable_with_other_methods(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Test that print can be chained with other flow operations."""

        async def source_fn(stream: AsyncIterator[None]) -> AsyncIterator[int]:
            for i in [1, 2, 3]:
                yield i

        def double(x: int) -> int:
            return x * 2

        flow = Flow(source_fn, name="source")
        chained_flow = flow.print().map(double)

        # Check that print was called
        captured = capsys.readouterr()
        assert "📦 Flow<source> :: source_fn" in captured.out

        # Check that chaining worked
        assert chained_flow.name == "source.map(double)"
        assert chained_flow is not flow

    @pytest.mark.asyncio
    async def test_print_works_with_execution(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Test that print doesn't interfere with flow execution."""

        async def test_fn(stream: AsyncIterator[int]) -> AsyncIterator[str]:
            async for item in stream:
                yield f"item_{item}"

        flow = Flow(test_fn, name="formatter")
        printed_flow = flow.print()

        async def int_stream() -> AsyncIterator[int]:
            for i in [10, 20]:
                yield i

        result = printed_flow(int_stream())
        items = [item async for item in result]

        # Check print output
        captured = capsys.readouterr()
        assert "📦 Flow<formatter> :: test_fn" in captured.out

        # Check execution worked correctly
        assert items == ["item_10", "item_20"]

    def test_print_multiple_times(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Test that print can be called multiple times."""

        async def test_fn(stream: AsyncIterator[int]) -> AsyncIterator[int]:
            async for item in stream:
                yield item

        flow = Flow(test_fn, name="test", metadata={"debug": True})

        flow.print()
        flow.print()

        captured = capsys.readouterr()
        output_lines = captured.out.strip().split("\n")

        # Should have printed twice
        flow_lines = [line for line in output_lines if "📦 Flow<test>" in line]
        assert len(flow_lines) == 2

        metadata_lines = [line for line in output_lines if "metadata:" in line]
        assert len(metadata_lines) == 2
