from typing import AsyncGenerator

import pytest

from flow.combinators.utils import empty_stream
from flow.flow import Flow


class TestFlowMap:
    """Tests for Flow.map method."""

    @pytest.mark.asyncio
    async def test_map_transforms_values(self) -> None:
        """Test that map applies function to each item in the stream."""

        async def source_fn(
            stream: AsyncGenerator[None, None],
        ) -> AsyncGenerator[int, None]:
            for i in [1, 2, 3]:
                yield i

        def double(x: int) -> int:
            return x * 2

        flow = Flow(source_fn, name="source")
        mapped_flow = flow.map(double)

        result = mapped_flow(empty_stream())
        items = [item async for item in result]

        assert items == [2, 4, 6]

    @pytest.mark.asyncio
    async def test_map_changes_output_type(self) -> None:
        """Test that map can change the output type of the flow."""

        async def int_source(
            stream: AsyncGenerator[None, None],
        ) -> AsyncGenerator[int, None]:
            for i in [10, 20, 30]:
                yield i

        def int_to_string(x: int) -> str:
            return f"value_{x}"

        flow = Flow(int_source, name="int_source")
        string_flow = flow.map(int_to_string)

        async def empty_stream() -> AsyncGenerator[None, None]:
            return
            yield  # pragma: no cover

        result = string_flow(empty_stream())
        items = [item async for item in result]

        assert items == ["value_10", "value_20", "value_30"]

    @pytest.mark.asyncio
    async def test_map_preserves_input_type(self) -> None:
        """Test that map preserves the input type of the original flow."""

        async def transform_fn(
            stream: AsyncGenerator[str, None],
        ) -> AsyncGenerator[int, None]:
            async for item in stream:
                yield len(item)

        def square(x: int) -> int:
            return x * x

        flow = Flow(transform_fn, name="transform")
        mapped_flow = flow.map(square)

        async def string_stream() -> AsyncGenerator[str, None]:
            for s in ["hi", "test", "hello"]:
                yield s

        result = mapped_flow(string_stream())
        items = [item async for item in result]

        assert items == [4, 16, 25]  # len("hi")^2, len("test")^2, len("hello")^2

    def test_map_creates_new_flow_with_descriptive_name(self) -> None:
        """Test that map creates a new flow with a descriptive name."""

        async def test_fn(
            stream: AsyncGenerator[int, None],
        ) -> AsyncGenerator[str, None]:
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

        async def empty_source(
            stream: AsyncGenerator[None, None],
        ) -> AsyncGenerator[int, None]:
            return
            yield  # pragma: no cover

        def multiply_by_ten(x: int) -> int:
            return x * 10

        flow = Flow(empty_source, name="empty")
        mapped_flow = flow.map(multiply_by_ten)

        result = mapped_flow(empty_stream())
        items = [item async for item in result]

        assert items == []

    @pytest.mark.asyncio
    async def test_map_chaining(self) -> None:
        """Test that multiple maps can be chained together."""

        async def source_fn(
            stream: AsyncGenerator[None, None],
        ) -> AsyncGenerator[int, None]:
            for i in [1, 2, 3]:
                yield i

        def add_one(x: int) -> int:
            return x + 1

        def multiply_by_three(x: int) -> int:
            return x * 3

        flow = Flow(source_fn, name="source")
        chained_flow = flow.map(add_one).map(multiply_by_three)

        async def empty_stream() -> AsyncGenerator[None, None]:
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

        async def source_fn(
            stream: AsyncGenerator[None, None],
        ) -> AsyncGenerator[int, None]:
            for i in [1, 2, 3, 4, 5, 6]:
                yield i

        def is_even(x: int) -> bool:
            return x % 2 == 0

        flow = Flow(source_fn, name="source")
        filtered_flow = flow.filter(is_even)

        async def empty_stream() -> AsyncGenerator[None, None]:
            return
            yield  # pragma: no cover

        result = filtered_flow(empty_stream())
        items = [item async for item in result]

        assert items == [2, 4, 6]

    @pytest.mark.asyncio
    async def test_filter_preserves_output_type(self) -> None:
        """Test that filter preserves the output type of the flow."""

        async def string_source(
            stream: AsyncGenerator[None, None],
        ) -> AsyncGenerator[str, None]:
            for s in ["apple", "banana", "cherry", "date"]:
                yield s

        def starts_with_a_or_c(s: str) -> bool:
            return s.startswith("a") or s.startswith("c")

        flow = Flow(string_source, name="strings")
        filtered_flow = flow.filter(starts_with_a_or_c)

        async def empty_stream() -> AsyncGenerator[None, None]:
            return
            yield  # pragma: no cover

        result = filtered_flow(empty_stream())
        items = [item async for item in result]

        assert items == ["apple", "cherry"]

    @pytest.mark.asyncio
    async def test_filter_preserves_input_type(self) -> None:
        """Test that filter preserves the input type of the original flow."""

        async def transform_fn(
            stream: AsyncGenerator[str, None],
        ) -> AsyncGenerator[int, None]:
            async for item in stream:
                yield len(item)

        def is_short(length: int) -> bool:
            return length <= 3

        flow = Flow(transform_fn, name="length_transform")
        filtered_flow = flow.filter(is_short)

        async def string_stream() -> AsyncGenerator[str, None]:
            for s in ["hi", "test", "a", "hello", "ok"]:
                yield s

        result = filtered_flow(string_stream())
        items = [item async for item in result]

        assert items == [2, 1, 2]  # len("hi"), len("a"), len("ok")

    def test_filter_creates_new_flow_with_descriptive_name(self) -> None:
        """Test that filter creates a new flow with a descriptive name."""

        async def test_fn(
            stream: AsyncGenerator[int, None],
        ) -> AsyncGenerator[int, None]:
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

        async def empty_source(
            stream: AsyncGenerator[None, None],
        ) -> AsyncGenerator[int, None]:
            return
            yield  # pragma: no cover

        def always_true(x: int) -> bool:
            return True

        flow = Flow(empty_source, name="empty")
        filtered_flow = flow.filter(always_true)

        async def empty_stream() -> AsyncGenerator[None, None]:
            return
            yield  # pragma: no cover

        result = filtered_flow(empty_stream())
        items = [item async for item in result]

        assert items == []

    @pytest.mark.asyncio
    async def test_filter_with_no_matches(self) -> None:
        """Test that filter returns empty stream when no items match."""

        async def source_fn(
            stream: AsyncGenerator[None, None],
        ) -> AsyncGenerator[int, None]:
            for i in [1, 3, 5, 7, 9]:
                yield i

        def is_even(x: int) -> bool:
            return x % 2 == 0

        flow = Flow(source_fn, name="odds")
        filtered_flow = flow.filter(is_even)

        async def empty_stream() -> AsyncGenerator[None, None]:
            return
            yield  # pragma: no cover

        result = filtered_flow(empty_stream())
        items = [item async for item in result]

        assert items == []

    @pytest.mark.asyncio
    async def test_filter_chaining_with_map(self) -> None:
        """Test that filter can be chained with map operations."""

        async def source_fn(
            stream: AsyncGenerator[None, None],
        ) -> AsyncGenerator[int, None]:
            for i in [1, 2, 3, 4, 5]:
                yield i

        def is_odd(x: int) -> bool:
            return x % 2 == 1

        def square(x: int) -> int:
            return x * x

        flow = Flow(source_fn, name="source")
        chained_flow = flow.filter(is_odd).map(square)

        async def empty_stream() -> AsyncGenerator[None, None]:
            return
            yield  # pragma: no cover

        result = chained_flow(empty_stream())
        items = [item async for item in result]

        assert items == [1, 9, 25]  # 1^2, 3^2, 5^2


