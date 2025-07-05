from __future__ import annotations

from typing import Any, AsyncGenerator

import pytest

from flowengine.flow import Flow


class TestFlowPure:
    """Tests for Flow.pure static method."""

    @pytest.mark.asyncio
    async def test_pure_yields_single_value(self) -> None:
        """Test that pure flow yields the specified value once."""

        flow: Flow[Any, str] = Flow.pure("hello")

        async def any_stream() -> AsyncGenerator[int, None]:
            yield 1
            yield 2
            yield 3

        result = flow(any_stream())
        items: list[str] = [item async for item in result]

        assert items == ["hello"]

    @pytest.mark.asyncio
    async def test_pure_ignores_input_stream(self) -> None:
        """Test that pure flow ignores the input stream completely."""

        flow: Flow[Any, int] = Flow.pure(42)

        # Test with different input streams
        async def string_stream() -> AsyncGenerator[str, None]:
            yield "ignored"
            yield "completely"

        async def empty_stream() -> AsyncGenerator[None, None]:
            return
            yield  # pragma: no cover

        async def large_stream() -> AsyncGenerator[int, None]:
            for i in range(1000):
                yield i

        # All should yield the same single value
        result1 = flow(string_stream())
        items1: list[int] = [item async for item in result1]

        result2 = flow(empty_stream())
        items2: list[int] = [item async for item in result2]

        result3 = flow(large_stream())
        items3: list[int] = [item async for item in result3]

        assert items1 == items2 == items3 == [42]

    @pytest.mark.asyncio
    async def test_pure_with_different_value_types(self) -> None:
        """Test that pure flow works with different value types."""
        await self._test_pure_with_string()
        await self._test_pure_with_integer()
        await self._test_pure_with_list()

    async def _test_pure_with_string(self) -> None:
        """Test pure flow with string value."""
        string_flow: Flow[Any, str] = Flow.pure("test")

        async def dummy_stream1() -> AsyncGenerator[None, None]:
            yield None

        result1 = string_flow(dummy_stream1())
        items1: list[str] = [item async for item in result1]
        assert items1 == ["test"]

    async def _test_pure_with_integer(self) -> None:
        """Test pure flow with integer value."""
        int_flow: Flow[Any, int] = Flow.pure(123)

        async def dummy_stream2() -> AsyncGenerator[None, None]:
            yield None

        result2 = int_flow(dummy_stream2())
        items2: list[int] = [item async for item in result2]
        assert items2 == [123]

    async def _test_pure_with_list(self) -> None:
        """Test pure flow with list value."""
        list_flow: Flow[Any, list[str]] = Flow.pure(["a", "b", "c"])

        async def dummy_stream3() -> AsyncGenerator[None, None]:
            yield None

        result3 = list_flow(dummy_stream3())
        items3: list[list[str]] = [item async for item in result3]
        assert items3 == [["a", "b", "c"]]

    @pytest.mark.asyncio
    async def test_pure_with_none_value(self) -> None:
        """Test that pure flow works with None value."""

        flow: Flow[Any, None] = Flow.pure(None)

        async def any_stream() -> AsyncGenerator[str, None]:
            yield "anything"

        result = flow(any_stream())
        items: list[None] = [item async for item in result]

        assert items == [None]

    @pytest.mark.asyncio
    async def test_pure_with_complex_object(self) -> None:
        """Test that pure flow works with complex objects."""

        complex_obj = {"name": "test", "values": [1, 2, 3], "nested": {"key": "value"}}
        flow: Flow[Any, dict[str, Any]] = Flow.pure(complex_obj)

        async def any_stream() -> AsyncGenerator[int, None]:
            yield 999

        result = flow(any_stream())
        items: list[dict[str, Any]] = [item async for item in result]

        assert items == [complex_obj]
        # Ensure it's the same object reference
        assert items[0] is complex_obj

    def test_pure_sets_descriptive_name(self) -> None:
        """Test that pure flow sets a descriptive name including the value."""

        flow1: Flow[Any, str] = Flow.pure("hello")
        assert flow1.name == "pure(hello)"

        flow2: Flow[Any, int] = Flow.pure(42)
        assert flow2.name == "pure(42)"

        flow3: Flow[Any, list[int]] = Flow.pure([1, 2, 3])
        assert flow3.name == "pure([1, 2, 3])"

    @pytest.mark.asyncio
    async def test_pure_chaining_with_other_operations(self) -> None:
        """Test that pure flow can be chained with other operations."""

        def add_suffix(s: str) -> str:
            return f"{s}_modified"

        def repeat_twice(s: str) -> str:
            return s + s

        # Chain pure with transformations
        flow = Flow.pure("base").map(add_suffix).map(repeat_twice)

        async def any_stream() -> AsyncGenerator[int, None]:
            yield 123

        result = flow(any_stream())
        items: list[str] = [item async for item in result]

        assert items == ["base_modifiedbase_modified"]

    @pytest.mark.asyncio
    async def test_pure_composition_with_other_flows(self) -> None:
        """Test that pure flow can be composed with other flows."""

        def double(x: int) -> int:
            return x * 2

        pure_flow: Flow[Any, int] = Flow.pure(5)
        double_flow = Flow.from_sync_fn(double)

        # Compose pure with function flow
        composed = pure_flow >> double_flow

        async def any_stream() -> AsyncGenerator[str, None]:
            yield "ignored"

        result = composed(any_stream())
        items: list[int] = [item async for item in result]

        assert items == [10]  # 5 * 2

    @pytest.mark.asyncio
    async def test_pure_with_filter_operations(self) -> None:
        """Test pure flow with filter operations."""

        flow: Flow[Any, int] = Flow.pure(10)

        def is_even(x: int) -> bool:
            return x % 2 == 0

        filtered_flow = flow.filter(is_even)

        async def any_stream() -> AsyncGenerator[str, None]:
            yield "test"

        result = filtered_flow(any_stream())
        items: list[int] = [item async for item in result]

        assert items == [10]  # 10 is even, so it passes the filter

        # Test with filter that blocks the value
        def is_negative(x: int) -> bool:
            return x < 0

        blocked_flow = flow.filter(is_negative)
        result2 = blocked_flow(any_stream())
        items2: list[int] = [item async for item in result2]

        assert items2 == []  # 10 is not negative, so it's filtered out

    @pytest.mark.asyncio
    async def test_pure_preserves_value_identity(self) -> None:
        """Test that pure flow preserves the exact identity of mutable objects."""

        original_list = [1, 2, 3]
        flow: Flow[Any, list[int]] = Flow.pure(original_list)

        async def any_stream() -> AsyncGenerator[None, None]:
            yield None

        result = flow(any_stream())
        items: list[list[int]] = [item async for item in result]

        # Should be the exact same object
        assert items[0] is original_list

        # Modifying the original should affect the yielded value
        original_list.append(4)

        result2 = flow(any_stream())
        items2: list[list[int]] = [item async for item in result2]

        assert items2[0] == [1, 2, 3, 4]  # Reflects the mutation

    @pytest.mark.asyncio
    async def test_pure_multiple_calls_same_result(self) -> None:
        """Test that pure flow produces the same result across multiple calls."""

        flow: Flow[Any, str] = Flow.pure("constant")

        async def stream1() -> AsyncGenerator[int, None]:
            yield 1

        async def stream2() -> AsyncGenerator[str, None]:
            yield "different"

        async def stream3() -> AsyncGenerator[None, None]:
            return
            yield  # pragma: no cover

        result1 = flow(stream1())
        items1: list[str] = [item async for item in result1]

        result2 = flow(stream2())
        items2: list[str] = [item async for item in result2]

        result3 = flow(stream3())
        items3: list[str] = [item async for item in result3]

        assert items1 == items2 == items3 == ["constant"]

    @pytest.mark.asyncio
    async def test_pure_with_boolean_values(self) -> None:
        """Test pure flow with boolean values."""

        true_flow: Flow[Any, bool] = Flow.pure(True)
        false_flow: Flow[Any, bool] = Flow.pure(False)

        async def any_stream() -> AsyncGenerator[int, None]:
            yield 42

        result1 = true_flow(any_stream())
        items1: list[bool] = [item async for item in result1]

        result2 = false_flow(any_stream())
        items2: list[bool] = [item async for item in result2]

        assert items1 == [True]
        assert items2 == [False]

    @pytest.mark.asyncio
    async def test_pure_as_constant_source(self) -> None:
        """Test using pure flow as a constant value source in pipelines."""

        def format_number(n: int) -> str:
            return f"Number: {n}"

        def add_prefix(s: str) -> str:
            return f"Result - {s}"

        # Create a pipeline that starts with a constant and transforms it
        pipeline = Flow.pure(42).map(format_number).map(add_prefix)

        async def any_stream() -> AsyncGenerator[None, None]:
            yield None

        result = pipeline(any_stream())
        items: list[str] = [item async for item in result]

        assert items == ["Result - Number: 42"]
