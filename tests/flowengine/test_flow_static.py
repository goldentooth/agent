from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator

import pytest

from flowengine.flow import Flow


class TestFlowFromValueFn:
    """Tests for Flow.from_value_fn static method."""

    @pytest.mark.asyncio
    async def test_from_value_fn_creates_flow_from_async_function(self) -> None:
        """Test that from_value_fn creates a flow from an async function."""

        async def double_async(x: int) -> int:
            return x * 2

        flow = Flow.from_value_fn(double_async)

        async def int_stream() -> AsyncIterator[int]:
            for i in [1, 2, 3]:
                yield i

        result = flow(int_stream())
        items = [item async for item in result]

        assert items == [2, 4, 6]

    @pytest.mark.asyncio
    async def test_from_value_fn_as_decorator(self) -> None:
        """Test that from_value_fn can be used as a decorator."""

        @Flow.from_value_fn
        async def process_item(x: str) -> str:
            return x.upper()

        async def string_stream() -> AsyncIterator[str]:
            for s in ["hello", "world"]:
                yield s

        result = process_item(string_stream())
        items = [item async for item in result]

        assert items == ["HELLO", "WORLD"]

    def test_from_value_fn_sets_function_name(self) -> None:
        """Test that from_value_fn uses the function name for the flow."""

        async def transform_data(x: int) -> str:
            return f"item_{x}"

        flow = Flow.from_value_fn(transform_data)

        assert flow.name == "transform_data"

    @pytest.mark.asyncio
    async def test_from_value_fn_with_empty_stream(self) -> None:
        """Test that from_value_fn works with empty streams."""

        async def add_ten(x: int) -> int:
            return x + 10

        flow = Flow.from_value_fn(add_ten)

        async def empty_stream() -> AsyncIterator[int]:
            return
            yield  # pragma: no cover

        result = flow(empty_stream())
        items = [item async for item in result]

        assert items == []

    @pytest.mark.asyncio
    async def test_from_value_fn_preserves_types(self) -> None:
        """Test that from_value_fn preserves input/output types."""

        async def length_func(s: str) -> int:
            return len(s)

        flow = Flow.from_value_fn(length_func)

        async def string_stream() -> AsyncIterator[str]:
            for s in ["a", "bb", "ccc"]:
                yield s

        result = flow(string_stream())
        items = [item async for item in result]

        assert items == [1, 2, 3]
        assert all(isinstance(item, int) for item in items)

    @pytest.mark.asyncio
    async def test_from_value_fn_with_single_item(self) -> None:
        """Test that from_value_fn works with single item streams."""

        async def square(x: int) -> int:
            return x * x

        flow = Flow.from_value_fn(square)

        async def single_stream() -> AsyncIterator[int]:
            yield 5

        result = flow(single_stream())
        items = [item async for item in result]

        assert items == [25]

    @pytest.mark.asyncio
    async def test_from_value_fn_chaining(self) -> None:
        """Test that flows from from_value_fn can be chained."""

        async def add_one(x: int) -> int:
            return x + 1

        async def multiply_two(x: int) -> int:
            return x * 2

        flow1 = Flow.from_value_fn(add_one)
        flow2 = Flow.from_value_fn(multiply_two)
        chained = flow1 >> flow2

        async def int_stream() -> AsyncIterator[int]:
            for i in [1, 2, 3]:
                yield i

        result = chained(int_stream())
        items = [item async for item in result]

        assert items == [4, 6, 8]  # (1+1)*2, (2+1)*2, (3+1)*2

    @pytest.mark.asyncio
    async def test_from_value_fn_error_handling(self) -> None:
        """Test that from_value_fn properly propagates exceptions."""

        async def failing_func(x: int) -> int:
            if x == 2:
                raise ValueError("Test error")
            return x * 10

        flow = Flow.from_value_fn(failing_func)

        async def int_stream() -> AsyncIterator[int]:
            for i in [1, 2, 3]:
                yield i

        result = flow(int_stream())

        # Should get first item, then error on second
        items = []
        with pytest.raises(ValueError, match="Test error"):
            async for item in result:
                items.append(item)

        assert items == [10]  # Only first item before error

    def test_from_value_fn_without_argument_returns_decorator(self) -> None:
        """Test that from_value_fn() without argument returns a decorator."""

        decorator = Flow.from_value_fn()
        assert callable(decorator)

        async def test_func(x: str) -> str:
            return x.lower()

        flow = decorator(test_func)
        assert isinstance(flow, Flow)
        assert flow.name == "test_func"

    @pytest.mark.asyncio
    async def test_from_value_fn_with_complex_types(self) -> None:
        """Test from_value_fn with complex input/output types."""

        async def process_dict(data: dict[str, int]) -> list[str]:
            return [f"{k}:{v}" for k, v in data.items()]

        flow = Flow.from_value_fn(process_dict)

        async def dict_stream() -> AsyncIterator[dict[str, int]]:
            yield {"a": 1, "b": 2}
            yield {"x": 10}

        result = flow(dict_stream())
        items = [item async for item in result]

        assert items == [["a:1", "b:2"], ["x:10"]]