class TestFlowFlatMap:
    """Tests for Flow.flat_map method."""

    @pytest.mark.asyncio
    async def test_flat_map_flattens_async_iterators(self) -> None:
        """Test that flat_map flattens nested async iterators into a single stream."""

        async def source_fn(
            stream: AsyncGenerator[None, None],
        ) -> AsyncGenerator[str, None]:
            for s in ["hello", "world"]:
                yield s

        async def split_chars(text: str) -> AsyncGenerator[str, None]:
            for char in text:
                yield char

        flow = Flow(source_fn, name="source")
        flat_mapped_flow = flow.flat_map(split_chars)

        async def empty_stream() -> AsyncGenerator[None, None]:
            return
            yield  # pragma: no cover

        result = flat_mapped_flow(empty_stream())
        items = [item async for item in result]

        assert items == ["h", "e", "l", "l", "o", "w", "o", "r", "l", "d"]

    @pytest.mark.asyncio
    async def test_flat_map_changes_output_type(self) -> None:
        """Test that flat_map can change the output type of the flow."""

        async def int_source(
            stream: AsyncGenerator[None, None],
        ) -> AsyncGenerator[int, None]:
            for i in [3, 2]:
                yield i

        async def repeat_number(n: int) -> AsyncGenerator[str, None]:
            for _ in range(n):
                yield str(n)

        flow = Flow(int_source, name="int_source")
        string_flow = flow.flat_map(repeat_number)

        async def empty_stream() -> AsyncGenerator[None, None]:
            return
            yield  # pragma: no cover

        result = string_flow(empty_stream())
        items = [item async for item in result]

        assert items == ["3", "3", "3", "2", "2"]

    @pytest.mark.asyncio
    async def test_flat_map_preserves_input_type(self) -> None:
        """Test that flat_map preserves the input type of the original flow."""

        async def transform_fn(
            stream: AsyncGenerator[str, None],
        ) -> AsyncGenerator[int, None]:
            async for item in stream:
                yield len(item)

        async def expand_to_range(n: int) -> AsyncGenerator[int, None]:
            for i in range(n):
                yield i

        flow = Flow(transform_fn, name="length_transform")
        flat_mapped_flow = flow.flat_map(expand_to_range)

        async def string_stream() -> AsyncGenerator[str, None]:
            for s in ["hi", "a", "test"]:
                yield s

        result = flat_mapped_flow(string_stream())
        items = [item async for item in result]

        assert items == [0, 1, 0, 0, 1, 2, 3]  # range(2), range(1), range(4)

    def test_flat_map_creates_new_flow_with_descriptive_name(self) -> None:
        """Test that flat_map creates a new flow with a descriptive name."""

        async def test_fn(
            stream: AsyncGenerator[str, None],
        ) -> AsyncGenerator[str, None]:
            async for item in stream:
                yield item.upper()

        async def split_words(text: str) -> AsyncGenerator[str, None]:
            for word in text.split():
                yield word

        flow = Flow(test_fn, name="upper_case")
        flat_mapped_flow = flow.flat_map(split_words)

        assert flat_mapped_flow.name == "upper_case.flat_map(split_words)"
        assert flat_mapped_flow is not flow  # Should be a new flow instance

    @pytest.mark.asyncio
    async def test_flat_map_with_empty_stream(self) -> None:
        """Test that flat_map works correctly with empty streams."""

        async def empty_source(
            stream: AsyncGenerator[None, None],
        ) -> AsyncGenerator[int, None]:
            return
            yield  # pragma: no cover

        async def create_range(n: int) -> AsyncGenerator[int, None]:
            for i in range(n):
                yield i

        flow = Flow(empty_source, name="empty")
        flat_mapped_flow = flow.flat_map(create_range)

        async def empty_stream() -> AsyncGenerator[None, None]:
            return
            yield  # pragma: no cover

        result = flat_mapped_flow(empty_stream())
        items = [item async for item in result]

        assert items == []

    @pytest.mark.asyncio
    async def test_flat_map_with_empty_inner_iterators(self) -> None:
        """Test that flat_map works when inner iterators are empty."""

        async def source_fn(
            stream: AsyncGenerator[None, None],
        ) -> AsyncGenerator[int, None]:
            for i in [0, 1, 0, 2]:
                yield i

        async def create_range(n: int) -> AsyncGenerator[str, None]:
            for i in range(n):
                yield f"item_{i}"

        flow = Flow(source_fn, name="source")
        flat_mapped_flow = flow.flat_map(create_range)

        async def empty_stream() -> AsyncGenerator[None, None]:
            return
            yield  # pragma: no cover

        result = flat_mapped_flow(empty_stream())
        items = [item async for item in result]

        assert items == ["item_0", "item_0", "item_1"]  # range(0) is empty

    @pytest.mark.asyncio
    async def test_flat_map_chaining_with_map_and_filter(self) -> None:
        """Test that flat_map can be chained with other operations."""

        async def source_fn(
            stream: AsyncGenerator[None, None],
        ) -> AsyncGenerator[str, None]:
            for s in ["ab", "cd"]:
                yield s

        async def duplicate_chars(text: str) -> AsyncGenerator[str, None]:
            for char in text:
                yield char
                yield char

        def is_vowel(char: str) -> bool:
            return char.lower() in "aeiou"

        def to_upper(char: str) -> str:
            return char.upper()

        flow = Flow(source_fn, name="source")
        chained_flow = flow.flat_map(duplicate_chars).filter(is_vowel).map(to_upper)

        async def empty_stream() -> AsyncGenerator[None, None]:
            return
            yield  # pragma: no cover

        result = chained_flow(empty_stream())
        items = [item async for item in result]

        assert items == [
            "A",
            "A",
        ]  # Only 'a' chars from "ab" doubled, filtered, and uppercased
