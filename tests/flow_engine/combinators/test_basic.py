"""Tests for basic flow combinators."""

from collections.abc import AsyncIterator

import pytest

from goldentooth_agent.flow_engine.combinators.basic import (
    collect_stream,
    compose,
    filter_stream,
    flat_map_stream,
    flatten_stream,
    guard_stream,
    identity_stream,
    map_stream,
    run_fold,
    share_stream,
    skip_stream,
    take_stream,
    until_stream,
)
from goldentooth_agent.flow_engine.exceptions import FlowValidationError


# Helper functions
def increment(x: int) -> int:
    """Increment a number by 1."""
    return x + 1


def double(x: int) -> int:
    """Double a number."""
    return x * 2


def is_even(x: int) -> bool:
    """Check if a number is even."""
    return x % 2 == 0


async def async_range(n: int) -> AsyncIterator[int]:
    """Generate an async range of integers."""
    for i in range(n):
        yield i


async def duplicate_items(x: int) -> AsyncIterator[int]:
    """Duplicate each item."""
    yield x
    yield x


async def repeat_n_times(x: int, n: int = 3) -> AsyncIterator[int]:
    """Repeat each item n times."""
    for _ in range(n):
        yield x


class TestRunFold:
    """Tests for run_fold function."""

    @pytest.mark.asyncio
    async def test_run_fold_empty_list(self):
        """Test run_fold with empty flow list."""
        input_stream = async_range(3)
        result_stream = await run_fold(input_stream, [])
        values = [item async for item in result_stream]
        assert values == [0, 1, 2]

    @pytest.mark.asyncio
    async def test_run_fold_single_flow(self):
        """Test run_fold with single flow."""
        input_stream = async_range(3)
        increment_flow = map_stream(increment)
        result_stream = await run_fold(input_stream, [increment_flow])
        values = [item async for item in result_stream]
        assert values == [1, 2, 3]

    @pytest.mark.asyncio
    async def test_run_fold_multiple_flows(self):
        """Test run_fold with multiple flows."""
        input_stream = async_range(3)
        increment_flow = map_stream(increment)
        double_flow = map_stream(double)
        result_stream = await run_fold(input_stream, [increment_flow, double_flow])
        values = [item async for item in result_stream]
        assert values == [2, 4, 6]  # (0+1)*2, (1+1)*2, (2+1)*2


class TestCompose:
    """Tests for compose function."""

    @pytest.mark.asyncio
    async def test_compose_basic(self):
        """Test basic flow composition."""
        increment_flow = map_stream(increment)
        double_flow = map_stream(double)
        composed = compose(increment_flow, double_flow)

        assert "map(increment) ∘ map(double)" in composed.name

        input_stream = async_range(3)
        result_stream = composed(input_stream)
        values = [item async for item in result_stream]
        assert values == [2, 4, 6]

    @pytest.mark.asyncio
    async def test_compose_type_transformation(self):
        """Test composition with type transformation."""
        double_flow = map_stream(double)
        to_string_flow = map_stream(str)
        composed = compose(double_flow, to_string_flow)

        input_stream = async_range(3)
        result_stream = composed(input_stream)
        values = [item async for item in result_stream]
        assert values == ["0", "2", "4"]


class TestFilterStream:
    """Tests for filter_stream function."""

    @pytest.mark.asyncio
    async def test_filter_basic(self):
        """Test basic filtering."""
        filter_flow = filter_stream(is_even)
        assert "filter(is_even)" in filter_flow.name

        input_stream = async_range(5)
        result_stream = filter_flow(input_stream)
        values = [item async for item in result_stream]
        assert values == [0, 2, 4]

    @pytest.mark.asyncio
    async def test_filter_with_lambda(self):
        """Test filtering with lambda."""
        filter_flow = filter_stream(lambda x: x > 2)
        input_stream = async_range(5)
        result_stream = filter_flow(input_stream)
        values = [item async for item in result_stream]
        assert values == [3, 4]

    @pytest.mark.asyncio
    async def test_filter_no_matches(self):
        """Test filtering with no matches."""
        filter_flow = filter_stream(lambda x: x > 10)
        input_stream = async_range(5)
        result_stream = filter_flow(input_stream)
        values = [item async for item in result_stream]
        assert values == []

    @pytest.mark.asyncio
    async def test_filter_all_match(self):
        """Test filtering where all items match."""
        filter_flow = filter_stream(lambda x: x < 10)
        input_stream = async_range(5)
        result_stream = filter_flow(input_stream)
        values = [item async for item in result_stream]
        assert values == [0, 1, 2, 3, 4]


