import asyncio
from typing import AsyncGenerator

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

        async def int_stream() -> AsyncGenerator[int, None]:
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

        async def string_stream() -> AsyncGenerator[str, None]:
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

        async def empty_stream() -> AsyncGenerator[int, None]:
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

        async def string_stream() -> AsyncGenerator[str, None]:
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

        async def single_stream() -> AsyncGenerator[int, None]:
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

        async def int_stream() -> AsyncGenerator[int, None]:
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

        async def int_stream() -> AsyncGenerator[int, None]:
            for i in [1, 2, 3]:
                yield i

        result = flow(int_stream())

        # Should get first item, then error on second
        items: list[int] = []
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

        async def dict_stream() -> AsyncGenerator[dict[str, int], None]:
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

        async def int_stream() -> AsyncGenerator[int, None]:
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

        async def string_stream() -> AsyncGenerator[str, None]:
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

        async def empty_stream() -> AsyncGenerator[int, None]:
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

        async def string_stream() -> AsyncGenerator[str, None]:
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

        async def single_stream() -> AsyncGenerator[int, None]:
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

        async def int_stream() -> AsyncGenerator[int, None]:
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

        async def int_stream() -> AsyncGenerator[int, None]:
            for i in [1, 2, 3]:
                yield i

        result = flow(int_stream())

        # Should get first item, then error on second
        items: list[int] = []
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

        async def dict_stream() -> AsyncGenerator[dict[str, int], None]:
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

        async def int_stream() -> AsyncGenerator[int, None]:
            for i in [1, 2, 3]:
                yield i

        # Both should produce the same result
        sync_result = sync_flow(int_stream())
        sync_items = [item async for item in sync_result]

        async def int_stream2() -> AsyncGenerator[int, None]:
            for i in [1, 2, 3]:
                yield i

        async_result = async_flow(int_stream2())
        async_items = [item async for item in async_result]

        assert sync_items == async_items == [2, 4, 6]

    @pytest.mark.asyncio
    async def test_from_sync_fn_with_side_effects(self) -> None:
        """Test that from_sync_fn works with functions that have side effects."""

        processed_items: list[str] = []

        def process_with_side_effect(x: str) -> str:
            processed_items.append(f"processed_{x}")
            return x.upper()

        flow = Flow.from_sync_fn(process_with_side_effect)

        async def string_stream() -> AsyncGenerator[str, None]:
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

        async def split_lines(text: str) -> AsyncGenerator[str, None]:
            for line in text.split("\n"):
                yield line

        flow = Flow.from_event_fn(split_lines)

        async def text_stream() -> AsyncGenerator[str, None]:
            yield "hello\nworld"
            yield "foo\nbar\nbaz"

        result = flow(text_stream())
        items = [item async for item in result]

        assert items == ["hello", "world", "foo", "bar", "baz"]

    @pytest.mark.asyncio
    async def test_from_event_fn_as_decorator(self) -> None:
        """Test that from_event_fn can be used as a decorator."""

        @Flow.from_event_fn
        async def split_words(text: str) -> AsyncGenerator[str, None]:
            for word in text.split():
                yield word.upper()

        async def text_stream() -> AsyncGenerator[str, None]:
            yield "hello world"
            yield "foo bar"

        result = split_words(text_stream())
        items = [item async for item in result]

        assert items == ["HELLO", "WORLD", "FOO", "BAR"]

    def test_from_event_fn_sets_function_name(self) -> None:
        """Test that from_event_fn uses the function name for the flow."""

        async def process_data(x: int) -> AsyncGenerator[str, None]:
            for i in range(x):
                yield f"item_{i}"

        flow = Flow.from_event_fn(process_data)

        assert flow.name == "process_data"

    @pytest.mark.asyncio
    async def test_from_event_fn_with_empty_stream(self) -> None:
        """Test that from_event_fn works with empty streams."""

        async def generate_range(n: int) -> AsyncGenerator[int, None]:
            for i in range(n):
                yield i

        flow = Flow.from_event_fn(generate_range)

        async def empty_stream() -> AsyncGenerator[int, None]:
            return
            yield  # pragma: no cover

        result = flow(empty_stream())
        items = [item async for item in result]

        assert items == []

    @pytest.mark.asyncio
    async def test_from_event_fn_preserves_types(self) -> None:
        """Test that from_event_fn preserves input/output types."""

        async def duplicate_items(s: str) -> AsyncGenerator[int, None]:
            for _ in range(2):
                yield len(s)

        flow = Flow.from_event_fn(duplicate_items)

        async def string_stream() -> AsyncGenerator[str, None]:
            yield "ab"
            yield "cde"

        result = flow(string_stream())
        items = [item async for item in result]

        assert items == [2, 2, 3, 3]
        assert all(isinstance(item, int) for item in items)

    @pytest.mark.asyncio
    async def test_from_event_fn_with_single_item(self) -> None:
        """Test that from_event_fn works with single item streams."""

        async def explode_number(n: int) -> AsyncGenerator[int, None]:
            for i in range(1, n + 1):
                yield i * i

        flow = Flow.from_event_fn(explode_number)

        async def single_stream() -> AsyncGenerator[int, None]:
            yield 3

        result = flow(single_stream())
        items = [item async for item in result]

        assert items == [1, 4, 9]  # 1^2, 2^2, 3^2

    @pytest.mark.asyncio
    async def test_from_event_fn_chaining(self) -> None:
        """Test that flows from from_event_fn can be chained."""

        async def duplicate(x: int) -> AsyncGenerator[int, None]:
            yield x
            yield x

        def add_ten(x: int) -> int:
            return x + 10

        event_flow = Flow.from_event_fn(duplicate)
        sync_flow = Flow.from_sync_fn(add_ten)
        chained = event_flow >> sync_flow

        async def int_stream() -> AsyncGenerator[int, None]:
            for i in [1, 2]:
                yield i

        result = chained(int_stream())
        items = [item async for item in result]

        assert items == [11, 11, 12, 12]  # (1+10, 1+10, 2+10, 2+10)

    @pytest.mark.asyncio
    async def test_from_event_fn_error_handling(self) -> None:
        """Test that from_event_fn properly propagates exceptions."""

        async def failing_generator(x: int) -> AsyncGenerator[int, None]:
            yield x
            if x == 2:
                raise ValueError("Test error")
            yield x * 2

        flow = Flow.from_event_fn(failing_generator)

        async def int_stream() -> AsyncGenerator[int, None]:
            for i in [1, 2, 3]:
                yield i

        result = flow(int_stream())

        # Should get some items, then error
        items: list[int] = []
        with pytest.raises(ValueError, match="Test error"):
            async for item in result:
                items.append(item)

        assert items == [1, 2, 2]  # 1, 1*2, 2 (then error before 2*2)

    def test_from_event_fn_without_argument_returns_decorator(self) -> None:
        """Test that from_event_fn() without argument returns a decorator."""

        decorator = Flow.from_event_fn()
        assert callable(decorator)

        async def test_func(x: str) -> AsyncGenerator[str, None]:
            for char in x:
                yield char

        flow = decorator(test_func)
        assert isinstance(flow, Flow)
        assert flow.name == "test_func"

    @pytest.mark.asyncio
    async def test_from_event_fn_with_empty_generators(self) -> None:
        """Test from_event_fn with functions that can return empty generators."""

        async def conditional_generate(x: int) -> AsyncGenerator[str, None]:
            if x > 0:
                for i in range(x):
                    yield f"item_{i}"

        flow = Flow.from_event_fn(conditional_generate)

        async def mixed_stream() -> AsyncGenerator[int, None]:
            yield 0  # Should produce no items
            yield 2  # Should produce 2 items
            yield -1  # Should produce no items

        result = flow(mixed_stream())
        items = [item async for item in result]

        assert items == ["item_0", "item_1"]

    @pytest.mark.asyncio
    async def test_from_event_fn_flattening_behavior(self) -> None:
        """Test that from_event_fn properly flattens nested async iterators."""

        async def create_pairs(n: int) -> AsyncGenerator[tuple[int, int], None]:
            for i in range(n):
                yield (i, i * 2)

        flow = Flow.from_event_fn(create_pairs)

        async def int_stream() -> AsyncGenerator[int, None]:
            yield 2
            yield 1

        result = flow(int_stream())
        items = [item async for item in result]

        assert items == [(0, 0), (1, 2), (0, 0)]

    @pytest.mark.asyncio
    async def test_from_event_fn_with_async_operations(self) -> None:
        """Test from_event_fn with functions containing async operations."""

        async def async_expand(text: str) -> AsyncGenerator[str, None]:
            for char in text:
                # Simulate async operation
                await asyncio.sleep(0.001)
                yield char.upper()

        flow = Flow.from_event_fn(async_expand)

        async def text_stream() -> AsyncGenerator[str, None]:
            yield "ab"

        result = flow(text_stream())
        items = [item async for item in result]

        assert items == ["A", "B"]


