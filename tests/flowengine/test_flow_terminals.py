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
