"""Tests for basic flow combinators."""

from __future__ import annotations

from typing import AsyncGenerator

import pytest

from flowengine.combinators.basic import (
    collect_stream,
    compose,
    filter_stream,
    flat_map_stream,
    flatten_stream,
    guard_stream,
    identity_stream,
    map_stream,
    run_fold,
    skip_stream,
    take_stream,
)
from flowengine.exceptions import FlowValidationError
from flowengine.flow import Flow


# Helper functions to replace lambdas and eliminate type: ignore comments
def increment(x: int) -> int:
    """Add 1 to the input."""
    return x + 1


def double(x: int) -> int:
    """Multiply input by 2."""
    return x * 2


def identity(x: int) -> int:
    """Return input unchanged."""
    return x


def int_to_str(x: int) -> str:
    """Convert integer to string."""
    return str(x)


def str_length(s: str) -> int:
    """Get length of string."""
    return len(s)


def is_even(x: int) -> bool:
    """Check if number is even."""
    return x % 2 == 0


def always_true(x: int) -> bool:
    """Always return True."""
    return True


def length_and_upper(s: str) -> str:
    """Transform string to UPPER:length format."""
    return f"{s.upper()}:{len(s)}"


def is_positive(x: int) -> bool:
    """Check if number is positive."""
    return x > 0


def is_non_zero(x: int) -> bool:
    """Check if number is non-zero."""
    return x != 0


class TestRunFold:
    """Test the run_fold function."""

    @pytest.mark.asyncio
    async def test_run_fold_empty_steps(self) -> None:
        """Test run_fold with empty steps list."""

        async def source():
            yield 1
            yield 2
            yield 3

        result_stream = await run_fold(source(), [])
        results: list[int] = []
        async for item in result_stream:
            results.append(item)

        assert results == [1, 2, 3]

    @pytest.mark.asyncio
    async def test_run_fold_single_step(self) -> None:
        """Test run_fold with a single step."""

        async def source():
            yield 1
            yield 2
            yield 3

        increment_flow = Flow.from_sync_fn(increment)
        result_stream = await run_fold(source(), [increment_flow])
        results: list[int] = []
        async for item in result_stream:
            results.append(item)

        assert results == [2, 3, 4]

    @pytest.mark.asyncio
    async def test_run_fold_multiple_steps(self) -> None:
        """Test run_fold with multiple steps."""

        async def source():
            yield 1
            yield 2
            yield 3

        increment_flow = Flow.from_sync_fn(increment)
        double_flow = Flow.from_sync_fn(double)
        result_stream = await run_fold(source(), [increment_flow, double_flow])
        results: list[int] = []
        async for item in result_stream:
            results.append(item)

        assert results == [4, 6, 8]  # (1+1)*2, (2+1)*2, (3+1)*2

    @pytest.mark.asyncio
    async def test_run_fold_empty_stream(self) -> None:
        """Test run_fold with empty input stream."""

        async def empty_source():
            return
            yield  # pragma: no cover

        increment_flow = Flow.from_sync_fn(increment)
        result_stream = await run_fold(empty_source(), [increment_flow])
        results: list[int] = []
        async for item in result_stream:
            results.append(item)

        assert results == []

    @pytest.mark.asyncio
    async def test_run_fold_identity_steps(self) -> None:
        """Test run_fold with identity flows."""

        async def source():
            yield 1
            yield 2
            yield 3

        identity_flow = Flow.from_sync_fn(identity)
        result_stream = await run_fold(source(), [identity_flow, identity_flow])
        results: list[int] = []
        async for item in result_stream:
            results.append(item)

        assert results == [1, 2, 3]