class TestFlowFromSyncFn:
    """Tests for Flow.from_sync_fn static method."""

    @pytest.mark.asyncio
    async def test_from_sync_fn_creates_flow_from_sync_function(self) -> None:
        """Test that from_sync_fn creates a flow from a sync function."""

        def double_sync(x: int) -> int:
            return x * 2

        flow = Flow.from_sync_fn(double_sync)

        async def int_stream() -> AsyncIterator[int]:
            for i in [1, 2, 3]:
                yield i

        result = flow(int_stream())
        items = [item async for item in result]

        assert items == [2, 4, 6]

    @pytest.mark.asyncio
    async def test_from_sync_fn_as_decorator(self) -> None:
        """Test that from_sync_fn can be used as a decorator."""

        @Flow.from_sync_fn
        def process_item(x: str) -> str:
            return x.upper()

        async def string_stream() -> AsyncIterator[str]:
            for s in ["hello", "world"]:
                yield s

        result = process_item(string_stream())
        items = [item async for item in result]

        assert items == ["HELLO", "WORLD"]

    def test_from_sync_fn_sets_function_name(self) -> None:
        """Test that from_sync_fn uses the function name for the flow."""

        def transform_data(x: int) -> str:
            return f"item_{x}"

        flow = Flow.from_sync_fn(transform_data)

        assert flow.name == "transform_data"

    @pytest.mark.asyncio
    async def test_from_sync_fn_with_empty_stream(self) -> None:
        """Test that from_sync_fn works with empty streams."""

        def add_ten(x: int) -> int:
            return x + 10

        flow = Flow.from_sync_fn(add_ten)

        async def empty_stream() -> AsyncIterator[int]:
            return
            yield  # pragma: no cover

        result = flow(empty_stream())
        items = [item async for item in result]

        assert items == []

    @pytest.mark.asyncio
    async def test_from_sync_fn_preserves_types(self) -> None:
        """Test that from_sync_fn preserves input/output types."""

        def length_func(s: str) -> int:
            return len(s)

        flow = Flow.from_sync_fn(length_func)

        async def string_stream() -> AsyncIterator[str]:
            for s in ["a", "bb", "ccc"]:
                yield s

        result = flow(string_stream())
        items = [item async for item in result]

        assert items == [1, 2, 3]
        assert all(isinstance(item, int) for item in items)

    @pytest.mark.asyncio
    async def test_from_sync_fn_with_single_item(self) -> None:
        """Test that from_sync_fn works with single item streams."""

        def square(x: int) -> int:
            return x * x

        flow = Flow.from_sync_fn(square)

        async def single_stream() -> AsyncIterator[int]:
            yield 5

        result = flow(single_stream())
        items = [item async for item in result]

        assert items == [25]

    @pytest.mark.asyncio
    async def test_from_sync_fn_chaining(self) -> None:
        """Test that flows from from_sync_fn can be chained."""

        def add_one(x: int) -> int:
            return x + 1

        def multiply_two(x: int) -> int:
            return x * 2

        flow1 = Flow.from_sync_fn(add_one)
        flow2 = Flow.from_sync_fn(multiply_two)
        chained = flow1 >> flow2

        async def int_stream() -> AsyncIterator[int]:
            for i in [1, 2, 3]:
                yield i

        result = chained(int_stream())
        items = [item async for item in result]

        assert items == [4, 6, 8]  # (1+1)*2, (2+1)*2, (3+1)*2

    @pytest.mark.asyncio
    async def test_from_sync_fn_error_handling(self) -> None:
        """Test that from_sync_fn properly propagates exceptions."""

        def failing_func(x: int) -> int:
            if x == 2:
                raise ValueError("Test error")
            return x * 10

        flow = Flow.from_sync_fn(failing_func)

        async def int_stream() -> AsyncIterator[int]:
            for i in [1, 2, 3]:
                yield i

        result = flow(int_stream())

        # Should get first item, then error on second
        items = []
        with pytest.raises(ValueError, match="Test error"):
            async for item in result:
                items.append(item)

        assert items == [10]  # Only first item before error

    def test_from_sync_fn_without_argument_returns_decorator(self) -> None:
        """Test that from_sync_fn() without argument returns a decorator."""

        decorator = Flow.from_sync_fn()
        assert callable(decorator)

        def test_func(x: str) -> str:
            return x.lower()

        flow = decorator(test_func)
        assert isinstance(flow, Flow)
        assert flow.name == "test_func"

    @pytest.mark.asyncio
    async def test_from_sync_fn_with_complex_types(self) -> None:
        """Test from_sync_fn with complex input/output types."""

        def process_dict(data: dict[str, int]) -> list[str]:
            return [f"{k}:{v}" for k, v in data.items()]

        flow = Flow.from_sync_fn(process_dict)

        async def dict_stream() -> AsyncIterator[dict[str, int]]:
            yield {"a": 1, "b": 2}
            yield {"x": 10}

        result = flow(dict_stream())
        items = [item async for item in result]

        assert items == [["a:1", "b:2"], ["x:10"]]

    @pytest.mark.asyncio
    async def test_from_sync_fn_vs_from_value_fn_difference(self) -> None:
        """Test the difference between sync and async function flows."""

        def sync_double(x: int) -> int:
            return x * 2

        async def async_double(x: int) -> int:
            return x * 2

        sync_flow = Flow.from_sync_fn(sync_double)
        async_flow = Flow.from_value_fn(async_double)

        async def int_stream() -> AsyncIterator[int]:
            for i in [1, 2, 3]:
                yield i

        # Both should produce the same result
        sync_result = sync_flow(int_stream())
        sync_items = [item async for item in sync_result]

        async def int_stream2() -> AsyncIterator[int]:
            for i in [1, 2, 3]:
                yield i

        async_result = async_flow(int_stream2())
        async_items = [item async for item in async_result]

        assert sync_items == async_items == [2, 4, 6]

    @pytest.mark.asyncio
    async def test_from_sync_fn_with_side_effects(self) -> None:
        """Test that from_sync_fn works with functions that have side effects."""

        processed_items = []

        def process_with_side_effect(x: str) -> str:
            processed_items.append(f"processed_{x}")
            return x.upper()

        flow = Flow.from_sync_fn(process_with_side_effect)

        async def string_stream() -> AsyncIterator[str]:
            for s in ["a", "b"]:
                yield s

        result = flow(string_stream())
        items = [item async for item in result]

        assert items == ["A", "B"]
        assert processed_items == ["processed_a", "processed_b"]