class TestMapStream:
    """Tests for map_stream function."""

    @pytest.mark.asyncio
    async def test_map_basic(self):
        """Test basic mapping."""
        map_flow = map_stream(increment)
        assert "map(increment)" in map_flow.name

        input_stream = async_range(3)
        result_stream = map_flow(input_stream)
        values = [item async for item in result_stream]
        assert values == [1, 2, 3]

    @pytest.mark.asyncio
    async def test_map_with_lambda(self):
        """Test mapping with lambda."""
        map_flow = map_stream(lambda x: x * 3)
        input_stream = async_range(3)
        result_stream = map_flow(input_stream)
        values = [item async for item in result_stream]
        assert values == [0, 3, 6]

    @pytest.mark.asyncio
    async def test_map_type_transformation(self):
        """Test mapping with type transformation."""
        map_flow = map_stream(str)
        input_stream = async_range(3)
        result_stream = map_flow(input_stream)
        values = [item async for item in result_stream]
        assert values == ["0", "1", "2"]

    @pytest.mark.asyncio
    async def test_map_empty_stream(self):
        """Test mapping on empty stream."""
        map_flow = map_stream(increment)

        async def empty_stream() -> AsyncIterator[int]:
            if False:
                yield 0

        result_stream = map_flow(empty_stream())
        values = [item async for item in result_stream]
        assert values == []


class TestFlatMapStream:
    """Tests for flat_map_stream function."""

    @pytest.mark.asyncio
    async def test_flat_map_basic(self):
        """Test basic flat mapping."""
        flat_map_flow = flat_map_stream(duplicate_items)
        assert "flat_map(duplicate_items)" in flat_map_flow.name

        input_stream = async_range(3)
        result_stream = flat_map_flow(input_stream)
        values = [item async for item in result_stream]
        assert values == [0, 0, 1, 1, 2, 2]

    @pytest.mark.asyncio
    async def test_flat_map_repeat(self):
        """Test flat mapping with repetition."""
        flat_map_flow = flat_map_stream(lambda x: repeat_n_times(x, 3))
        input_stream = async_range(2)
        result_stream = flat_map_flow(input_stream)
        values = [item async for item in result_stream]
        assert values == [0, 0, 0, 1, 1, 1]

    @pytest.mark.asyncio
    async def test_flat_map_empty_results(self):
        """Test flat mapping that produces empty results."""

        async def empty_generator(_: int) -> AsyncIterator[int]:
            if False:
                yield 0

        flat_map_flow = flat_map_stream(empty_generator)
        input_stream = async_range(3)
        result_stream = flat_map_flow(input_stream)
        values = [item async for item in result_stream]
        assert values == []


class TestIdentityStream:
    """Tests for identity_stream function."""

    @pytest.mark.asyncio
    async def test_identity_basic(self):
        """Test basic identity stream."""
        identity_flow = identity_stream()
        assert identity_flow.name == "identity"

        input_stream = async_range(3)
        result_stream = identity_flow(input_stream)
        values = [item async for item in result_stream]
        assert values == [0, 1, 2]

    @pytest.mark.asyncio
    async def test_identity_with_complex_objects(self):
        """Test identity stream with complex objects."""
        identity_flow = identity_stream()

        async def complex_stream() -> AsyncIterator[dict]:
            yield {"a": 1}
            yield {"b": 2}

        result_stream = identity_flow(complex_stream())
        values = [item async for item in result_stream]
        assert values == [{"a": 1}, {"b": 2}]


class TestTakeStream:
    """Tests for take_stream function."""

    @pytest.mark.asyncio
    async def test_take_basic(self):
        """Test basic take functionality."""
        take_flow = take_stream(3)
        assert "take(3)" in take_flow.name

        input_stream = async_range(5)
        result_stream = take_flow(input_stream)
        values = [item async for item in result_stream]
        assert values == [0, 1, 2]

    @pytest.mark.asyncio
    async def test_take_more_than_available(self):
        """Test taking more items than available."""
        take_flow = take_stream(10)
        input_stream = async_range(3)
        result_stream = take_flow(input_stream)
        values = [item async for item in result_stream]
        assert values == [0, 1, 2]

    @pytest.mark.asyncio
    async def test_take_zero(self):
        """Test taking zero items."""
        take_flow = take_stream(0)
        input_stream = async_range(5)
        result_stream = take_flow(input_stream)
        values = [item async for item in result_stream]
        assert values == []


class TestSkipStream:
    """Tests for skip_stream function."""

    @pytest.mark.asyncio
    async def test_skip_basic(self):
        """Test basic skip functionality."""
        skip_flow = skip_stream(2)
        assert "skip(2)" in skip_flow.name

        input_stream = async_range(5)
        result_stream = skip_flow(input_stream)
        values = [item async for item in result_stream]
        assert values == [2, 3, 4]

    @pytest.mark.asyncio
    async def test_skip_more_than_available(self):
        """Test skipping more items than available."""
        skip_flow = skip_stream(10)
        input_stream = async_range(3)
        result_stream = skip_flow(input_stream)
        values = [item async for item in result_stream]
        assert values == []

    @pytest.mark.asyncio
    async def test_skip_zero(self):
        """Test skipping zero items."""
        skip_flow = skip_stream(0)
        input_stream = async_range(3)
        result_stream = skip_flow(input_stream)
        values = [item async for item in result_stream]
        assert values == [0, 1, 2]


