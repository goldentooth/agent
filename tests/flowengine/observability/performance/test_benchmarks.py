"""Performance benchmarks for Flow operations."""

import asyncio
import json
import os
import tempfile
import time
from collections.abc import AsyncGenerator
from typing import Any, Dict, List

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
from flowengine.observability.performance import (
    benchmark_stream,
    enable_memory_tracking,
    get_performance_monitor,
    get_performance_summary,
    memory_profile_stream,
    monitored_stream,
)

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


class TestPerformanceRegression:
    """Performance regression test class for detecting performance degradation."""

    @pytest.mark.asyncio
    async def test_performance_doesnt_degrade(self):
        """Test that performance doesn't degrade compared to baseline."""
        # Define baseline performance expectations
        baseline_throughput = 500  # items/second
        baseline_duration = 1.0  # seconds for 1000 items

        # Test flow performance
        test_flow = map_stream(lambda x: x * 2)

        # Run performance test
        benchmark = benchmark_stream(iterations=5)

        def test_stream_factory():
            return async_large_range(1000)

        stats = await benchmark(test_flow)(test_stream_factory)

        # Assert performance doesn't degrade
        avg_duration = stats["avg_duration_ms"] / 1000  # Convert to seconds
        assert avg_duration < baseline_duration * 1.2  # Allow 20% variance

        # Calculate throughput (items processed / time)
        throughput = 1000 / avg_duration
        assert throughput > baseline_throughput * 0.8  # Allow 20% variance

    @pytest.mark.asyncio
    async def test_memory_leaks(self):
        """Test for memory leaks during repeated flow executions."""
        try:
            import psutil  # noqa: F401
        except ImportError:
            pytest.skip("psutil not available for memory tracking")

        enable_memory_tracking()

        # Create flow that processes data
        @monitored_stream("memory_leak_test")
        def create_test_flow():
            return map_stream(lambda x: x * 2)

        flow = create_test_flow
        initial_memory: float | None = None
        memory_measurements: list[float] = []

        # Run multiple iterations to detect memory leaks
        for iteration in range(5):
            input_stream = async_large_range(1000)
            result = [item async for item in flow(input_stream)]
            assert len(result) == 1000

            # Get memory usage after each iteration
            monitor = get_performance_monitor()
            if monitor.metrics:
                latest_metric = list(monitor.metrics.values())[-1]
                if latest_metric.memory_usage_kb is not None:
                    if initial_memory is None:
                        initial_memory = latest_metric.memory_usage_kb
                    memory_measurements.append(latest_metric.memory_usage_kb)

        # Check for memory leak (memory shouldn't grow significantly)
        if memory_measurements and initial_memory is not None:
            final_memory = memory_measurements[-1]
            memory_growth = final_memory - initial_memory
            # Allow some memory growth but not excessive (< 50% increase)
            assert memory_growth < initial_memory * 0.5

    @pytest.mark.asyncio
    async def test_throughput_consistency(self):
        """Test that throughput remains consistent across multiple runs."""
        test_flow = map_stream(lambda x: x + 1)
        # Use 30 trials with percentile-based outlier removal (trim top/bottom 10%)
        benchmark = benchmark_stream(
            iterations=30, warmup_iterations=5, trim_percent=10.0
        )

        def test_stream_factory():
            # Use larger dataset for more stable timing measurements
            return async_large_range(2000)

        stats = await benchmark(test_flow)(test_stream_factory)
        self._validate_throughput_consistency(stats)

    def _validate_throughput_consistency(self, stats: Dict[str, Any]):
        """Validate throughput consistency from benchmark statistics."""
        throughput_metrics = self._calculate_throughput_metrics(stats)
        self._assert_variance_within_threshold(throughput_metrics, stats)
        self._assert_no_extreme_outliers(throughput_metrics)
        self._assert_minimum_performance(throughput_metrics)

    def _calculate_throughput_metrics(self, stats: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate throughput metrics from benchmark statistics."""
        min_duration = stats["min_duration_ms"] / 1000
        max_duration = stats["max_duration_ms"] / 1000
        avg_duration = stats["avg_duration_ms"] / 1000

        # Calculate throughput for each duration measurement (2000 items per test)
        dataset_size = 2000
        min_throughput = dataset_size / max_duration  # Inverse relationship
        max_throughput = dataset_size / min_duration
        avg_throughput = dataset_size / avg_duration

        return {
            "min_duration": min_duration,
            "max_duration": max_duration,
            "avg_duration": avg_duration,
            "min_throughput": min_throughput,
            "max_throughput": max_throughput,
            "avg_throughput": avg_throughput,
        }

    def _assert_variance_within_threshold(
        self, metrics: Dict[str, Any], stats: Dict[str, Any]
    ):
        """Assert throughput variance is within acceptable threshold."""
        throughput_variance = (
            metrics["max_throughput"] - metrics["min_throughput"]
        ) / metrics["avg_throughput"]

        # Use more lenient thresholds in CI environments
        is_ci = os.getenv("CI") is not None or os.getenv("GITHUB_ACTIONS") is not None
        variance_threshold = 0.4 if is_ci else 0.25  # 40% for CI, 25% for local

        assert throughput_variance < variance_threshold, (
            f"Throughput variance {throughput_variance:.3f} exceeds threshold {variance_threshold} "
            f"({'CI' if is_ci else 'local'} environment). "
            f"Stats: min={metrics['min_throughput']:.2f}, max={metrics['max_throughput']:.2f}, avg={metrics['avg_throughput']:.2f} ops/sec "
            f"(from {stats['iterations']}/{stats.get('original_iterations', 'unknown')} samples "
            f"after {stats.get('trim_percent', 0)}% trimming)"
        )

    def _assert_no_extreme_outliers(self, metrics: Dict[str, Any]):
        """Assert max duration is not an extreme outlier."""
        # Use more lenient outlier detection in CI environments
        is_ci = os.getenv("CI") is not None or os.getenv("GITHUB_ACTIONS") is not None
        outlier_threshold = 10.0 if is_ci else 5.0  # 10x for CI, 5x for local

        assert metrics["max_duration"] < metrics["avg_duration"] * outlier_threshold, (
            f"Max duration {metrics['max_duration']:.3f}s exceeds {outlier_threshold}x average "
            f"{metrics['avg_duration']:.3f}s ({'CI' if is_ci else 'local'} environment)"
        )

    def _assert_minimum_performance(self, metrics: Dict[str, Any]):
        """Assert minimum performance is reasonable."""
        # Use more lenient minimum performance threshold in CI environments
        is_ci = os.getenv("CI") is not None or os.getenv("GITHUB_ACTIONS") is not None
        min_performance_ratio = 0.1 if is_ci else 0.2  # 10% for CI, 20% for local

        assert (
            metrics["min_throughput"]
            > metrics["avg_throughput"] * min_performance_ratio
        ), (
            f"Min throughput {metrics['min_throughput']:.2f} is less than {min_performance_ratio*100}% "
            f"of average {metrics['avg_throughput']:.2f} ops/sec ({'CI' if is_ci else 'local'} environment)"
        )


class TestBenchmarkReporting:
    """Benchmark reporting test class for data export and analysis."""

    @pytest.mark.asyncio
    async def test_benchmark_export(self):
        """Test benchmark data export functionality."""

        # Create monitored flow and generate performance data
        @monitored_stream("export_test_flow")
        def create_test_flow():
            return map_stream(lambda x: x * 2)

        flow = create_test_flow
        input_stream = async_large_range(100)
        result = [item async for item in flow(input_stream)]
        assert len(result) == 100

        # Export performance metrics to temporary file
        with tempfile.NamedTemporaryFile(
            mode="w", delete=False, suffix=".json"
        ) as tmp_file:
            monitor = get_performance_monitor()
            monitor.export_metrics(tmp_file.name)

            # Verify export file exists and contains valid JSON
            assert os.path.exists(tmp_file.name)

            with open(tmp_file.name, "r") as f:
                exported_data = json.load(f)

            # Validate export structure and content
            assert "summary" in exported_data
            assert "individual_flows" in exported_data

            # Find flow by name (key includes timestamp)
            flow_found = False
            for flow_id, flow_data in exported_data["individual_flows"].items():
                if flow_data.get("name") == "export_test_flow":
                    flow_found = True
                    assert flow_data["items_processed"] == 100
                    break
            assert flow_found, "Expected flow 'export_test_flow' not found in export"

            # Clean up
            os.unlink(tmp_file.name)

    @pytest.mark.asyncio
    async def test_performance_comparison(self):
        """Test performance comparison analysis between benchmark runs."""
        # Run first benchmark (baseline)
        baseline_stats = await self._run_baseline_benchmark()

        # Run second benchmark (comparison)
        comparison_stats = await self._run_comparison_benchmark()

        # Compare performance metrics
        self._validate_performance_comparison(baseline_stats, comparison_stats)

    async def _run_baseline_benchmark(self) -> Dict[str, Any]:
        """Run baseline benchmark for comparison testing."""
        baseline_flow = map_stream(lambda x: x * 2)
        baseline_benchmark = benchmark_stream(iterations=5)

        def baseline_stream_factory():
            return async_large_range(500)

        return await baseline_benchmark(baseline_flow)(baseline_stream_factory)

    async def _run_comparison_benchmark(self) -> Dict[str, Any]:
        """Run comparison benchmark with different operation."""
        comparison_flow = map_stream(lambda x: x * 3)  # Different operation
        comparison_benchmark = benchmark_stream(iterations=5)

        def comparison_stream_factory():
            return async_large_range(500)

        return await comparison_benchmark(comparison_flow)(comparison_stream_factory)

    def _validate_performance_comparison(
        self, baseline_stats: Dict[str, Any], comparison_stats: Dict[str, Any]
    ):
        """Validate performance comparison analysis results."""
        # Compare performance metrics
        baseline_avg = baseline_stats["avg_duration_ms"]
        comparison_avg = comparison_stats["avg_duration_ms"]

        # Calculate performance difference (percentage)
        performance_diff = abs(comparison_avg - baseline_avg) / baseline_avg

        # Verify comparison analysis works
        assert isinstance(performance_diff, float)
        assert performance_diff >= 0  # Should be non-negative percentage

        # Verify both benchmarks produced valid results
        original_iterations = 5
        trim_percent = 10.0

        # Calculate expected trimmed count using same logic as benchmark_stream
        trim_count = max(1, int(original_iterations * (trim_percent / 100)))
        if original_iterations > 2 * trim_count:
            expected_trimmed = original_iterations - 2 * trim_count
        else:
            expected_trimmed = max(
                1, original_iterations - 2
            )  # Remove most extreme outliers

        assert baseline_stats["original_iterations"] == original_iterations
        assert comparison_stats["original_iterations"] == original_iterations
        assert baseline_stats["iterations"] == expected_trimmed
        assert comparison_stats["iterations"] == expected_trimmed

    @pytest.mark.asyncio
    async def test_statistical_analysis(self):
        """Test statistical analysis of benchmark results."""
        # Run benchmark with multiple iterations for statistical analysis
        test_flow = map_stream(lambda x: x + 1)
        benchmark = benchmark_stream(iterations=10)

        def test_stream_factory():
            return async_large_range(300)

        stats = await benchmark(test_flow)(test_stream_factory)
        self._validate_statistical_metrics(stats)

    def _validate_statistical_metrics(self, stats: Dict[str, Any]):
        """Validate statistical metrics from benchmark results."""
        # Verify statistical metrics are present and valid
        assert "min_duration_ms" in stats
        assert "max_duration_ms" in stats
        assert "avg_duration_ms" in stats
        assert "iterations" in stats

        min_duration = stats["min_duration_ms"]
        max_duration = stats["max_duration_ms"]
        avg_duration = stats["avg_duration_ms"]
        iterations = stats["iterations"]

        self._validate_duration_relationships(
            min_duration, max_duration, avg_duration, iterations
        )
        self._validate_statistical_variation(min_duration, max_duration, avg_duration)

    def _validate_duration_relationships(
        self, min_dur: float, max_dur: float, avg_dur: float, iterations: int
    ):
        """Validate duration relationships and iteration count."""
        assert min_dur <= avg_dur <= max_dur

        # Calculate expected trimmed count using same logic as benchmark_stream
        original_iterations = 10
        trim_percent = 10.0
        trim_count = max(1, int(original_iterations * (trim_percent / 100)))
        if original_iterations > 2 * trim_count:
            expected_trimmed = original_iterations - 2 * trim_count
        else:
            expected_trimmed = max(1, original_iterations - 2)

        assert iterations == expected_trimmed
        assert min_dur > 0  # Should take some time
        assert max_dur > min_dur or min_dur == max_dur  # Allow equal if very fast

    def _validate_statistical_variation(
        self, min_dur: float, max_dur: float, avg_dur: float
    ):
        """Validate statistical variation is within reasonable bounds."""
        # Calculate coefficient of variation (standard deviation approximation)
        duration_range = max_dur - min_dur
        cv_approx = duration_range / avg_dur

        # Statistical analysis should show reasonable variation (< 100% CV)
        assert cv_approx >= 0
        assert cv_approx < 1.0  # Range shouldn't exceed average (reasonable variation)