class TestFlowFromEventFn:
    """Tests for Flow.from_event_fn static method."""

    @pytest.mark.asyncio
    async def test_from_event_fn_creates_flow_from_async_iterator_function(
        self,
    ) -> None:
        """Test that from_event_fn creates a flow from an async iterator function."""

        async def split_lines(text: str) -> AsyncIterator[str]:
            for line in text.split("\n"):
                yield line

        flow = Flow.from_event_fn(split_lines)

        async def text_stream() -> AsyncIterator[str]:
            yield "hello\nworld"
            yield "foo\nbar\nbaz"

        result = flow(text_stream())
        items = [item async for item in result]

        assert items == ["hello", "world", "foo", "bar", "baz"]

    @pytest.mark.asyncio
    async def test_from_event_fn_as_decorator(self) -> None:
        """Test that from_event_fn can be used as a decorator."""

        @Flow.from_event_fn
        async def split_words(text: str) -> AsyncIterator[str]:
            for word in text.split():
                yield word.upper()

        async def text_stream() -> AsyncIterator[str]:
            yield "hello world"
            yield "foo bar"

        result = split_words(text_stream())
        items = [item async for item in result]

        assert items == ["HELLO", "WORLD", "FOO", "BAR"]

    def test_from_event_fn_sets_function_name(self) -> None:
        """Test that from_event_fn uses the function name for the flow."""

        async def process_data(x: int) -> AsyncIterator[str]:
            for i in range(x):
                yield f"item_{i}"

        flow = Flow.from_event_fn(process_data)

        assert flow.name == "process_data"

    @pytest.mark.asyncio
    async def test_from_event_fn_with_empty_stream(self) -> None:
        """Test that from_event_fn works with empty streams."""

        async def generate_range(n: int) -> AsyncIterator[int]:
            for i in range(n):
                yield i

        flow = Flow.from_event_fn(generate_range)

        async def empty_stream() -> AsyncIterator[int]:
            return
            yield  # pragma: no cover

        result = flow(empty_stream())
        items = [item async for item in result]

        assert items == []

    @pytest.mark.asyncio
    async def test_from_event_fn_preserves_types(self) -> None:
        """Test that from_event_fn preserves input/output types."""

        async def duplicate_items(s: str) -> AsyncIterator[int]:
            for _ in range(2):
                yield len(s)

        flow = Flow.from_event_fn(duplicate_items)

        async def string_stream() -> AsyncIterator[str]:
            yield "ab"
            yield "cde"

        result = flow(string_stream())
        items = [item async for item in result]

        assert items == [2, 2, 3, 3]
        assert all(isinstance(item, int) for item in items)

    @pytest.mark.asyncio
    async def test_from_event_fn_with_single_item(self) -> None:
        """Test that from_event_fn works with single item streams."""

        async def explode_number(n: int) -> AsyncIterator[int]:
            for i in range(1, n + 1):
                yield i * i

        flow = Flow.from_event_fn(explode_number)

        async def single_stream() -> AsyncIterator[int]:
            yield 3

        result = flow(single_stream())
        items = [item async for item in result]

        assert items == [1, 4, 9]  # 1^2, 2^2, 3^2

    @pytest.mark.asyncio
    async def test_from_event_fn_chaining(self) -> None:
        """Test that flows from from_event_fn can be chained."""

        async def duplicate(x: int) -> AsyncIterator[int]:
            yield x
            yield x

        def add_ten(x: int) -> int:
            return x + 10

        event_flow = Flow.from_event_fn(duplicate)
        sync_flow = Flow.from_sync_fn(add_ten)
        chained = event_flow >> sync_flow

        async def int_stream() -> AsyncIterator[int]:
            for i in [1, 2]:
                yield i

        result = chained(int_stream())
        items = [item async for item in result]

        assert items == [11, 11, 12, 12]  # (1+10, 1+10, 2+10, 2+10)

    @pytest.mark.asyncio
    async def test_from_event_fn_error_handling(self) -> None:
        """Test that from_event_fn properly propagates exceptions."""

        async def failing_generator(x: int) -> AsyncIterator[int]:
            yield x
            if x == 2:
                raise ValueError("Test error")
            yield x * 2

        flow = Flow.from_event_fn(failing_generator)

        async def int_stream() -> AsyncIterator[int]:
            for i in [1, 2, 3]:
                yield i

        result = flow(int_stream())

        # Should get some items, then error
        items = []
        with pytest.raises(ValueError, match="Test error"):
            async for item in result:
                items.append(item)

        assert items == [1, 2, 2]  # 1, 1*2, 2 (then error before 2*2)

    def test_from_event_fn_without_argument_returns_decorator(self) -> None:
        """Test that from_event_fn() without argument returns a decorator."""

        decorator = Flow.from_event_fn()
        assert callable(decorator)

        async def test_func(x: str) -> AsyncIterator[str]:
            for char in x:
                yield char

        flow = decorator(test_func)
        assert isinstance(flow, Flow)
        assert flow.name == "test_func"

    @pytest.mark.asyncio
    async def test_from_event_fn_with_empty_generators(self) -> None:
        """Test from_event_fn with functions that can return empty generators."""

        async def conditional_generate(x: int) -> AsyncIterator[str]:
            if x > 0:
                for i in range(x):
                    yield f"item_{i}"

        flow = Flow.from_event_fn(conditional_generate)

        async def mixed_stream() -> AsyncIterator[int]:
            yield 0  # Should produce no items
            yield 2  # Should produce 2 items
            yield -1  # Should produce no items

        result = flow(mixed_stream())
        items = [item async for item in result]

        assert items == ["item_0", "item_1"]

    @pytest.mark.asyncio
    async def test_from_event_fn_flattening_behavior(self) -> None:
        """Test that from_event_fn properly flattens nested async iterators."""

        async def create_pairs(n: int) -> AsyncIterator[tuple[int, int]]:
            for i in range(n):
                yield (i, i * 2)

        flow = Flow.from_event_fn(create_pairs)

        async def int_stream() -> AsyncIterator[int]:
            yield 2
            yield 1

        result = flow(int_stream())
        items = [item async for item in result]

        assert items == [(0, 0), (1, 2), (0, 0)]

    @pytest.mark.asyncio
    async def test_from_event_fn_with_async_operations(self) -> None:
        """Test from_event_fn with functions containing async operations."""

        async def async_expand(text: str) -> AsyncIterator[str]:
            for char in text:
                # Simulate async operation
                await asyncio.sleep(0.001)
                yield char.upper()

        flow = Flow.from_event_fn(async_expand)

        async def text_stream() -> AsyncIterator[str]:
            yield "ab"

        result = flow(text_stream())
        items = [item async for item in result]

        assert items == ["A", "B"]