class TestGuardStream:
    """Tests for guard_stream function."""

    @pytest.mark.asyncio
    async def test_guard_stream_valid(self):
        """Test guard stream with valid items."""
        guard_flow = guard_stream(lambda x: x >= 0, "Value must be non-negative")
        assert "guard(<lambda>)" in guard_flow.name

        input_stream = async_range(3)
        result_stream = guard_flow(input_stream)
        values = [item async for item in result_stream]
        assert values == [0, 1, 2]

    @pytest.mark.asyncio
    async def test_guard_stream_invalid(self):
        """Test guard stream with invalid items."""
        guard_flow = guard_stream(lambda x: x < 2, "Value must be less than 2")

        async def stream_with_invalid() -> AsyncIterator[int]:
            yield 0
            yield 1
            yield 2  # This will fail the guard

        with pytest.raises(FlowValidationError) as exc_info:
            result_stream = guard_flow(stream_with_invalid())
            _ = [item async for item in result_stream]

        assert "Value must be less than 2: 2" in str(exc_info.value)


class TestFlattenStream:
    """Tests for flatten_stream function."""

    @pytest.mark.asyncio
    async def test_flatten_basic(self):
        """Test basic flatten functionality."""
        flatten_flow = flatten_stream()
        assert flatten_flow.name == "flatten"

        async def nested_stream() -> AsyncIterator[AsyncIterator[int]]:
            yield async_range(2)
            yield async_range(3)

        result_stream = flatten_flow(nested_stream())
        values = [item async for item in result_stream]
        assert values == [0, 1, 0, 1, 2]

    @pytest.mark.asyncio
    async def test_flatten_empty_sub_streams(self):
        """Test flattening with empty sub-streams."""
        flatten_flow = flatten_stream()

        async def empty_async_iter() -> AsyncIterator[int]:
            if False:
                yield 0

        async def nested_with_empty() -> AsyncIterator[AsyncIterator[int]]:
            yield async_range(2)
            yield empty_async_iter()
            yield async_range(1)

        result_stream = flatten_flow(nested_with_empty())
        values = [item async for item in result_stream]
        assert values == [0, 1, 0]


class TestCollectStream:
    """Tests for collect_stream function."""

    @pytest.mark.asyncio
    async def test_collect_basic(self):
        """Test basic collect functionality."""
        collect_flow = collect_stream()
        assert collect_flow.name == "collect"

        input_stream = async_range(3)
        result_stream = collect_flow(input_stream)
        values = [item async for item in result_stream]
        assert values == [[0, 1, 2]]

    @pytest.mark.asyncio
    async def test_collect_empty_stream(self):
        """Test collecting empty stream."""
        collect_flow = collect_stream()

        async def empty_stream() -> AsyncIterator[int]:
            if False:
                yield 0

        result_stream = collect_flow(empty_stream())
        values = [item async for item in result_stream]
        assert values == [[]]


class TestUntilStream:
    """Tests for until_stream function."""

    @pytest.mark.asyncio
    async def test_until_stream_basic(self):
        """Test basic until functionality."""
        until_flow = until_stream(lambda x: x == 2)
        assert "until(<lambda>)" in until_flow.name

        input_stream = async_range(5)
        result_stream = until_flow(input_stream)
        values = [item async for item in result_stream]
        assert values == [0, 1, 2]  # Includes the item that matches

    @pytest.mark.asyncio
    async def test_until_stream_no_match(self):
        """Test until stream when predicate never matches."""
        until_flow = until_stream(lambda x: x == 10)
        input_stream = async_range(3)
        result_stream = until_flow(input_stream)
        values = [item async for item in result_stream]
        assert values == [0, 1, 2]

    @pytest.mark.asyncio
    async def test_until_stream_immediate_match(self):
        """Test until stream when first item matches."""
        until_flow = until_stream(lambda x: x == 0)
        input_stream = async_range(3)
        result_stream = until_flow(input_stream)
        values = [item async for item in result_stream]
        assert values == [0]


class TestShareStream:
    """Tests for share_stream function."""

    @pytest.mark.asyncio
    async def test_share_basic(self):
        """Test basic share functionality."""
        share_flow = share_stream()
        assert share_flow.name == "share"

        # Note: This is a simplified test since the current implementation
        # doesn't actually implement subscription sharing
        input_stream = async_range(3)
        result_stream = share_flow(input_stream)
        values = [item async for item in result_stream]
        assert values == [0, 1, 2]
