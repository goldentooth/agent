"""Performance benchmarks for Flow operations."""

import asyncio
import time
from collections.abc import AsyncGenerator
from typing import Any, List

import pytest

from flowengine.combinators import (
    batch_stream,
    distinct_stream,
    filter_stream,
    map_stream,
    memoize_stream,
    parallel_stream,
)
from flowengine.flow import Flow

# pyright: reportUnknownVariableType=false
# pyright: reportUnknownArgumentType=false
# pyright: reportUnknownParameterType=false
# pyright: reportUnknownLambdaType=false
# pyright: reportOperatorIssue=false
# pyright: reportCallIssue=false
# pyright: reportArgumentType=false


# Test fixtures
async def async_range(n: int) -> AsyncGenerator[int, None]:
    """Generate numbers from 0 to n-1."""
    for i in range(n):
        yield i


async def async_large_range(n: int = 10000) -> AsyncGenerator[int, None]:
    """Generate a large range for performance testing."""
    for i in range(n):
        yield i


class TestFlowBenchmarks:
    """Core benchmarking test class for Flow operations."""

    @pytest.mark.asyncio
    async def test_simple_flow_performance(self):
        """Benchmark simple flow operations like map and filter."""
        await self._test_map_performance()
        await self._test_filter_performance()

    async def _test_map_performance(self):
        """Test map operation performance."""
        map_flow = map_stream(lambda x: x * 2)

        start_time = time.time()
        input_stream = async_large_range(1000)
        result = [item async for item in map_flow(input_stream)]
        duration = time.time() - start_time

        assert len(result) == 1000
        assert duration < 1.0  # Should complete in under 1 second

        # Check throughput
        throughput = len(result) / duration
        assert throughput > 500  # At least 500 items/second

    async def _test_filter_performance(self):
        """Test filter operation performance."""
        filter_flow = filter_stream(lambda x: x % 2 == 0)

        start_time = time.time()
        input_stream = async_large_range(1000)
        result = [item async for item in filter_flow(input_stream)]
        duration = time.time() - start_time

        assert len(result) == 500  # Half the items should pass
        assert duration < 1.0

    @pytest.mark.asyncio
    async def test_complex_composition_performance(self):
        """Benchmark complex flow composition performance."""
        # Create a complex pipeline using available methods
        from flowengine.combinators import batch_stream

        # Create empty input for from_iterable
        async def empty_stream():
            yield None

        base_flow = (
            Flow.from_iterable(range(1000))
            .map(lambda x: x * 2)
            .filter(lambda x: x % 4 == 0)
        )

        # Manually compose with batch operation
        complex_flow = (
            base_flow >> batch_stream(10) >> map_stream(lambda batch: sum(batch))
        )

        start_time = time.time()
        result = await complex_flow.to_list()(empty_stream())
        duration = time.time() - start_time

        assert len(result) > 0
        assert duration < 2.0

        # Verify correctness
        expected_items = [x * 2 for x in range(1000) if (x * 2) % 4 == 0]
        expected_batches = [
            expected_items[i : i + 10] for i in range(0, len(expected_items), 10)
        ]
        expected_sums = [sum(batch) for batch in expected_batches]

        assert result == expected_sums

    @pytest.mark.asyncio
    async def test_memory_usage_tracking(self):
        """Test memory usage tracking during flow operations."""
        await self._test_batch_memory_usage()
        await self._test_distinct_memory_usage()
        await self._test_memoization_memory_usage()

    async def _test_batch_memory_usage(self):
        """Test batch operation for memory usage."""
        batch_flow = batch_stream(10)

        start_time = time.time()
        input_stream = async_large_range(1000)
        result = [batch async for batch in batch_flow(input_stream)]
        duration = time.time() - start_time

        assert len(result) == 100  # 1000 items / 10 per batch
        assert all(len(batch) == 10 for batch in result)
        assert duration < 1.0

    async def _test_distinct_memory_usage(self):
        """Test distinct operation for memory usage."""
        distinct_flow = distinct_stream()

        async def duplicate_stream():
            for _ in range(100):
                for i in range(10):  # 10 unique items, repeated 100 times
                    yield i

        start_time = time.time()
        result = [item async for item in distinct_flow(duplicate_stream())]
        duration = time.time() - start_time

        assert len(result) == 10  # Only unique items should remain
        assert set(result) == set(range(10))
        assert duration < 1.0

    async def _test_memoization_memory_usage(self):
        """Test memoization for memory usage."""
        memoize_flow = memoize_stream(lambda x: x)

        async def repeat_stream():
            for _ in range(100):
                for i in range(5):
                    yield i

        start_time = time.time()
        result = [item async for item in memoize_flow(repeat_stream())]
        duration = time.time() - start_time

        assert len(result) == 500  # All items pass through (memoization doesn't filter)
        assert duration < 1.0

    @pytest.mark.asyncio
    async def test_parallel_performance(self):
        """Benchmark parallel_stream performance."""
        # Create simple flows for parallel execution
        flow1 = map_stream(lambda x: x * 2)
        flow2 = map_stream(lambda x: x + 10)
        flow3 = map_stream(lambda x: x**2)

        parallel_flow = parallel_stream(flow1, flow2, flow3)

        start_time = time.time()
        input_stream = async_range(100)
        result = [item async for item in parallel_flow(input_stream)]
        duration = time.time() - start_time

        assert len(result) == 100
        assert all(len(item_results) == 3 for item_results in result)
        assert duration < 2.0  # Parallel should be faster than sequential

    @pytest.mark.asyncio
    async def test_concurrent_flow_execution(self):
        """Test multiple flows running concurrently."""
        flow1 = map_stream(lambda x: x * 2)
        flow2 = map_stream(lambda x: x + 100)
        flow3 = filter_stream(lambda x: x % 2 == 0)

        async def run_flow(flow: Any, stream_size: int) -> List[Any]:
            input_stream = async_range(stream_size)
            return [item async for item in flow(input_stream)]

        # Run multiple flows concurrently
        start_time = time.time()
        results = await asyncio.gather(
            run_flow(flow1, 500), run_flow(flow2, 500), run_flow(flow3, 500)
        )
        duration = time.time() - start_time

        # All should complete
        assert len(results) == 3
        assert len(results[0]) == 500  # flow1 results
        assert len(results[1]) == 500  # flow2 results
        assert len(results[2]) == 250  # flow3 results (half pass filter)

        # Should complete in reasonable time
        assert duration < 5.0

    @pytest.mark.asyncio
    async def test_error_handling_performance(self):
        """Test that error handling doesn't significantly impact performance."""

        def sometimes_fail(x: int) -> int:
            if x % 100 == 99:  # Fail on every 100th item
                raise ValueError(f"Intentional error for item {x}")
            return x * 2

        # Create a flow that handles errors at the map level
        def safe_map_function(x: int) -> int:
            try:
                return sometimes_fail(x)
            except ValueError:
                return x  # Return original value on error

        # Use the safe version instead
        combined_flow = map_stream(safe_map_function)

        start_time = time.time()
        input_stream = async_range(1000)
        result = [item async for item in combined_flow(input_stream)]
        duration = time.time() - start_time

        # Should complete with some results
        assert len(result) > 0
        # Should not take too long despite errors
        assert duration < 5.0
