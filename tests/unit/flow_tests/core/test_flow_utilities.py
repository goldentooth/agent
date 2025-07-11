from typing import AsyncGenerator

import pytest

from flow.flow import Flow


class TestFlowPrint:
    """Tests for Flow.print method."""

    def test_print_returns_self(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Test that print returns the same flow instance for chaining."""

        async def test_fn(
            stream: AsyncGenerator[int, None],
        ) -> AsyncGenerator[str, None]:
            async for item in stream:
                yield str(item)

        flow = Flow(test_fn, name="test_flow")
        result = flow.print()

        assert result is flow

    def test_print_outputs_flow_information(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Test that print outputs flow name and function information."""

        async def transform_data(
            stream: AsyncGenerator[int, None],
        ) -> AsyncGenerator[str, None]:
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

        async def process_fn(
            stream: AsyncGenerator[int, None],
        ) -> AsyncGenerator[str, None]:
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

        async def simple_fn(
            stream: AsyncGenerator[int, None],
        ) -> AsyncGenerator[int, None]:
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

        async def anonymous_fn(
            stream: AsyncGenerator[str, None],
        ) -> AsyncGenerator[str, None]:
            async for item in stream:
                yield item.upper()

        flow = Flow(anonymous_fn)  # No name provided
        flow.print()

        captured = capsys.readouterr()
        assert "📦 Flow<<anonymous>> :: anonymous_fn" in captured.out

    def test_print_preserves_type_signature(self) -> None:
        """Test that print preserves the flow's type signature."""

        async def typed_fn(
            stream: AsyncGenerator[str, None],
        ) -> AsyncGenerator[int, None]:
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

        async def source_fn(
            stream: AsyncGenerator[None, None],
        ) -> AsyncGenerator[int, None]:
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

        async def test_fn(
            stream: AsyncGenerator[int, None],
        ) -> AsyncGenerator[str, None]:
            async for item in stream:
                yield f"item_{item}"

        flow = Flow(test_fn, name="formatter")
        printed_flow = flow.print()

        async def int_stream() -> AsyncGenerator[int, None]:
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

        async def test_fn(
            stream: AsyncGenerator[int, None],
        ) -> AsyncGenerator[int, None]:
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


class TestFlowWithFallback:
    """Tests for Flow.with_fallback method."""

    @pytest.mark.asyncio
    async def test_with_fallback_provides_default_for_empty_stream(self) -> None:
        """Test that with_fallback provides default value for empty streams."""

        async def empty_source(
            stream: AsyncGenerator[None, None],
        ) -> AsyncGenerator[int, None]:
            return
            yield  # pragma: no cover

        flow = Flow(empty_source, name="empty")
        fallback_flow = flow.with_fallback(42)

        async def empty_stream() -> AsyncGenerator[None, None]:
            return
            yield  # pragma: no cover

        result = fallback_flow(empty_stream())
        items = [item async for item in result]

        assert items == [42]

    @pytest.mark.asyncio
    async def test_with_fallback_ignored_when_stream_has_items(self) -> None:
        """Test that with_fallback is ignored when stream produces items."""

        async def source_fn(
            stream: AsyncGenerator[None, None],
        ) -> AsyncGenerator[str, None]:
            for s in ["hello", "world"]:
                yield s

        flow = Flow(source_fn, name="source")
        fallback_flow = flow.with_fallback("fallback")

        async def empty_stream() -> AsyncGenerator[None, None]:
            return
            yield  # pragma: no cover

        result = fallback_flow(empty_stream())
        items = [item async for item in result]

        assert items == ["hello", "world"]

    @pytest.mark.asyncio
    async def test_with_fallback_used_for_single_empty_yield(self) -> None:
        """Test that with_fallback is used when flow yields nothing."""

        async def conditional_source(
            stream: AsyncGenerator[bool, None],
        ) -> AsyncGenerator[str, None]:
            async for should_yield in stream:
                if should_yield:
                    yield "item"

        flow = Flow(conditional_source, name="conditional")
        fallback_flow = flow.with_fallback("default")

        async def false_stream() -> AsyncGenerator[bool, None]:
            yield False

        result = fallback_flow(false_stream())
        items = [item async for item in result]

        assert items == ["default"]

    @pytest.mark.asyncio
    async def test_with_fallback_different_types(self) -> None:
        """Test with_fallback with different value types."""

        # Test with number fallback
        async def empty_int_source(
            stream: AsyncGenerator[None, None],
        ) -> AsyncGenerator[int, None]:
            return
            yield  # pragma: no cover

        int_flow = Flow(empty_int_source, name="empty_int")
        int_fallback_flow = int_flow.with_fallback(999)

        async def empty_stream() -> AsyncGenerator[None, None]:
            return
            yield  # pragma: no cover

        result = int_fallback_flow(empty_stream())
        items = [item async for item in result]
        assert items == [999]

        # Test with list fallback
        async def empty_list_source(
            stream: AsyncGenerator[None, None],
        ) -> AsyncGenerator[list[str], None]:
            return
            yield  # pragma: no cover

        list_flow = Flow(empty_list_source, name="empty_list")
        list_fallback_flow = list_flow.with_fallback(["default", "items"])

        result2 = list_fallback_flow(empty_stream())
        items2 = [item async for item in result2]
        assert items2 == [["default", "items"]]

    def test_with_fallback_creates_new_flow_with_descriptive_name(self) -> None:
        """Test that with_fallback creates a new flow with descriptive name."""

        async def test_fn(
            stream: AsyncGenerator[int, None],
        ) -> AsyncGenerator[str, None]:
            async for item in stream:
                yield str(item)

        flow = Flow(test_fn, name="stringify")
        fallback_flow = flow.with_fallback("default")

        assert fallback_flow.name == "stringify.with_fallback(default)"
        assert fallback_flow is not flow

    @pytest.mark.asyncio
    async def test_with_fallback_preserves_type_signature(self) -> None:
        """Test that with_fallback preserves the flow's type signature."""

        async def typed_fn(
            stream: AsyncGenerator[str, None],
        ) -> AsyncGenerator[int, None]:
            async for item in stream:
                yield len(item)

        flow = Flow(typed_fn, name="length")
        fallback_flow = flow.with_fallback(0)

        async def empty_string_stream() -> AsyncGenerator[str, None]:
            return
            yield  # pragma: no cover

        result = fallback_flow(empty_string_stream())
        items = [item async for item in result]

        assert items == [0]
        assert all(isinstance(item, int) for item in items)

    @pytest.mark.asyncio
    async def test_with_fallback_chaining_with_other_operations(self) -> None:
        """Test that with_fallback can be chained with other flow operations."""

        async def source_fn(
            stream: AsyncGenerator[None, None],
        ) -> AsyncGenerator[int, None]:
            return
            yield  # pragma: no cover

        def double(x: int) -> int:
            return x * 2

        flow = Flow(source_fn, name="empty_source")
        chained_flow = flow.with_fallback(5).map(double)

        async def empty_stream() -> AsyncGenerator[None, None]:
            return
            yield  # pragma: no cover

        result = chained_flow(empty_stream())
        items = [item async for item in result]

        assert items == [10]  # 5 * 2

    @pytest.mark.asyncio
    async def test_with_fallback_multiple_fallbacks(self) -> None:
        """Test chaining multiple fallbacks (last one wins if empty)."""

        async def empty_source(
            stream: AsyncGenerator[None, None],
        ) -> AsyncGenerator[str, None]:
            return
            yield  # pragma: no cover

        flow = Flow(empty_source, name="empty")
        chained_flow = flow.with_fallback("first").with_fallback("second")

        async def empty_stream() -> AsyncGenerator[None, None]:
            return
            yield  # pragma: no cover

        result = chained_flow(empty_stream())
        items = [item async for item in result]

        # Should use the outer fallback since inner flow (with "first") produces one item
        assert items == ["first"]

    @pytest.mark.asyncio
    async def test_with_fallback_single_item_stream(self) -> None:
        """Test with_fallback when stream produces exactly one item."""

        async def single_source(
            stream: AsyncGenerator[None, None],
        ) -> AsyncGenerator[str, None]:
            yield "only_item"

        flow = Flow(single_source, name="single")
        fallback_flow = flow.with_fallback("fallback")

        async def empty_stream() -> AsyncGenerator[None, None]:
            return
            yield  # pragma: no cover

        result = fallback_flow(empty_stream())
        items = [item async for item in result]

        assert items == ["only_item"]

    @pytest.mark.asyncio
    async def test_with_fallback_with_different_input_streams(self) -> None:
        """Test with_fallback works with different input stream types."""

        async def filter_fn(
            stream: AsyncGenerator[int, None],
        ) -> AsyncGenerator[int, None]:
            async for item in stream:
                if item > 10:
                    yield item

        flow = Flow(filter_fn, name="filter_large")
        fallback_flow = flow.with_fallback(-1)

        # Stream with no items > 10
        async def small_numbers() -> AsyncGenerator[int, None]:
            for i in [1, 5, 8]:
                yield i

        result1 = fallback_flow(small_numbers())
        items1 = [item async for item in result1]
        assert items1 == [-1]

        # Stream with items > 10
        async def mixed_numbers() -> AsyncGenerator[int, None]:
            for i in [1, 15, 8, 20]:
                yield i

        result2 = fallback_flow(mixed_numbers())
        items2 = [item async for item in result2]
        assert items2 == [15, 20]


class TestFlowBatch:
    """Tests for Flow.batch method."""

    @pytest.mark.asyncio
    async def test_batch_groups_items_by_size(self) -> None:
        """Test that batch groups items into batches of specified size."""

        async def source_fn(
            stream: AsyncGenerator[None, None],
        ) -> AsyncGenerator[int, None]:
            for i in range(1, 8):  # 1, 2, 3, 4, 5, 6, 7
                yield i

        flow = Flow(source_fn, name="source")
        batched_flow = flow.batch(3)

        async def empty_stream() -> AsyncGenerator[None, None]:
            return
            yield  # pragma: no cover

        result = batched_flow(empty_stream())
        items = [item async for item in result]

        assert items == [[1, 2, 3], [4, 5, 6], [7]]

    @pytest.mark.asyncio
    async def test_batch_with_empty_stream(self) -> None:
        """Test that batch handles empty streams correctly."""

        async def empty_source(
            stream: AsyncGenerator[None, None],
        ) -> AsyncGenerator[int, None]:
            return
            yield  # pragma: no cover

        flow = Flow(empty_source, name="empty")
        batched_flow = flow.batch(3)

        async def empty_stream() -> AsyncGenerator[None, None]:
            return
            yield  # pragma: no cover

        result = batched_flow(empty_stream())
        items = [item async for item in result]

        assert items == []

    @pytest.mark.asyncio
    async def test_batch_with_single_item(self) -> None:
        """Test that batch works with single item streams."""

        async def single_source(
            stream: AsyncGenerator[None, None],
        ) -> AsyncGenerator[str, None]:
            yield "single"

        flow = Flow(single_source, name="single")
        batched_flow = flow.batch(5)

        async def empty_stream() -> AsyncGenerator[None, None]:
            return
            yield  # pragma: no cover

        result = batched_flow(empty_stream())
        items = [item async for item in result]

        assert items == [["single"]]

    @pytest.mark.asyncio
    async def test_batch_exact_size_multiples(self) -> None:
        """Test batch when stream size is exact multiple of batch size."""

        async def source_fn(
            stream: AsyncGenerator[None, None],
        ) -> AsyncGenerator[int, None]:
            for i in [1, 2, 3, 4, 5, 6]:
                yield i

        flow = Flow(source_fn, name="source")
        batched_flow = flow.batch(2)

        async def empty_stream() -> AsyncGenerator[None, None]:
            return
            yield  # pragma: no cover

        result = batched_flow(empty_stream())
        items = [item async for item in result]

        assert items == [[1, 2], [3, 4], [5, 6]]

    @pytest.mark.asyncio
    async def test_batch_size_one(self) -> None:
        """Test batch with size 1 (each item becomes its own batch)."""

        async def source_fn(
            stream: AsyncGenerator[None, None],
        ) -> AsyncGenerator[str, None]:
            for s in ["a", "b", "c"]:
                yield s

        flow = Flow(source_fn, name="source")
        batched_flow = flow.batch(1)

        async def empty_stream() -> AsyncGenerator[None, None]:
            return
            yield  # pragma: no cover

        result = batched_flow(empty_stream())
        items = [item async for item in result]

        assert items == [["a"], ["b"], ["c"]]

    @pytest.mark.asyncio
    async def test_batch_larger_than_stream(self) -> None:
        """Test batch when batch size is larger than stream."""

        async def small_source(
            stream: AsyncGenerator[None, None],
        ) -> AsyncGenerator[int, None]:
            for i in [10, 20]:
                yield i

        flow = Flow(small_source, name="small")
        batched_flow = flow.batch(5)

        async def empty_stream() -> AsyncGenerator[None, None]:
            return
            yield  # pragma: no cover

        result = batched_flow(empty_stream())
        items = [item async for item in result]

        assert items == [[10, 20]]

    def test_batch_creates_new_flow_with_descriptive_name(self) -> None:
        """Test that batch creates a new flow with descriptive name."""

        async def test_fn(
            stream: AsyncGenerator[int, None],
        ) -> AsyncGenerator[str, None]:
            async for item in stream:
                yield str(item)

        flow = Flow(test_fn, name="stringify")
        batched_flow = flow.batch(3)

        assert batched_flow.name == "stringify.batch(3)"
        assert batched_flow is not flow  # type: ignore[comparison-overlap]

    @pytest.mark.asyncio
    async def test_batch_preserves_item_type_in_lists(self) -> None:
        """Test that batch preserves the type of items within batches."""

        async def typed_fn(
            stream: AsyncGenerator[str, None],
        ) -> AsyncGenerator[int, None]:
            async for item in stream:
                yield len(item)

        flow = Flow(typed_fn, name="length")
        batched_flow = flow.batch(2)

        async def string_stream() -> AsyncGenerator[str, None]:
            for s in ["hi", "hello", "world", "test"]:
                yield s

        result = batched_flow(string_stream())
        items = [item async for item in result]

        assert items == [[2, 5], [5, 4]]
        # Each batch should be a list of integers
        assert all(isinstance(batch, list) for batch in items)
        assert all(isinstance(item, int) for batch in items for item in batch)

    @pytest.mark.asyncio
    async def test_batch_chaining_with_other_operations(self) -> None:
        """Test that batch can be chained with other flow operations."""

        async def source_fn(
            stream: AsyncGenerator[None, None],
        ) -> AsyncGenerator[int, None]:
            for i in range(1, 8):
                yield i

        def sum_batch(batch: list[int]) -> int:
            return sum(batch)

        flow = Flow(source_fn, name="source")
        chained_flow = flow.batch(3).map(sum_batch)

        async def empty_stream() -> AsyncGenerator[None, None]:
            return
            yield  # pragma: no cover

        result = chained_flow(empty_stream())
        items = [item async for item in result]

        assert items == [6, 15, 7]  # sum([1,2,3]), sum([4,5,6]), sum([7])

    @pytest.mark.asyncio
    async def test_batch_with_different_input_streams(self) -> None:
        """Test that batch works with different input stream types."""

        async def transform_fn(
            stream: AsyncGenerator[str, None],
        ) -> AsyncGenerator[str, None]:
            async for item in stream:
                yield item.upper()

        flow = Flow(transform_fn, name="upper")
        batched_flow = flow.batch(2)

        async def string_stream() -> AsyncGenerator[str, None]:
            for s in ["a", "b", "c", "d", "e"]:
                yield s

        result = batched_flow(string_stream())
        items = [item async for item in result]

        assert items == [["A", "B"], ["C", "D"], ["E"]]

    @pytest.mark.asyncio
    async def test_batch_with_transformed_flow(self) -> None:
        """Test that batch works with previously transformed flows."""

        async def source_fn(
            stream: AsyncGenerator[None, None],
        ) -> AsyncGenerator[int, None]:
            for i in range(1, 10):
                yield i

        def is_even(x: int) -> bool:
            return x % 2 == 0

        def square(x: int) -> int:
            return x * x

        flow = Flow(source_fn, name="source")
        transformed_flow = flow.filter(is_even).map(square).batch(2)

        async def empty_stream() -> AsyncGenerator[None, None]:
            return
            yield  # pragma: no cover

        result = transformed_flow(empty_stream())
        items = [item async for item in result]

        # Even numbers: 2, 4, 6, 8
        # Squared: 4, 16, 36, 64
        # Batched by 2: [4, 16], [36, 64]
        assert items == [[4, 16], [36, 64]]

    @pytest.mark.asyncio
    async def test_batch_maintains_order(self) -> None:
        """Test that batch maintains the order of items."""

        async def source_fn(
            stream: AsyncGenerator[None, None],
        ) -> AsyncGenerator[str, None]:
            sequence = ["first", "second", "third", "fourth", "fifth"]
            for item in sequence:
                yield item

        flow = Flow(source_fn, name="sequence")
        batched_flow = flow.batch(2)

        async def empty_stream() -> AsyncGenerator[None, None]:
            return
            yield  # pragma: no cover

        result = batched_flow(empty_stream())
        items = [item async for item in result]

        assert items == [["first", "second"], ["third", "fourth"], ["fifth"]]