class TestCompose:
    """Test the compose function."""

    @pytest.mark.asyncio
    async def test_compose_two_flows(self) -> None:
        """Test composing two flows."""

        async def source():
            yield 1
            yield 2
            yield 3

        # First flow: add 1
        first_flow = Flow.from_sync_fn(increment)
        # Second flow: multiply by 2
        second_flow = Flow.from_sync_fn(double)

        # Compose: (x + 1) * 2
        composed_flow = compose(first_flow, second_flow)
        results: list[int] = []
        async for item in composed_flow(source()):
            results.append(item)

        assert results == [4, 6, 8]  # (1+1)*2, (2+1)*2, (3+1)*2

    @pytest.mark.asyncio
    async def test_compose_name_generation(self) -> None:
        """Test that compose generates appropriate names."""
        first_flow = Flow.from_sync_fn(increment)
        second_flow = Flow.from_sync_fn(double)

        # Set custom names
        first_flow.name = "add_one"
        second_flow.name = "double"

        composed_flow = compose(first_flow, second_flow)
        assert composed_flow.name == "add_one ∘ double"

    @pytest.mark.asyncio
    async def test_compose_empty_stream(self) -> None:
        """Test compose with empty input stream."""

        async def empty_source():
            return
            yield  # pragma: no cover

        first_flow = Flow.from_sync_fn(increment)
        second_flow = Flow.from_sync_fn(double)

        composed_flow = compose(first_flow, second_flow)
        results: list[int] = []
        async for item in composed_flow(empty_source()):
            results.append(item)

        assert results == []

    @pytest.mark.asyncio
    async def test_compose_identity_flows(self) -> None:
        """Test compose with identity flows."""

        async def source():
            yield 1
            yield 2
            yield 3

        identity_flow = Flow.from_sync_fn(identity)

        composed_flow = compose(identity_flow, identity_flow)
        results: list[int] = []
        async for item in composed_flow(source()):
            results.append(item)

        assert results == [1, 2, 3]

    @pytest.mark.asyncio
    async def test_compose_type_transformation(self) -> None:
        """Test compose with type transformation."""

        async def source():
            yield 1
            yield 2
            yield 3

        # First flow: int to string
        int_to_str_flow = Flow.from_sync_fn(int_to_str)
        # Second flow: string to length
        str_to_len_flow = Flow.from_sync_fn(str_length)

        composed_flow = compose(int_to_str_flow, str_to_len_flow)
        results: list[int] = []
        async for item in composed_flow(source()):
            results.append(item)

        assert results == [1, 1, 1]  # len("1"), len("2"), len("3")


class TestFilterStream:
    """Test the filter_stream function."""

    @pytest.mark.asyncio
    async def test_filter_stream_basic(self) -> None:
        """Test filter_stream with basic predicate."""

        async def source():
            for i in [1, 2, 3, 4, 5, 6]:
                yield i

        even_filter = filter_stream(is_even)
        result_stream = even_filter(source())
        results: list[int] = []
        async for item in result_stream:
            results.append(item)

        assert results == [2, 4, 6]

    @pytest.mark.asyncio
    async def test_filter_stream_empty_result(self) -> None:
        """Test filter_stream when no items match predicate."""

        async def source():
            for i in [1, 3, 5]:
                yield i

        even_filter = filter_stream(is_even)
        result_stream = even_filter(source())
        results: list[int] = []
        async for item in result_stream:
            results.append(item)

        assert results == []

    @pytest.mark.asyncio
    async def test_filter_stream_all_match(self) -> None:
        """Test filter_stream when all items match predicate."""

        async def source():
            for i in [2, 4, 6]:
                yield i

        even_filter = filter_stream(is_even)
        result_stream = even_filter(source())
        results: list[int] = []
        async for item in result_stream:
            results.append(item)

        assert results == [2, 4, 6]

    @pytest.mark.asyncio
    async def test_filter_stream_empty_input(self) -> None:
        """Test filter_stream with empty input stream."""

        async def empty_source():
            return
            yield  # pragma: no cover

        filter_flow = filter_stream(always_true)
        result_stream = filter_flow(empty_source())
        results: list[int] = []
        async for item in result_stream:
            results.append(item)

        assert results == []

    def test_filter_stream_name_generation(self) -> None:
        """Test that filter_stream generates appropriate names."""

        def is_positive(x: int) -> bool:
            return x > 0

        positive_filter = filter_stream(is_positive)
        assert "filter(is_positive)" in positive_filter.name


