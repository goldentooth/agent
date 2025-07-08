"""Tests for control flow combinators: take_stream, skip_stream, collect_stream, share_stream."""

from typing import AsyncGenerator

import pytest

from flowengine.combinators.basic import (
    collect_stream,
    share_stream,
    skip_stream,
    take_stream,
)
from flowengine.flow import Flow


class TestTakeStream:
    """Test the take_stream function."""

    @pytest.mark.asyncio
    async def test_take_stream_basic(self) -> None:
        """Test take_stream with basic functionality."""

        async def source() -> AsyncGenerator[int, None]:
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

        async def source() -> AsyncGenerator[int, None]:
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

        async def source() -> AsyncGenerator[int, None]:
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

        async def empty_source() -> AsyncGenerator[int, None]:
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

        async def source() -> AsyncGenerator[int, None]:
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

        async def source() -> AsyncGenerator[int, None]:
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

        async def source() -> AsyncGenerator[int, None]:
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

        async def empty_source() -> AsyncGenerator[int, None]:
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


class TestCollectStream:
    """Test the collect_stream function."""

    @pytest.mark.asyncio
    async def test_collect_stream_basic(self) -> None:
        """Test collect_stream with basic functionality."""

        async def source() -> AsyncGenerator[int, None]:
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

        async def empty_source() -> AsyncGenerator[int, None]:
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

        async def source() -> AsyncGenerator[int, None]:
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

        async def source() -> AsyncGenerator[str, None]:
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


class TestShareStream:
    """Test the share_stream function."""

    @pytest.mark.asyncio
    async def test_share_stream_basic(self) -> None:
        """Test share_stream basic functionality."""

        async def source() -> AsyncGenerator[int, None]:
            for i in [1, 2, 3]:
                yield i

        shared: Flow[int, int] = share_stream()
        result_stream = shared(source())
        results: list[int] = []
        async for item in result_stream:
            results.append(item)

        assert results == [1, 2, 3]

    def test_share_stream_name(self) -> None:
        """Test share_stream name."""

        shared: Flow[int, int] = share_stream()
        assert shared.name == "share"
