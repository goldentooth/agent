"""Tests for transformation flow combinators: map_stream, flat_map_stream, flatten_stream."""

from __future__ import annotations

from typing import AsyncGenerator

import pytest

from flowengine.combinators.basic import flat_map_stream, flatten_stream, map_stream
from flowengine.flow import Flow

from .conftest import double, int_to_str, length_and_upper


class TestMapStream:
    """Test the map_stream function."""

    @pytest.mark.asyncio
    async def test_map_stream_basic(self) -> None:
        """Test map_stream with basic transformation."""

        async def source() -> AsyncGenerator[int, None]:
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

        async def source() -> AsyncGenerator[int, None]:
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

        async def empty_source() -> AsyncGenerator[int, None]:
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

        async def source() -> AsyncGenerator[str, None]:
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

        async def source() -> AsyncGenerator[str, None]:
            for word in ["ab", "cd"]:
                yield word

        async def split_chars(s: str) -> AsyncGenerator[str, None]:
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

        async def source() -> AsyncGenerator[int, None]:
            for i in [0, 2, 0, 3]:
                yield i

        async def range_generator(n: int) -> AsyncGenerator[int, None]:
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

        async def empty_source() -> AsyncGenerator[str, None]:
            return
            yield  # pragma: no cover

        async def split_chars(s: str) -> AsyncGenerator[str, None]:
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

        async def source() -> AsyncGenerator[int, None]:
            for n in [2, 3]:
                yield n

        async def repeat_number(n: int) -> AsyncGenerator[str, None]:
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

        async def explode_string(s: str) -> AsyncGenerator[str, None]:
            for char in s:
                yield char

        exploder = flat_map_stream(explode_string)
        assert "flat_map(explode_string)" in exploder.name


class TestFlattenStream:
    """Test the flatten_stream function."""

    @pytest.mark.asyncio
    async def test_flatten_stream_basic(self) -> None:
        """Test flatten_stream with basic nested generators."""

        async def sub_stream_1() -> AsyncGenerator[int, None]:
            for i in [1, 2]:
                yield i

        async def sub_stream_2() -> AsyncGenerator[int, None]:
            for i in [3, 4]:
                yield i

        async def source() -> AsyncGenerator[AsyncGenerator[int, None], None]:
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

        async def empty_stream() -> AsyncGenerator[int, None]:
            return
            yield  # pragma: no cover

        async def non_empty_stream() -> AsyncGenerator[int, None]:
            for i in [1, 2]:
                yield i

        async def source() -> AsyncGenerator[AsyncGenerator[int, None], None]:
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

        async def sub_stream() -> AsyncGenerator[int, None]:
            for i in [10, 20, 30]:
                yield i

        async def source() -> AsyncGenerator[AsyncGenerator[int, None], None]:
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

        async def empty_source() -> AsyncGenerator[AsyncGenerator[int, None], None]:
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