class TestMapStream:
    """Test the map_stream function."""

    @pytest.mark.asyncio
    async def test_map_stream_basic(self) -> None:
        """Test map_stream with basic transformation."""

        async def source():
            for i in [1, 2, 3]:
                yield i

        doubler = map_stream(double)
        result_stream = doubler(source())
        results: list[int] = []
        async for item in result_stream:
            results.append(item)

        assert results == [2, 4, 6]

    @pytest.mark.asyncio
    async def test_map_stream_type_transformation(self) -> None:
        """Test map_stream with type transformation."""

        async def source():
            for i in [1, 2, 3]:
                yield i

        int_to_str_flow = map_stream(int_to_str)
        result_stream = int_to_str_flow(source())
        results: list[str] = []
        async for item in result_stream:
            results.append(item)

        assert results == ["1", "2", "3"]

    @pytest.mark.asyncio
    async def test_map_stream_empty_input(self) -> None:
        """Test map_stream with empty input stream."""

        async def empty_source():
            return
            yield  # pragma: no cover

        doubler = map_stream(double)
        result_stream = doubler(empty_source())
        results: list[int] = []
        async for item in result_stream:
            results.append(item)

        assert results == []

    @pytest.mark.asyncio
    async def test_map_stream_complex_transformation(self) -> None:
        """Test map_stream with complex transformation."""

        async def source():
            for word in ["hello", "world", "test"]:
                yield word

        transformer = map_stream(length_and_upper)
        result_stream = transformer(source())
        results: list[str] = []
        async for item in result_stream:
            results.append(item)

        assert results == ["HELLO:5", "WORLD:5", "TEST:4"]

    def test_map_stream_name_generation(self) -> None:
        """Test that map_stream generates appropriate names."""

        def square(x: int) -> int:
            return x * x

        square_mapper = map_stream(square)
        assert "map(square)" in square_mapper.name


class TestFlatMapStream:
    """Test the flat_map_stream function."""

    @pytest.mark.asyncio
    async def test_flat_map_stream_basic(self) -> None:
        """Test flat_map_stream with basic character splitting."""

        async def source():
            for word in ["ab", "cd"]:
                yield word

        async def split_chars(s: str):
            for char in s:
                yield char

        char_splitter = flat_map_stream(split_chars)
        result_stream = char_splitter(source())
        results: list[str] = []
        async for item in result_stream:
            results.append(item)

        assert results == ["a", "b", "c", "d"]

    @pytest.mark.asyncio
    async def test_flat_map_stream_empty_sub_streams(self) -> None:
        """Test flat_map_stream when some sub-streams are empty."""

        async def source():
            for i in [0, 2, 0, 3]:
                yield i

        async def range_generator(n: int):
            for i in range(n):
                yield i

        range_flattener = flat_map_stream(range_generator)
        result_stream = range_flattener(source())
        results: list[int] = []
        async for item in result_stream:
            results.append(item)

        assert results == [
            0,
            1,
            0,
            1,
            2,
        ]  # range(0)=[], range(2)=[0,1], range(0)=[], range(3)=[0,1,2]

    @pytest.mark.asyncio
    async def test_flat_map_stream_empty_input(self) -> None:
        """Test flat_map_stream with empty input stream."""

        async def empty_source():
            return
            yield  # pragma: no cover

        async def split_chars(s: str):
            for char in s:
                yield char

        char_splitter = flat_map_stream(split_chars)
        result_stream = char_splitter(empty_source())
        results: list[str] = []
        async for item in result_stream:
            results.append(item)

        assert results == []

    @pytest.mark.asyncio
    async def test_flat_map_stream_type_transformation(self) -> None:
        """Test flat_map_stream with type transformation."""

        async def source():
            for n in [2, 3]:
                yield n

        async def repeat_number(n: int):
            for _ in range(n):
                yield str(n)  # int -> str transformation

        string_repeater = flat_map_stream(repeat_number)
        result_stream = string_repeater(source())
        results: list[str] = []
        async for item in result_stream:
            results.append(item)

        assert results == ["2", "2", "3", "3", "3"]

    def test_flat_map_stream_name_generation(self) -> None:
        """Test that flat_map_stream generates appropriate names."""

        async def explode_string(s: str):
            for char in s:
                yield char

        exploder = flat_map_stream(explode_string)
        assert "flat_map(explode_string)" in exploder.name


