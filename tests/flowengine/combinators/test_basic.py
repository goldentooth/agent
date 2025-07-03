"""Tests for basic flow combinators."""

from __future__ import annotations

import pytest

from flowengine.combinators.basic import compose, run_fold
from flowengine.flow import Flow


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
            results.append(item)  # type: ignore[misc]

        assert results == [1, 2, 3]

    @pytest.mark.asyncio
    async def test_run_fold_single_step(self) -> None:
        """Test run_fold with a single step."""

        async def source():
            yield 1
            yield 2
            yield 3

        increment_flow = Flow.from_sync_fn(lambda x: x + 1)  # type: ignore[misc]
        result_stream = await run_fold(source(), [increment_flow])
        results: list[int] = []
        async for item in result_stream:
            results.append(item)  # type: ignore[misc]

        assert results == [2, 3, 4]

    @pytest.mark.asyncio
    async def test_run_fold_multiple_steps(self) -> None:
        """Test run_fold with multiple steps."""

        async def source():
            yield 1
            yield 2
            yield 3

        increment_flow = Flow.from_sync_fn(lambda x: x + 1)  # type: ignore[misc]
        double_flow = Flow.from_sync_fn(lambda x: x * 2)  # type: ignore[misc]
        result_stream = await run_fold(source(), [increment_flow, double_flow])
        results: list[int] = []
        async for item in result_stream:
            results.append(item)  # type: ignore[misc]

        assert results == [4, 6, 8]  # (1+1)*2, (2+1)*2, (3+1)*2

    @pytest.mark.asyncio
    async def test_run_fold_empty_stream(self) -> None:
        """Test run_fold with empty input stream."""

        async def empty_source():
            return
            yield  # pragma: no cover

        increment_flow = Flow.from_sync_fn(lambda x: x + 1)  # type: ignore[misc]
        result_stream = await run_fold(empty_source(), [increment_flow])
        results: list[int] = []
        async for item in result_stream:
            results.append(item)  # type: ignore[misc]

        assert results == []

    @pytest.mark.asyncio
    async def test_run_fold_identity_steps(self) -> None:
        """Test run_fold with identity flows."""

        async def source():
            yield 1
            yield 2
            yield 3

        identity_flow = Flow.from_sync_fn(lambda x: x)  # type: ignore[misc]
        result_stream = await run_fold(source(), [identity_flow, identity_flow])
        results: list[int] = []
        async for item in result_stream:
            results.append(item)  # type: ignore[misc]

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
        first_flow = Flow.from_sync_fn(lambda x: x + 1)  # type: ignore[misc]
        # Second flow: multiply by 2
        second_flow = Flow.from_sync_fn(lambda x: x * 2)  # type: ignore[misc]

        # Compose: (x + 1) * 2
        composed_flow = compose(first_flow, second_flow)  # type: ignore[misc]
        results: list[int] = []
        async for item in composed_flow(source()):  # type: ignore[misc]
            results.append(item)  # type: ignore[misc]

        assert results == [4, 6, 8]  # (1+1)*2, (2+1)*2, (3+1)*2

    @pytest.mark.asyncio
    async def test_compose_name_generation(self) -> None:
        """Test that compose generates appropriate names."""
        first_flow = Flow.from_sync_fn(lambda x: x + 1)  # type: ignore[misc]
        second_flow = Flow.from_sync_fn(lambda x: x * 2)  # type: ignore[misc]

        # Set custom names
        first_flow.name = "add_one"
        second_flow.name = "double"

        composed_flow = compose(first_flow, second_flow)  # type: ignore[misc]
        assert composed_flow.name == "add_one ∘ double"

    @pytest.mark.asyncio
    async def test_compose_empty_stream(self) -> None:
        """Test compose with empty input stream."""

        async def empty_source():
            return
            yield  # pragma: no cover

        first_flow = Flow.from_sync_fn(lambda x: x + 1)  # type: ignore[misc]
        second_flow = Flow.from_sync_fn(lambda x: x * 2)  # type: ignore[misc]

        composed_flow = compose(first_flow, second_flow)  # type: ignore[misc]
        results: list[int] = []
        async for item in composed_flow(empty_source()):  # type: ignore[misc]
            results.append(item)  # type: ignore[misc]

        assert results == []

    @pytest.mark.asyncio
    async def test_compose_identity_flows(self) -> None:
        """Test compose with identity flows."""

        async def source():
            yield 1
            yield 2
            yield 3

        identity_flow = Flow.from_sync_fn(lambda x: x)  # type: ignore[misc]

        composed_flow = compose(identity_flow, identity_flow)  # type: ignore[misc]
        results: list[int] = []
        async for item in composed_flow(source()):  # type: ignore[misc]
            results.append(item)  # type: ignore[misc]

        assert results == [1, 2, 3]

    @pytest.mark.asyncio
    async def test_compose_type_transformation(self) -> None:
        """Test compose with type transformation."""

        async def source():
            yield 1
            yield 2
            yield 3

        # First flow: int to string
        int_to_str = Flow.from_sync_fn(str)  # type: ignore[misc]
        # Second flow: string to length
        str_to_len = Flow.from_sync_fn(lambda s: len(s))  # type: ignore[misc]

        composed_flow = compose(int_to_str, str_to_len)  # type: ignore[misc]
        results: list[int] = []
        async for item in composed_flow(source()):  # type: ignore[misc]
            results.append(item)  # type: ignore[misc]

        assert results == [1, 1, 1]  # len("1"), len("2"), len("3")