class TestFlowFromIterable:
    """Tests for Flow.from_iterable static method."""

    @pytest.mark.asyncio
    async def test_from_iterable_creates_flow_from_list(self) -> None:
        """Test that from_iterable creates a flow from a list."""

        data = [1, 2, 3, 4, 5]
        flow = Flow.from_iterable(data)

        async def empty_stream() -> AsyncGenerator[None, None]:
            yield None

        result = flow(empty_stream())
        items = [item async for item in result]

        assert items == [1, 2, 3, 4, 5]

    @pytest.mark.asyncio
    async def test_from_iterable_creates_flow_from_tuple(self) -> None:
        """Test that from_iterable creates a flow from a tuple."""

        data = ("a", "b", "c")
        flow = Flow.from_iterable(data)

        async def empty_stream() -> AsyncGenerator[None, None]:
            yield None

        result = flow(empty_stream())
        items = [item async for item in result]

        assert items == ["a", "b", "c"]

    @pytest.mark.asyncio
    async def test_from_iterable_creates_flow_from_range(self) -> None:
        """Test that from_iterable creates a flow from a range."""

        data = range(3, 7)
        flow = Flow.from_iterable(data)

        async def empty_stream() -> AsyncGenerator[None, None]:
            yield None

        result = flow(empty_stream())
        items = [item async for item in result]

        assert items == [3, 4, 5, 6]

    @pytest.mark.asyncio
    async def test_from_iterable_with_empty_iterable(self) -> None:
        """Test that from_iterable works with empty iterables."""

        data: list[int] = []
        flow = Flow.from_iterable(data)

        async def empty_stream() -> AsyncGenerator[None, None]:
            yield None

        result = flow(empty_stream())
        items = [item async for item in result]

        assert items == []

    @pytest.mark.asyncio
    async def test_from_iterable_with_generator(self) -> None:
        """Test that from_iterable works with generator expressions."""

        data = (x * 2 for x in range(4))
        flow = Flow.from_iterable(data)

        async def empty_stream() -> AsyncGenerator[None, None]:
            yield None

        result = flow(empty_stream())
        items = [item async for item in result]

        assert items == [0, 2, 4, 6]

    def test_from_iterable_sets_descriptive_name(self) -> None:
        """Test that from_iterable sets a descriptive flow name."""

        data = [1, 2, 3]
        flow = Flow.from_iterable(data)

        assert flow.name == "from_iterable"

    @pytest.mark.asyncio
    async def test_from_iterable_preserves_types(self) -> None:
        """Test that from_iterable preserves the type of items."""

        string_data = ["hello", "world"]
        string_flow = Flow.from_iterable(string_data)

        async def empty_stream() -> AsyncGenerator[None, None]:
            yield None

        result = string_flow(empty_stream())
        items = [item async for item in result]

        assert items == ["hello", "world"]
        assert all(isinstance(item, str) for item in items)

    @pytest.mark.asyncio
    async def test_from_iterable_with_dict_items(self) -> None:
        """Test that from_iterable works with dict items."""

        data = {"a": 1, "b": 2, "c": 3}
        flow = Flow.from_iterable(data.items())

        async def empty_stream() -> AsyncGenerator[None, None]:
            yield None

        result = flow(empty_stream())
        items = [item async for item in result]

        assert items == [("a", 1), ("b", 2), ("c", 3)]

    @pytest.mark.asyncio
    async def test_from_iterable_chaining_with_other_operations(self) -> None:
        """Test that flows from from_iterable can be chained."""

        data = [1, 2, 3, 4, 5]

        def is_even(x: int) -> bool:
            return x % 2 == 0

        def square(x: int) -> int:
            return x * x

        flow = Flow.from_iterable(data).filter(is_even).map(square)

        async def empty_stream() -> AsyncGenerator[None, None]:
            yield None

        result = flow(empty_stream())
        items = [item async for item in result]

        assert items == [4, 16]  # 2^2, 4^2

    @pytest.mark.asyncio
    async def test_from_iterable_ignores_input_stream(self) -> None:
        """Test that from_iterable ignores the input stream completely."""

        data = ["x", "y", "z"]
        flow = Flow.from_iterable(data)

        # Input stream with different data
        async def input_stream() -> AsyncGenerator[int, None]:
            for i in [100, 200, 300]:
                yield i

        result = flow(input_stream())
        items = [item async for item in result]

        # Should get the iterable data, not the input stream data
        assert items == ["x", "y", "z"]

    @pytest.mark.asyncio
    async def test_from_iterable_with_single_item(self) -> None:
        """Test that from_iterable works with single item iterables."""

        data = [42]
        flow = Flow.from_iterable(data)

        async def empty_stream() -> AsyncGenerator[None, None]:
            yield None

        result = flow(empty_stream())
        items = [item async for item in result]

        assert items == [42]

    @pytest.mark.asyncio
    async def test_from_iterable_multiple_input_calls(self) -> None:
        """Test that from_iterable produces the same output for multiple calls."""

        data = [10, 20, 30]
        flow = Flow.from_iterable(data)

        async def stream1() -> AsyncGenerator[None, None]:
            yield None

        async def stream2() -> AsyncGenerator[str, None]:
            yield "ignored"

        result1 = flow(stream1())
        items1 = [item async for item in result1]

        result2 = flow(stream2())
        items2 = [item async for item in result2]

        assert items1 == items2 == [10, 20, 30]
