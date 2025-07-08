"""Tests for filtering flow combinators: filter_stream, guard_stream, until_stream."""

from typing import AsyncGenerator

import pytest

from flowengine.combinators.basic import filter_stream, guard_stream, until_stream
from flowengine.exceptions import FlowValidationError
from flowengine.flow import Flow

from .conftest import always_true, equals_five, is_even, is_non_zero, is_positive


class TestFilterStream:
    """Test the filter_stream function."""

    @pytest.mark.asyncio
    async def test_filter_stream_basic(self) -> None:
        """Test filter_stream with basic predicate."""

        async def source() -> AsyncGenerator[int, None]:
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

        async def source() -> AsyncGenerator[int, None]:
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

        async def source() -> AsyncGenerator[int, None]:
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

        async def empty_source() -> AsyncGenerator[int, None]:
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


class TestGuardStream:
    """Test the guard_stream function."""

    @pytest.mark.asyncio
    async def test_guard_stream_all_pass(self) -> None:
        """Test guard_stream when all items pass validation."""

        async def source() -> AsyncGenerator[int, None]:
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

        async def source() -> AsyncGenerator[int, None]:
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

        async def source() -> AsyncGenerator[int, None]:
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

        async def empty_source() -> AsyncGenerator[int, None]:
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


class TestUntilStream:
    """Test the until_stream function."""

    @pytest.mark.asyncio
    async def test_until_stream_stops_at_match(self) -> None:
        """Test until_stream stops when predicate matches."""

        async def source() -> AsyncGenerator[int, None]:
            for i in [1, 2, 3, 5, 6, 7]:
                yield i

        until_five: Flow[int, int] = until_stream(equals_five)
        result_stream = until_five(source())
        results: list[int] = []
        async for item in result_stream:
            results.append(item)

        assert results == [1, 2, 3, 5]  # Includes the matching item

    @pytest.mark.asyncio
    async def test_until_stream_no_match(self) -> None:
        """Test until_stream when predicate never matches."""

        async def source() -> AsyncGenerator[int, None]:
            for i in [1, 2, 3, 4]:
                yield i

        until_five: Flow[int, int] = until_stream(equals_five)
        result_stream = until_five(source())
        results: list[int] = []
        async for item in result_stream:
            results.append(item)

        assert results == [1, 2, 3, 4]

    @pytest.mark.asyncio
    async def test_until_stream_first_item_matches(self) -> None:
        """Test until_stream when first item matches."""

        async def source() -> AsyncGenerator[int, None]:
            for i in [5, 1, 2, 3]:
                yield i

        until_five: Flow[int, int] = until_stream(equals_five)
        result_stream = until_five(source())
        results: list[int] = []
        async for item in result_stream:
            results.append(item)

        assert results == [5]

    def test_until_stream_name_generation(self) -> None:
        """Test that until_stream generates appropriate names."""

        until_five: Flow[int, int] = until_stream(equals_five)
        assert "until(equals_five)" in until_five.name
