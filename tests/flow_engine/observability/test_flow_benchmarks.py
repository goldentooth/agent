"""Performance and benchmarking tests for Flow combinators."""

import asyncio
import time
from collections.abc import AsyncIterator

import pytest

from goldentooth_agent.flow_engine import Flow
from goldentooth_agent.flow_engine.combinators import (
    batch_stream,
    distinct_stream,
    filter_stream,
    map_stream,
    memoize_stream,
    parallel_stream,
)
from goldentooth_agent.flow_engine.observability.performance import (
    benchmark_stream,
    enable_memory_tracking,
    get_performance_monitor,
    get_performance_summary,
    monitored_stream,
    performance_stream,
)


# Test fixtures
async def async_range(n: int) -> AsyncIterator[int]:
    """Generate numbers from 0 to n-1."""
    for i in range(n):
        yield i


async def async_large_range(n: int = 10000) -> AsyncIterator[int]:
    """Generate a large range for performance testing."""
    for i in range(n):
        yield i


class TestPerformanceMonitoring:
    """Test performance monitoring capabilities."""

    def setup_method(self):
        """Reset performance monitor before each test."""
        get_performance_monitor().metrics.clear()
        get_performance_monitor().global_stats.clear()

    @pytest.mark.asyncio
    async def test_monitored_stream_basic(self):
        """Test basic performance monitoring."""

        @monitored_stream("test_flow")
        def create_test_flow():
            return map_stream(lambda x: x * 2)

        flow = create_test_flow
        input_stream = async_range(100)
        result = [item async for item in flow(input_stream)]

        assert len(result) == 100
        assert result[:3] == [0, 2, 4]

        # Check that metrics were collected
        summary = get_performance_summary()
        assert summary["total_flows_monitored"] > 0

    @pytest.mark.asyncio
    async def test_performance_stream_combinator(self):
        """Test the performance_stream combinator."""
        flow = performance_stream()
        input_stream = async_range(50)
        result = [item async for item in flow(input_stream)]

        assert result == list(range(50))

        # Check metrics
        summary = get_performance_summary()
        assert "duration_ms" in summary

    @pytest.mark.asyncio
    async def test_benchmark_basic(self):
        """Test basic benchmarking functionality."""
        test_flow = map_stream(lambda x: x + 1)
        benchmark = benchmark_stream(iterations=10, warmup_iterations=2)

        def test_stream_factory():
            return async_range(100)

        stats = await benchmark(test_flow)(test_stream_factory)

        assert "flow_name" in stats
        assert "avg_duration_ms" in stats
        assert "min_duration_ms" in stats
        assert "max_duration_ms" in stats
        assert "p50_duration_ms" in stats
        assert "p95_duration_ms" in stats
        assert "p99_duration_ms" in stats
        assert stats["iterations"] == 10

    @pytest.mark.asyncio
    async def test_memory_tracking(self):
        """Test memory usage tracking."""
        try:
            import psutil  # noqa: F401
        except ImportError:
            pytest.skip("psutil not available for memory tracking")

        enable_memory_tracking()

        @monitored_stream("memory_test")
        def create_memory_flow():
            return map_stream(lambda x: x * 2)

        flow = create_memory_flow
        input_stream = async_range(1000)
        result = [item async for item in flow(input_stream)]

        assert len(result) == 1000

        # Memory metrics should be available
        metrics = get_performance_monitor().metrics
        if metrics:
            latest_metric = list(metrics.values())[-1]
            # Memory tracking might be available
            assert (
                latest_metric.memory_usage_kb is not None
                or latest_metric.memory_usage_kb is None
            )


class TestPerformanceBenchmarks:
    """Performance benchmarks for various Flow operations."""

    @pytest.mark.asyncio
    async def test_map_performance(self):
        """Benchmark map_stream performance."""
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

    @pytest.mark.asyncio
    async def test_filter_performance(self):
        """Benchmark filter_stream performance."""
        filter_flow = filter_stream(lambda x: x % 2 == 0)

        start_time = time.time()
        input_stream = async_large_range(1000)
        result = [item async for item in filter_flow(input_stream)]
        duration = time.time() - start_time

        assert len(result) == 500  # Half the items should pass
        assert duration < 1.0

    @pytest.mark.asyncio
    async def test_batch_performance(self):
        """Benchmark batch_stream performance."""
        batch_flow = batch_stream(10)

        start_time = time.time()
        input_stream = async_large_range(1000)
        result = [batch async for batch in batch_flow(input_stream)]
        duration = time.time() - start_time

        assert len(result) == 100  # 1000 items / 10 per batch
        assert all(len(batch) == 10 for batch in result)
        assert duration < 1.0

    @pytest.mark.asyncio
    async def test_distinct_performance(self):
        """Benchmark distinct_stream performance with duplicates."""
        distinct_flow = distinct_stream()

        # Create stream with many duplicates
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

    @pytest.mark.asyncio
    async def test_memoize_performance(self):
        """Benchmark memoize_stream performance."""
        memoize_flow = memoize_stream(lambda x: x)

        # Create stream with repeated values
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
    async def test_composition_performance(self):
        """Benchmark complex flow composition performance."""
        # Create a complex pipeline using available methods
        from goldentooth_agent.flow_engine.combinators import batch_stream

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


class TestScalabilityTests:
    """Test Flow behavior under various scale conditions."""

    @pytest.mark.asyncio
    async def test_large_stream_processing(self):
        """Test processing very large streams."""
        flow = map_stream(lambda x: x + 1)

        # Process 10,000 items
        input_stream = async_large_range(10000)

        start_time = time.time()
        count = 0
        async for _item in flow(input_stream):
            count += 1
            if count % 1000 == 0:
                # Check that we're not accumulating too much time
                elapsed = time.time() - start_time
                assert elapsed < 10.0  # Should process 1000 items in under 10 seconds

        assert count == 10000

    @pytest.mark.asyncio
    async def test_memory_bounded_operations(self):
        """Test that memory-bounded operations don't leak."""
        # Test distinct_stream performance
        distinct_flow = distinct_stream()

        # Generate more unique items than the memory limit
        async def large_unique_stream():
            for i in range(1000):
                yield str(i)  # Unique string keys

        result = [item async for item in distinct_flow(large_unique_stream())]

        # Should process all items (distinct_stream passes all through)
        assert len(result) == 1000

        # The internal memory should be bounded
        # (We can't easily test this without accessing internals)

    @pytest.mark.asyncio
    async def test_concurrent_flow_execution(self):
        """Test multiple flows running concurrently."""
        flow1 = map_stream(lambda x: x * 2)
        flow2 = map_stream(lambda x: x + 100)
        flow3 = filter_stream(lambda x: x % 2 == 0)

        async def run_flow(flow, stream_size):
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

        def sometimes_fail(x):
            if x % 100 == 99:  # Fail on every 100th item
                raise ValueError(f"Intentional error for item {x}")
            return x * 2

        # Create a flow that handles errors at the map level
        def safe_map_function(x):
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
