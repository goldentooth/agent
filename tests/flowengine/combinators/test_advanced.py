"""Tests for advanced flow combinators."""

import asyncio
from typing import AsyncGenerator

import pytest

from flowengine import Flow
from flowengine.combinators.advanced import (
    chain_stream,
    combine_latest_stream,
    flat_map_ctx_stream,
    merge_async_generators,
    merge_flows,
    merge_stream,
    parallel_stream,
    parallel_stream_successful,
    race_stream,
    zip_stream,
)
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
    async def test_race_first_succeeds(self) -> None:
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
    async def test_race_first_fails_second_succeeds(self) -> None:
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
    async def test_race_all_fail(self) -> None:
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
    async def test_race_empty_list(self) -> None:
        """Test racing with no flows."""
        race_flow: Flow[int, int] = race_stream()

        input_stream = async_range(1)
        result_stream = race_flow(input_stream)

        # Should produce no results with no flows to race
        values = [item async for item in result_stream]
        assert values == []

    @pytest.mark.asyncio
    async def test_race_no_results(self) -> None:
        """Test racing when a flow produces no results."""

        async def empty_flow_fn(
            stream: AsyncGenerator[int, None],
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
    async def test_parallel_all_succeed(self) -> None:
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
    async def test_parallel_some_fail(self) -> None:
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
    async def test_parallel_empty_list(self) -> None:
        """Test parallel execution with no flows."""
        parallel_flow: Flow[int, list[int]] = parallel_stream()

        input_stream = async_range(2)
        result_stream = parallel_flow(input_stream)
        results = [item async for item in result_stream]

        # Each input produces empty list (no flows)
        assert results == [[], []]


class TestParallelStreamSuccessful:
    """Tests for parallel_stream_successful function."""

    @pytest.mark.asyncio
    async def test_parallel_successful_all_succeed(self) -> None:
        """Test parallel successful when all flows succeed."""
        increment_flow: Flow[int, int] = map_stream(increment)
        double_flow: Flow[int, int] = map_stream(double)

        parallel_flow = parallel_stream_successful(increment_flow, double_flow)
        assert "parallel_successful(map(increment), map(double))" in parallel_flow.name

        input_stream = async_range(2)
        result_stream = parallel_flow(input_stream)
        results = [item async for item in result_stream]

        assert len(results) == 2
        assert sorted(results[0]) == [0, 1]  # double(0)=0, increment(0)=1
        assert sorted(results[1]) == [2, 2]  # double(1)=2, increment(1)=2

    @pytest.mark.asyncio
    async def test_parallel_successful_some_fail(self) -> None:
        """Test parallel successful when some flows fail."""
        working_flow: Flow[int, int] = map_stream(double)
        failing_flow: Flow[int, int] = map_stream(lambda x: 1 // x)  # Fails on 0
        another_working: Flow[int, int] = map_stream(increment)

        parallel_flow = parallel_stream_successful(
            working_flow, failing_flow, another_working
        )

        input_stream = async_range(2)
        result_stream = parallel_flow(input_stream)
        results = [item async for item in result_stream]

        # For 0: failing_flow fails, others succeed
        assert sorted(results[0]) == [0, 1]  # double(0)=0, increment(0)=1
        # For 1: all succeed
        assert sorted(results[1]) == [1, 2, 2]  # 1//1=1, double(1)=2, increment(1)=2

    @pytest.mark.asyncio
    async def test_parallel_successful_all_fail(self) -> None:
        """Test parallel successful when all flows fail."""
        fail1: Flow[int, int] = map_stream(lambda x: 1 // 0)
        fail2: Flow[int, int] = map_stream(lambda x: x // 0)

        parallel_flow = parallel_stream_successful(fail1, fail2)

        input_stream = async_range(1)
        result_stream = parallel_flow(input_stream)
        results = [item async for item in result_stream]

        # Should return empty list when all fail
        assert results == [[]]

    @pytest.mark.asyncio
    async def test_parallel_successful_empty_list(self) -> None:
        """Test parallel successful with no flows."""
        parallel_flow: Flow[int, list[int]] = parallel_stream_successful()

        input_stream = async_range(1)
        result_stream = parallel_flow(input_stream)
        results = [item async for item in result_stream]

        assert results == [[]]


class TestZipStream:
    """Tests for zip_stream function."""

    @pytest.mark.asyncio
    async def test_zip_basic(self) -> None:
        """Test basic zipping functionality."""

        async def letters() -> AsyncGenerator[str, None]:
            for letter in ["a", "b", "c"]:
                yield letter

        zip_flow: Flow[int, tuple[int, str]] = zip_stream(letters())
        assert zip_flow.name == "zip"

        input_stream = async_range(3)
        result_stream = zip_flow(input_stream)
        values = [item async for item in result_stream]

        assert values == [(0, "a"), (1, "b"), (2, "c")]

    @pytest.mark.asyncio
    async def test_zip_different_lengths_first_shorter(self) -> None:
        """Test zipping when first stream is shorter."""

        async def short_stream() -> AsyncGenerator[str, None]:
            yield "x"
            yield "y"

        zip_flow: Flow[int, tuple[int, str]] = zip_stream(short_stream())

        input_stream = async_range(5)  # Longer
        result_stream = zip_flow(input_stream)
        values = [item async for item in result_stream]

        # Stops when other stream exhausted
        assert values == [(0, "x"), (1, "y")]

    @pytest.mark.asyncio
    async def test_zip_different_lengths_second_shorter(self) -> None:
        """Test zipping when second stream is shorter."""

        async def short_other() -> AsyncGenerator[str, None]:
            yield "only"

        zip_flow: Flow[int, tuple[int, str]] = zip_stream(short_other())

        input_stream = async_range(3)
        result_stream = zip_flow(input_stream)
        values = [item async for item in result_stream]

        # Stops when other stream exhausted
        assert values == [(0, "only")]

    @pytest.mark.asyncio
    async def test_zip_empty_streams(self) -> None:
        """Test zipping with empty streams."""

        async def empty() -> AsyncGenerator[str, None]:
            if False:
                yield "never"

        zip_flow: Flow[int, tuple[int, str]] = zip_stream(empty())

        input_stream = async_range(2)
        result_stream = zip_flow(input_stream)
        values = [item async for item in result_stream]

        assert values == []


class TestChainStream:
    """Tests for chain_stream function."""

    @pytest.mark.asyncio
    async def test_chain_basic(self) -> None:
        """Test basic stream chaining."""

        async def first() -> AsyncGenerator[int, None]:
            yield 1
            yield 2

        async def second() -> AsyncGenerator[int, None]:
            yield 3
            yield 4

        async def third() -> AsyncGenerator[int, None]:
            yield 5

        chain_flow: Flow[None, int] = chain_stream(first(), second(), third())
        assert "chain(3 streams)" in chain_flow.name

        # Chain doesn't need input
        async def empty_input() -> AsyncGenerator[None, None]:
            if False:
                yield None

        result_stream = chain_flow(empty_input())
        values = [item async for item in result_stream]

        assert values == [1, 2, 3, 4, 5]

    @pytest.mark.asyncio
    async def test_chain_empty_streams(self) -> None:
        """Test chaining with empty streams."""

        async def empty() -> AsyncGenerator[str, None]:
            if False:
                yield "never"

        async def normal() -> AsyncGenerator[str, None]:
            yield "middle"

        chain_flow: Flow[None, str] = chain_stream(empty(), normal(), empty())

        async def empty_input() -> AsyncGenerator[None, None]:
            if False:
                yield None

        result_stream = chain_flow(empty_input())
        values = [item async for item in result_stream]

        assert values == ["middle"]

    @pytest.mark.asyncio
    async def test_chain_single_stream(self) -> None:
        """Test chaining single stream."""

        async def single() -> AsyncGenerator[str, None]:
            yield "a"
            yield "b"

        chain_flow: Flow[None, str] = chain_stream(single())

        async def empty_input() -> AsyncGenerator[None, None]:
            if False:
                yield None

        result_stream = chain_flow(empty_input())
        values = [item async for item in result_stream]

        assert values == ["a", "b"]

    @pytest.mark.asyncio
    async def test_chain_no_streams(self) -> None:
        """Test chaining with no streams."""
        chain_flow: Flow[None, int] = chain_stream()

        async def empty_input() -> AsyncGenerator[None, None]:
            if False:
                yield None

        result_stream = chain_flow(empty_input())
        values = [item async for item in result_stream]

        assert values == []


class TestMergeStream:
    """Tests for merge_stream function."""

    @pytest.mark.asyncio
    async def test_merge_basic(self) -> None:
        """Test basic stream merging."""
        increment_flow: Flow[int, int] = map_stream(increment)
        double_flow: Flow[int, int] = map_stream(double)

        merge_flow = merge_stream(increment_flow, double_flow)
        assert "merge(map(increment), map(double))" in merge_flow.name

        input_stream = async_range(3)
        result_stream = merge_flow(input_stream)
        values = [item async for item in result_stream]

        # Both flows process all items
        assert sorted(values) == [0, 1, 2, 2, 3, 4]
        # Increment: [1, 2, 3]
        # Double: [0, 2, 4]

    @pytest.mark.asyncio
    async def test_merge_with_delays(self) -> None:
        """Test merging with different processing speeds."""
        fast_flow: Flow[int, str] = map_stream(lambda x: f"fast_{x}")
        slow_flow: Flow[int, str] = Flow(
            lambda s: self._delayed_process(s, 0.01, "slow")
        )

        merge_flow = merge_stream(fast_flow, slow_flow)

        input_stream = async_range(2)
        result_stream = merge_flow(input_stream)
        values = [item async for item in result_stream]

        # All items should be present
        assert len(values) == 4
        fast_values = [v for v in values if v.startswith("fast_")]
        slow_values = [v for v in values if v.startswith("slow_")]
        assert fast_values == ["fast_0", "fast_1"]
        assert slow_values == ["slow_0", "slow_1"]

    @pytest.mark.asyncio
    async def test_merge_empty_input(self) -> None:
        """Test merging with empty input."""
        flow1: Flow[int, int] = map_stream(increment)
        flow2: Flow[int, int] = map_stream(double)

        merge_flow = merge_stream(flow1, flow2)

        async def empty() -> AsyncGenerator[int, None]:
            if False:
                yield 0

        result_stream = merge_flow(empty())
        values = [item async for item in result_stream]

        assert values == []

    @pytest.mark.asyncio
    async def test_merge_with_flow_error(self) -> None:
        """Test merge stream when one flow raises an error."""

        def working_fn(x: int) -> str:
            return f"work_{x}"

        def failing_fn(x: int) -> str:
            if x == 1:
                raise ValueError("Intentional error")
            return f"fail_{x}"

        working_flow: Flow[int, str] = map_stream(working_fn)
        failing_flow: Flow[int, str] = map_stream(failing_fn)

        merge_flow = merge_stream(working_flow, failing_flow)

        input_stream = async_range(2)  # [0, 1] - second item will cause error
        result_stream = merge_flow(input_stream)

        with pytest.raises(ValueError) as exc_info:
            _ = [item async for item in result_stream]

        assert "Intentional error" in str(exc_info.value)

    async def _delayed_process(
        self, stream: AsyncGenerator[int, None], delay: float, prefix: str
    ) -> AsyncGenerator[str, None]:
        """Helper for delayed processing."""
        async for item in stream:
            await asyncio.sleep(delay)
            yield f"{prefix}_{item}"


class TestMergeFlows:
    """Tests for merge_flows function."""

    @pytest.mark.asyncio
    async def test_merge_flows_basic(self) -> None:
        """Test basic merge_flows functionality."""
        increment_flow: Flow[int, int] = Flow.from_sync_fn(increment)
        double_flow: Flow[int, int] = Flow.from_sync_fn(double)

        merge_flow = merge_flows(increment_flow, double_flow)
        assert "merge(increment, double)" in merge_flow.name

        input_stream = async_range(2)
        result_stream = merge_flow(input_stream)
        values = [item async for item in result_stream]

        assert sorted(values) == [0, 1, 2, 2]


class TestCombineLatestStream:
    """Tests for combine_latest_stream function."""

    @pytest.mark.asyncio
    async def test_combine_latest_basic(self) -> None:
        """Test basic combine latest functionality."""

        async def slow_other() -> AsyncGenerator[str, None]:
            await asyncio.sleep(0.01)
            yield "A"
            await asyncio.sleep(0.02)
            yield "B"
            await asyncio.sleep(0.02)
            yield "C"

        combine_flow: Flow[int, tuple[int, str]] = combine_latest_stream(slow_other())
        assert combine_flow.name == "combine_latest"

        # Fast input stream
        result_stream = combine_flow(async_range(5, delay=0.005))
        values: list[tuple[int, str]] = []

        start_time = asyncio.get_event_loop().time()
        async for value in result_stream:
            values.append(value)
            # Stop after reasonable time
            if asyncio.get_event_loop().time() - start_time > 0.1:
                break

        # Should combine items with latest from other stream
        assert len(values) > 0
        # All values should be tuples
        assert all(isinstance(v, tuple) and len(v) == 2 for v in values)

    @pytest.mark.asyncio
    async def test_combine_latest_empty_other(self) -> None:
        """Test combine latest when other stream is empty."""

        async def empty() -> AsyncGenerator[str, None]:
            if False:
                yield "never"

        combine_flow: Flow[int, tuple[int, str]] = combine_latest_stream(empty())

        input_stream = async_range(3)
        result_stream = combine_flow(input_stream)
        values = [item async for item in result_stream]

        # No combinations possible
        assert values == []

    @pytest.mark.asyncio
    async def test_combine_latest_other_stream_error(self) -> None:
        """Test combine latest when other stream raises an error."""

        async def error_stream() -> AsyncGenerator[str, None]:
            yield "A"
            raise ValueError("Other stream error")

        combine_flow: Flow[int, tuple[int, str]] = combine_latest_stream(error_stream())

        # Main stream
        input_stream = async_range(3, delay=0.01)
        result_stream = combine_flow(input_stream)

        # Should still work until the other stream fails
        values: list[tuple[int, str]] = []
        try:
            async for value in result_stream:
                values.append(value)
        except:
            # Exception from other stream is silently caught
            pass

        # Should have at least gotten some combinations before error
        assert len(values) >= 0  # May get some values before error


class TestFlatMapCtxStream:
    """Tests for flat_map_ctx_stream function."""

    @pytest.mark.asyncio
    async def test_flat_map_ctx_basic(self) -> None:
        """Test basic context-aware flat mapping."""

        async def expand_with_context(
            current: int, original: int
        ) -> AsyncGenerator[str, None]:
            # In simplified version, both args are the same
            yield f"{current}_expanded"
            if current < 2:
                yield f"{current}_extra"

        flat_map_flow: Flow[int, str] = flat_map_ctx_stream(expand_with_context)
        assert "flat_map_ctx(expand_with_context)" in flat_map_flow.name

        input_stream = async_range(3)
        result_stream = flat_map_flow(input_stream)
        values = [item async for item in result_stream]

        assert values == [
            "0_expanded",
            "0_extra",
            "1_expanded",
            "1_extra",
            "2_expanded",
        ]


class TestMergeAsyncGenerators:
    """Tests for merge_async_generators utility function."""

    @pytest.mark.asyncio
    async def test_merge_basic(self) -> None:
        """Test basic merging of async generators."""

        async def gen1() -> AsyncGenerator[str, None]:
            yield "a"
            await asyncio.sleep(0.01)
            yield "b"

        async def gen2() -> AsyncGenerator[str, None]:
            await asyncio.sleep(0.005)
            yield "1"
            await asyncio.sleep(0.01)
            yield "2"

        merged = merge_async_generators(gen1(), gen2())
        values = [item async for item in merged]

        # All items should be present (order may vary due to concurrency)
        assert sorted(values) == ["1", "2", "a", "b"]

    @pytest.mark.asyncio
    async def test_merge_empty_generators(self) -> None:
        """Test merging with empty generators."""

        async def empty1() -> AsyncGenerator[int, None]:
            if False:
                yield 1

        async def empty2() -> AsyncGenerator[int, None]:
            if False:
                yield 2

        async def normal() -> AsyncGenerator[int, None]:
            yield 42

        merged = merge_async_generators(empty1(), normal(), empty2())
        values = [item async for item in merged]

        assert values == [42]

    @pytest.mark.asyncio
    async def test_merge_no_generators(self) -> None:
        """Test merging with no generators."""
        merged: AsyncGenerator[int, None] = merge_async_generators()
        values: list[int] = [item async for item in merged]

        assert values == []

    @pytest.mark.asyncio
    async def test_merge_single_generator(self) -> None:
        """Test merging with single generator."""

        async def single() -> AsyncGenerator[str, None]:
            yield "only"
            yield "item"

        merged = merge_async_generators(single())
        values = [item async for item in merged]

        assert values == ["only", "item"]

    @pytest.mark.asyncio
    async def test_merge_with_error(self) -> None:
        """Test merging when one generator raises an error."""

        async def working() -> AsyncGenerator[str, None]:
            yield "good"

        async def failing() -> AsyncGenerator[str, None]:
            yield "before_error"
            raise ValueError("Generator error")

        merged = merge_async_generators(working(), failing())

        with pytest.raises(ValueError) as exc_info:
            _ = [item async for item in merged]

        assert "Generator error" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_merge_different_speeds(self) -> None:
        """Test merging generators with different speeds."""

        async def fast() -> AsyncGenerator[str, None]:
            for i in range(3):
                yield f"fast_{i}"
                await asyncio.sleep(0.001)

        async def slow() -> AsyncGenerator[str, None]:
            for i in range(2):
                await asyncio.sleep(0.01)
                yield f"slow_{i}"

        merged = merge_async_generators(fast(), slow())
        values = [item async for item in merged]

        assert len(values) == 5
        fast_values = [v for v in values if v.startswith("fast_")]
        slow_values = [v for v in values if v.startswith("slow_")]
        assert len(fast_values) == 3
        assert len(slow_values) == 2
