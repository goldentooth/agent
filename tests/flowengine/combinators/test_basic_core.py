"""Tests for core flow combinators: run_fold, compose, identity_stream."""

from __future__ import annotations

from typing import AsyncGenerator

import pytest

from flowengine.combinators.basic import compose, identity_stream, run_fold
from flowengine.flow import Flow

from .conftest import double, identity, increment, int_to_str, str_length


class TestRunFold:
    """Test the run_fold function."""

    @pytest.mark.asyncio
    async def test_run_fold_empty_steps(self) -> None:
        """Test run_fold with empty steps list."""

        async def source() -> AsyncGenerator[int, None]:
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

        async def source() -> AsyncGenerator[int, None]:
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

        async def source() -> AsyncGenerator[int, None]:
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

        async def empty_source() -> AsyncGenerator[int, None]:
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

        async def source() -> AsyncGenerator[int, None]:
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

        async def source() -> AsyncGenerator[int, None]:
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

        async def empty_source() -> AsyncGenerator[int, None]:
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

        async def source() -> AsyncGenerator[int, None]:
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

        async def source() -> AsyncGenerator[int, None]:
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


class TestIdentityStream:
    """Test the identity_stream function."""

    @pytest.mark.asyncio
    async def test_identity_stream_basic(self) -> None:
        """Test identity_stream passes through all items unchanged."""

        async def source() -> AsyncGenerator[int, None]:
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

        async def source() -> AsyncGenerator[int, None]:
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

        async def empty_source() -> AsyncGenerator[int, None]:
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

        async def source() -> AsyncGenerator[int, None]:
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
