from __future__ import annotations

from typing import AsyncGenerator

import pytest

from flowengine.flow import Flow


class TestFlowIdentity:
    """Tests for Flow.identity static method."""

    @pytest.mark.asyncio
    async def test_identity_passes_through_all_items(self) -> None:
        """Test that identity flow passes through all items unchanged."""

        flow: Flow[str, str] = Flow.identity()

        async def string_stream() -> AsyncGenerator[str, None]:
            yield "hello"
            yield "world"
            yield "test"

        result = flow(string_stream())
        items: list[str] = [item async for item in result]

        assert items == ["hello", "world", "test"]

    @pytest.mark.asyncio
    async def test_identity_preserves_types(self) -> None:
        """Test that identity flow preserves the type of items."""

        int_flow: Flow[int, int] = Flow.identity()

        async def int_stream() -> AsyncGenerator[int, None]:
            yield 42
            yield 99
            yield 123

        result = int_flow(int_stream())
        items: list[int] = [item async for item in result]

        assert items == [42, 99, 123]
        assert all(isinstance(item, int) for item in items)

    @pytest.mark.asyncio
    async def test_identity_with_empty_stream(self) -> None:
        """Test that identity flow works with empty streams."""

        flow: Flow[str, str] = Flow.identity()

        async def empty_stream() -> AsyncGenerator[str, None]:
            return
            yield  # pragma: no cover

        result = flow(empty_stream())
        items: list[str] = [item async for item in result]

        assert items == []

    @pytest.mark.asyncio
    async def test_identity_with_single_item(self) -> None:
        """Test that identity flow works with single item streams."""

        flow: Flow[int, int] = Flow.identity()

        async def single_stream() -> AsyncGenerator[int, None]:
            yield 42

        result = flow(single_stream())
        items: list[int] = [item async for item in result]

        assert items == [42]

    def test_identity_sets_descriptive_name(self) -> None:
        """Test that identity flow sets a descriptive flow name."""

        flow: Flow[str, str] = Flow.identity()

        assert flow.name == "identity"

    @pytest.mark.asyncio
    async def test_identity_with_complex_types(self) -> None:
        """Test that identity flow works with complex data types."""

        flow: Flow[dict[str, int], dict[str, int]] = Flow.identity()

        async def dict_stream() -> AsyncGenerator[dict[str, int], None]:
            yield {"a": 1, "b": 2}
            yield {"x": 10, "y": 20}

        result = flow(dict_stream())
        items: list[dict[str, int]] = [item async for item in result]

        assert items == [{"a": 1, "b": 2}, {"x": 10, "y": 20}]

    @pytest.mark.asyncio
    async def test_identity_chaining_with_other_operations(self) -> None:
        """Test that identity flow can be chained with other operations."""

        def is_even(x: int) -> bool:
            return x % 2 == 0

        def square(x: int) -> int:
            return x * x

        # Chain identity with filter and map
        identity_flow: Flow[int, int] = Flow.identity()
        flow = identity_flow.filter(is_even).map(square)

        async def int_stream() -> AsyncGenerator[int, None]:
            for i in [1, 2, 3, 4, 5]:
                yield i

        result = flow(int_stream())
        items: list[int] = [item async for item in result]

        assert items == [4, 16]  # 2^2, 4^2

    @pytest.mark.asyncio
    async def test_identity_preserves_order(self) -> None:
        """Test that identity flow preserves the order of items."""

        flow: Flow[int, int] = Flow.identity()

        async def sequence_stream() -> AsyncGenerator[int, None]:
            for i in [3, 1, 4, 1, 5, 9, 2, 6]:
                yield i

        result = flow(sequence_stream())
        items: list[int] = [item async for item in result]

        assert items == [3, 1, 4, 1, 5, 9, 2, 6]

    @pytest.mark.asyncio
    async def test_identity_with_none_values(self) -> None:
        """Test that identity flow handles None values correctly."""

        flow: Flow[str | None, str | None] = Flow.identity()

        async def mixed_stream() -> AsyncGenerator[str | None, None]:
            yield "hello"
            yield None
            yield "world"
            yield None

        result = flow(mixed_stream())
        items: list[str | None] = [item async for item in result]

        assert items == ["hello", None, "world", None]

    @pytest.mark.asyncio
    async def test_identity_composition_with_itself(self) -> None:
        """Test that identity composed with itself is still identity."""

        flow1: Flow[int, int] = Flow.identity()
        flow2: Flow[int, int] = Flow.identity()
        composed = flow1 >> flow2

        async def int_stream() -> AsyncGenerator[int, None]:
            for i in [10, 20, 30]:
                yield i

        result = composed(int_stream())
        items: list[int] = [item async for item in result]

        assert items == [10, 20, 30]

    @pytest.mark.asyncio
    async def test_identity_as_left_identity_in_composition(self) -> None:
        """Test that identity acts as left identity in flow composition."""

        def double(x: int) -> int:
            return x * 2

        identity_flow: Flow[int, int] = Flow.identity()
        double_flow = Flow.from_sync_fn(double)

        # identity >> f should be equivalent to f
        composed = identity_flow >> double_flow

        async def int_stream() -> AsyncGenerator[int, None]:
            for i in [1, 2, 3]:
                yield i

        result1 = composed(int_stream())
        items1: list[int] = [item async for item in result1]

        async def int_stream2() -> AsyncGenerator[int, None]:
            for i in [1, 2, 3]:
                yield i

        result2 = double_flow(int_stream2())
        items2: list[int] = [item async for item in result2]

        assert items1 == items2 == [2, 4, 6]

    @pytest.mark.asyncio
    async def test_identity_as_right_identity_in_composition(self) -> None:
        """Test that identity acts as right identity in flow composition."""

        def triple(x: int) -> int:
            return x * 3

        triple_flow = Flow.from_sync_fn(triple)
        identity_flow: Flow[int, int] = Flow.identity()

        # f >> identity should be equivalent to f
        composed = triple_flow >> identity_flow

        async def int_stream() -> AsyncGenerator[int, None]:
            for i in [1, 2, 3]:
                yield i

        result1 = composed(int_stream())
        items1: list[int] = [item async for item in result1]

        async def int_stream2() -> AsyncGenerator[int, None]:
            for i in [1, 2, 3]:
                yield i

        result2 = triple_flow(int_stream2())
        items2: list[int] = [item async for item in result2]

        assert items1 == items2 == [3, 6, 9]
