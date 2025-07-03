"""Tests for basic flow combinators."""

from __future__ import annotations

import pytest

from flowengine.combinators.basic import run_fold
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
            results.append(item)

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
            results.append(item)

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
            results.append(item)

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
            results.append(item)

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
            results.append(item)

        assert results == [1, 2, 3]