class TestIdentityStream:
    """Test the identity_stream function."""

    @pytest.mark.asyncio
    async def test_identity_stream_basic(self) -> None:
        """Test identity_stream passes through all items unchanged."""

        async def source():
            for i in [1, 2, 3, 4, 5]:
                yield i

        passthrough: Flow[int, int] = identity_stream()
        result_stream = passthrough(source())
        results: list[int] = []
        async for item in result_stream:
            results.append(item)

        assert results == [1, 2, 3, 4, 5]

    @pytest.mark.asyncio
    async def test_identity_stream_preserves_types(self) -> None:
        """Test identity_stream preserves different types."""

        async def source():
            for item in ["hello", "world", "test"]:
                yield item

        passthrough: Flow[str, str] = identity_stream()
        result_stream = passthrough(source())
        results: list[str] = []
        async for item in result_stream:
            results.append(item)

        assert results == ["hello", "world", "test"]

    @pytest.mark.asyncio
    async def test_identity_stream_empty_input(self) -> None:
        """Test identity_stream with empty input stream."""

        async def empty_source():
            return
            yield  # pragma: no cover

        passthrough: Flow[int, int] = identity_stream()
        result_stream = passthrough(empty_source())
        results: list[int] = []
        async for item in result_stream:
            results.append(item)

        assert results == []

    @pytest.mark.asyncio
    async def test_identity_stream_complex_objects(self) -> None:
        """Test identity_stream with complex objects."""
        from typing import Any

        async def source():
            for item in [{"key": "value"}, [1, 2, 3], ("a", "b")]:
                yield item

        passthrough: Flow[Any, Any] = identity_stream()
        result_stream = passthrough(source())
        results: list[Any] = []
        async for item in result_stream:
            results.append(item)

        assert results == [{"key": "value"}, [1, 2, 3], ("a", "b")]

    def test_identity_stream_name(self) -> None:
        """Test that identity_stream has correct name."""

        passthrough: Flow[int, int] = identity_stream()
        assert passthrough.name == "identity"


class TestTakeStream:
    """Test the take_stream function."""

    @pytest.mark.asyncio
    async def test_take_stream_basic(self) -> None:
        """Test take_stream with basic functionality."""

        async def source():
            for i in range(10):
                yield i

        take_three: Flow[int, int] = take_stream(3)
        result_stream = take_three(source())
        results: list[int] = []
        async for item in result_stream:
            results.append(item)

        assert results == [0, 1, 2]

    @pytest.mark.asyncio
    async def test_take_stream_more_than_available(self) -> None:
        """Test take_stream when n is greater than available items."""

        async def source():
            for i in [1, 2, 3]:
                yield i

        take_ten: Flow[int, int] = take_stream(10)
        result_stream = take_ten(source())
        results: list[int] = []
        async for item in result_stream:
            results.append(item)

        assert results == [1, 2, 3]

    @pytest.mark.asyncio
    async def test_take_stream_zero_items(self) -> None:
        """Test take_stream with n=0."""

        async def source():
            for i in [1, 2, 3]:
                yield i

        take_zero: Flow[int, int] = take_stream(0)
        result_stream = take_zero(source())
        results: list[int] = []
        async for item in result_stream:
            results.append(item)

        assert results == []

    @pytest.mark.asyncio
    async def test_take_stream_empty_input(self) -> None:
        """Test take_stream with empty input stream."""

        async def empty_source():
            return
            yield  # pragma: no cover

        take_five: Flow[int, int] = take_stream(5)
        result_stream = take_five(empty_source())
        results: list[int] = []
        async for item in result_stream:
            results.append(item)

        assert results == []

    def test_take_stream_name_generation(self) -> None:
        """Test that take_stream generates appropriate names."""

        take_five: Flow[int, int] = take_stream(5)
        assert take_five.name == "take(5)"

        take_zero: Flow[int, int] = take_stream(0)
        assert take_zero.name == "take(0)"


