"""Tests for advanced flow combinators."""

import asyncio
from typing import AsyncGenerator

import pytest

from flowengine import Flow
from flowengine.combinators.advanced import parallel_stream, race_stream
from flowengine.combinators.basic import map_stream
from flowengine.exceptions import FlowExecutionError


# Helper functions
def increment(x: int) -> int:
    """Increment a number by 1."""
    return x + 1


def double(x: int) -> int:
    """Double a number."""
    return x * 2


def triple(x: int) -> int:
    """Triple a number."""
    return x * 3


async def async_range(n: int, delay: float = 0) -> AsyncGenerator[int, None]:
    """Generate an async range with optional delay."""
    for i in range(n):
        if delay > 0:
            await asyncio.sleep(delay)
        yield i


async def async_increment(x: int) -> int:
    """Async increment function."""
    await asyncio.sleep(0.001)
    return x + 1


class TestRaceStream:
    """Tests for race_stream function."""

    @pytest.mark.asyncio
    async def test_race_first_succeeds(self):
        """Test racing when first flow succeeds."""
        fast_flow: Flow[int, str] = map_stream(lambda x: f"fast_{x}")
        slow_flow: Flow[int, str] = Flow(lambda s: self._slow_process(s, 0.1))

        race_flow = race_stream(fast_flow, slow_flow)
        assert "race(map(<lambda>), <anonymous>)" in race_flow.name

        input_stream = async_range(2)
        result_stream = race_flow(input_stream)
        values = [item async for item in result_stream]

        # Fast flow should win
        assert values == ["fast_0", "fast_1"]

    @pytest.mark.asyncio
    async def test_race_first_fails_second_succeeds(self):
        """Test racing when first flow fails but second succeeds."""
        failing_flow: Flow[int, int] = map_stream(lambda x: 1 // 0)  # Always fails
        working_flow: Flow[int, int] = map_stream(double)

        race_flow = race_stream(failing_flow, working_flow)

        input_stream = async_range(2)
        result_stream = race_flow(input_stream)
        values = [item async for item in result_stream]

        # Working flow should provide results
        assert values == [0, 2]

    @pytest.mark.asyncio
    async def test_race_all_fail(self):
        """Test racing when all flows fail."""
        fail1_flow: Flow[int, int] = map_stream(lambda x: 1 // 0)
        fail2_flow: Flow[int, int] = map_stream(lambda x: x // 0)

        race_flow = race_stream(fail1_flow, fail2_flow)

        input_stream = async_range(1)
        result_stream = race_flow(input_stream)

        with pytest.raises(FlowExecutionError) as exc_info:
            _ = [item async for item in result_stream]

        assert "All racing flows failed" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_race_empty_list(self):
        """Test racing with no flows."""
        race_flow: Flow[int, int] = race_stream()

        input_stream = async_range(1)
        result_stream = race_flow(input_stream)

        # Should produce no results with no flows to race
        values = [item async for item in result_stream]
        assert values == []

    @pytest.mark.asyncio
    async def test_race_no_results(self):
        """Test racing when a flow produces no results."""

        async def empty_flow_fn(
            stream: AsyncGenerator[int, None]
        ) -> AsyncGenerator[int, None]:
            async for _ in stream:
                pass  # Consume but don't yield anything
            return
            yield  # Unreachable, but needed for async generator

        empty_flow: Flow[int, int] = Flow(empty_flow_fn)
        race_flow = race_stream(empty_flow)

        input_stream = async_range(1)
        result_stream = race_flow(input_stream)

        with pytest.raises(FlowExecutionError) as exc_info:
            _ = [item async for item in result_stream]

        assert "All racing flows failed" in str(exc_info.value)

    async def _slow_process(
        self, stream: AsyncGenerator[int, None], delay: float
    ) -> AsyncGenerator[str, None]:
        """Helper for slow processing."""
        async for item in stream:
            await asyncio.sleep(delay)
            yield f"slow_{item}"


class TestParallelStream:
    """Tests for parallel_stream function."""

    @pytest.mark.asyncio
    async def test_parallel_all_succeed(self):
        """Test parallel execution when all flows succeed."""
        increment_flow: Flow[int, int] = map_stream(increment)
        double_flow: Flow[int, int] = map_stream(double)
        triple_flow: Flow[int, int] = map_stream(triple)

        parallel_flow = parallel_stream(increment_flow, double_flow, triple_flow)
        assert (
            "parallel(map(increment), map(double), map(triple))" in parallel_flow.name
        )

        input_stream = async_range(2)
        result_stream = parallel_flow(input_stream)
        results = [item async for item in result_stream]

        # Each input produces results from all flows
        assert len(results) == 2  # One list per input item
        # For input 0: [1, 0, 0] (increment, double, triple)
        assert sorted(results[0]) == [0, 0, 1]
        # For input 1: [2, 2, 3]
        assert sorted(results[1]) == [2, 2, 3]

    @pytest.mark.asyncio
    async def test_parallel_some_fail(self):
        """Test parallel execution when some flows fail."""
        working_flow: Flow[int, int] = map_stream(double)
        failing_flow: Flow[int, int] = map_stream(lambda x: 1 // 0)

        parallel_flow = parallel_stream(working_flow, failing_flow)

        input_stream = async_range(1)
        result_stream = parallel_flow(input_stream)

        with pytest.raises(FlowExecutionError) as exc_info:
            _ = [item async for item in result_stream]

        assert "Parallel execution failed" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_parallel_empty_list(self):
        """Test parallel execution with no flows."""
        parallel_flow: Flow[int, list[int]] = parallel_stream()

        input_stream = async_range(2)
        result_stream = parallel_flow(input_stream)
        results = [item async for item in result_stream]

        # Each input produces empty list (no flows)
        assert results == [[], []]