class TestSkipStream:
    """Test the skip_stream function."""

    @pytest.mark.asyncio
    async def test_skip_stream_basic(self) -> None:
        """Test skip_stream with basic functionality."""

        async def source():
            for i in range(10):
                yield i

        skip_three: Flow[int, int] = skip_stream(3)
        result_stream = skip_three(source())
        results: list[int] = []
        async for item in result_stream:
            results.append(item)

        assert results == [3, 4, 5, 6, 7, 8, 9]

    @pytest.mark.asyncio
    async def test_skip_stream_more_than_available(self) -> None:
        """Test skip_stream when n is greater than available items."""

        async def source():
            for i in [1, 2, 3]:
                yield i

        skip_ten: Flow[int, int] = skip_stream(10)
        result_stream = skip_ten(source())
        results: list[int] = []
        async for item in result_stream:
            results.append(item)

        assert results == []

    @pytest.mark.asyncio
    async def test_skip_stream_zero_items(self) -> None:
        """Test skip_stream with n=0 (skip nothing)."""

        async def source():
            for i in [1, 2, 3]:
                yield i

        skip_zero: Flow[int, int] = skip_stream(0)
        result_stream = skip_zero(source())
        results: list[int] = []
        async for item in result_stream:
            results.append(item)

        assert results == [1, 2, 3]

    @pytest.mark.asyncio
    async def test_skip_stream_empty_input(self) -> None:
        """Test skip_stream with empty input stream."""

        async def empty_source():
            return
            yield  # pragma: no cover

        skip_five: Flow[int, int] = skip_stream(5)
        result_stream = skip_five(empty_source())
        results: list[int] = []
        async for item in result_stream:
            results.append(item)

        assert results == []

    def test_skip_stream_name_generation(self) -> None:
        """Test that skip_stream generates appropriate names."""

        skip_five: Flow[int, int] = skip_stream(5)
        assert skip_five.name == "skip(5)"

        skip_zero: Flow[int, int] = skip_stream(0)
        assert skip_zero.name == "skip(0)"


class TestGuardStream:
    """Test the guard_stream function."""

    @pytest.mark.asyncio
    async def test_guard_stream_all_pass(self) -> None:
        """Test guard_stream when all items pass validation."""

        async def source():
            for i in [1, 2, 3, 4, 5]:
                yield i

        positive_guard: Flow[int, int] = guard_stream(is_positive, "Must be positive")
        result_stream = positive_guard(source())
        results: list[int] = []
        async for item in result_stream:
            results.append(item)

        assert results == [1, 2, 3, 4, 5]

    @pytest.mark.asyncio
    async def test_guard_stream_validation_failure(self) -> None:
        """Test guard_stream when validation fails."""

        async def source():
            for i in [1, 2, -1, 4]:
                yield i

        positive_guard: Flow[int, int] = guard_stream(is_positive, "Must be positive")
        result_stream = positive_guard(source())
        results: list[int] = []

        with pytest.raises(FlowValidationError, match="Must be positive: -1"):
            async for item in result_stream:
                results.append(item)

        # Should have processed items before failure
        assert results == [1, 2]

    @pytest.mark.asyncio
    async def test_guard_stream_first_item_fails(self) -> None:
        """Test guard_stream when first item fails validation."""

        async def source():
            for i in [-5, 1, 2, 3]:
                yield i

        positive_guard: Flow[int, int] = guard_stream(is_positive, "Must be positive")
        result_stream = positive_guard(source())
        results: list[int] = []

        with pytest.raises(FlowValidationError, match="Must be positive: -5"):
            async for item in result_stream:
                results.append(item)

        # Should have processed no items
        assert results == []

    @pytest.mark.asyncio
    async def test_guard_stream_empty_input(self) -> None:
        """Test guard_stream with empty input stream."""

        async def empty_source():
            return
            yield  # pragma: no cover

        positive_guard: Flow[int, int] = guard_stream(is_positive, "Must be positive")
        result_stream = positive_guard(empty_source())
        results: list[int] = []
        async for item in result_stream:
            results.append(item)

        assert results == []

    def test_guard_stream_name_generation(self) -> None:
        """Test that guard_stream generates appropriate names."""

        positive_guard: Flow[int, int] = guard_stream(is_positive, "Must be positive")
        assert "guard(is_positive)" in positive_guard.name

        non_zero_guard: Flow[int, int] = guard_stream(is_non_zero, "Must be non-zero")
        assert "guard(is_non_zero)" in non_zero_guard.name


class TestFlattenStream:
    """Test the flatten_stream function."""

    @pytest.mark.asyncio
    async def test_flatten_stream_basic(self) -> None:
        """Test flatten_stream with basic nested generators."""

        async def sub_stream_1():
            for i in [1, 2]:
                yield i

        async def sub_stream_2():
            for i in [3, 4]:
                yield i

        async def source():
            yield sub_stream_1()
            yield sub_stream_2()

        flattener: Flow[AsyncGenerator[int, None], int] = flatten_stream()
        result_stream = flattener(source())
        results: list[int] = []
        async for item in result_stream:
            results.append(item)

        assert results == [1, 2, 3, 4]

    @pytest.mark.asyncio
    async def test_flatten_stream_empty_sub_streams(self) -> None:
        """Test flatten_stream with some empty sub-streams."""

        async def empty_stream():
            return
            yield  # pragma: no cover

        async def non_empty_stream():
            for i in [1, 2]:
                yield i

        async def source():
            yield empty_stream()
            yield non_empty_stream()
            yield empty_stream()

        flattener: Flow[AsyncGenerator[int, None], int] = flatten_stream()
        result_stream = flattener(source())
        results: list[int] = []
        async for item in result_stream:
            results.append(item)

        assert results == [1, 2]

    @pytest.mark.asyncio
    async def test_flatten_stream_single_sub_stream(self) -> None:
        """Test flatten_stream with single sub-stream."""

        async def sub_stream():
            for i in [10, 20, 30]:
                yield i

        async def source():
            yield sub_stream()

        flattener: Flow[AsyncGenerator[int, None], int] = flatten_stream()
        result_stream = flattener(source())
        results: list[int] = []
        async for item in result_stream:
            results.append(item)

        assert results == [10, 20, 30]

    @pytest.mark.asyncio
    async def test_flatten_stream_empty_input(self) -> None:
        """Test flatten_stream with empty input stream."""

        async def empty_source():
            return
            yield  # pragma: no cover

        flattener: Flow[AsyncGenerator[int, None], int] = flatten_stream()
        result_stream = flattener(empty_source())
        results: list[int] = []
        async for item in result_stream:
            results.append(item)

        assert results == []

    def test_flatten_stream_name(self) -> None:
        """Test that flatten_stream has correct name."""

        flattener: Flow[AsyncGenerator[int, None], int] = flatten_stream()
        assert flattener.name == "flatten"


class TestCollectStream:
    """Test the collect_stream function."""

    @pytest.mark.asyncio
    async def test_collect_stream_basic(self) -> None:
        """Test collect_stream with basic functionality."""

        async def source():
            for i in [1, 2, 3, 4, 5]:
                yield i

        collector: Flow[int, list[int]] = collect_stream()
        result_stream = collector(source())
        results: list[list[int]] = []
        async for item in result_stream:
            results.append(item)

        assert len(results) == 1
        assert results[0] == [1, 2, 3, 4, 5]

    @pytest.mark.asyncio
    async def test_collect_stream_empty_input(self) -> None:
        """Test collect_stream with empty input stream."""

        async def empty_source():
            return
            yield  # pragma: no cover

        collector: Flow[int, list[int]] = collect_stream()
        result_stream = collector(empty_source())
        results: list[list[int]] = []
        async for item in result_stream:
            results.append(item)

        assert len(results) == 1
        assert results[0] == []

    @pytest.mark.asyncio
    async def test_collect_stream_single_item(self) -> None:
        """Test collect_stream with single item."""

        async def source():
            yield 42

        collector: Flow[int, list[int]] = collect_stream()
        result_stream = collector(source())
        results: list[list[int]] = []
        async for item in result_stream:
            results.append(item)

        assert len(results) == 1
        assert results[0] == [42]

    @pytest.mark.asyncio
    async def test_collect_stream_different_types(self) -> None:
        """Test collect_stream with different data types."""

        async def source():
            for item in ["hello", "world", "test"]:
                yield item

        collector: Flow[str, list[str]] = collect_stream()
        result_stream = collector(source())
        results: list[list[str]] = []
        async for item in result_stream:
            results.append(item)

        assert len(results) == 1
        assert results[0] == ["hello", "world", "test"]

    def test_collect_stream_name(self) -> None:
        """Test that collect_stream has correct name."""

        collector: Flow[int, list[int]] = collect_stream()
        assert collector.name == "collect"
