"""Tests for performance monitoring utilities."""

import asyncio
import time
from collections.abc import AsyncGenerator
from typing import Any, Generator
from unittest.mock import mock_open, patch

import pytest

from flow.flow import Flow
from flow.observability.performance import (
    FlowMetrics,
    PerformanceMonitor,
    benchmark_stream,
    enable_memory_tracking,
    export_performance_metrics,
    get_performance_monitor,
    get_performance_summary,
    memory_profile_stream,
    monitored_stream,
    performance_stream,
)


@pytest.fixture(autouse=True)
def reset_global_performance_monitor() -> Generator[None, None, None]:
    """Reset the global performance monitor before each test to prevent interference."""
    monitor = get_performance_monitor()
    monitor.reset_metrics()
    yield
    # Optionally reset after test as well
    monitor.reset_metrics()


def get_mock_flow_metrics(overrides: dict[str, Any] | None = None) -> FlowMetrics:
    """Factory for creating test FlowMetrics instances."""
    base = _get_base_metrics_dict()
    if overrides:
        base.update(overrides)
    return FlowMetrics(**base)


def _get_base_metrics_dict() -> dict[str, Any]:
    """Get base metrics dictionary."""
    return {
        "name": "test_flow",
        "start_time": time.time(),
        "end_time": None,
        "items_processed": 0,
        "items_yielded": 0,
        "errors": [],
        "memory_usage_kb": None,
        "peak_memory_kb": None,
    }


async def async_range(n: int) -> AsyncGenerator[int, None]:
    """Generate async range for testing."""
    for i in range(n):
        yield i
        await asyncio.sleep(0.001)  # Small delay to make timing measurable


class TestFlowMetrics:
    """Test FlowMetrics class functionality."""

    def test_flow_metrics_creation(self) -> None:
        """Test that FlowMetrics can be created with required fields."""
        start_time = time.time()
        metrics = FlowMetrics(name="test", start_time=start_time)

        assert metrics.name == "test"
        assert metrics.start_time == start_time
        assert metrics.end_time is None
        assert metrics.items_processed == 0
        assert metrics.items_yielded == 0
        assert metrics.errors == []
        assert metrics.memory_usage_kb is None
        assert metrics.peak_memory_kb is None

    def test_duration_ms_active_execution(self) -> None:
        """Test duration calculation for ongoing execution."""
        start_time = time.time()
        metrics = get_mock_flow_metrics({"start_time": start_time})

        # Duration should be positive and reasonable
        duration = metrics.duration_ms
        assert duration >= 0
        assert duration < 1000  # Should be less than 1 second for this test

    def test_duration_ms_completed_execution(self) -> None:
        """Test duration calculation for completed execution."""
        start_time = time.time()
        end_time = start_time + 0.5  # 500ms execution
        metrics = get_mock_flow_metrics(
            {"start_time": start_time, "end_time": end_time}
        )

        expected_duration = 500.0
        assert abs(metrics.duration_ms - expected_duration) < 1.0

    def test_throughput_items_per_sec_zero_duration(self) -> None:
        """Test throughput calculation with zero duration."""
        start_time = time.time()
        metrics = get_mock_flow_metrics(
            {
                "start_time": start_time,
                "end_time": start_time,  # Zero duration
                "items_processed": 10,
            }
        )

        assert metrics.throughput_items_per_sec == 0.0

    def test_throughput_items_per_sec_normal_execution(self) -> None:
        """Test throughput calculation with normal execution."""
        start_time = time.time()
        end_time = start_time + 1.0  # 1 second execution
        metrics = get_mock_flow_metrics(
            {"start_time": start_time, "end_time": end_time, "items_processed": 100}
        )

        expected_throughput = 100.0  # 100 items per second
        assert abs(metrics.throughput_items_per_sec - expected_throughput) < 0.1

    def test_yield_rate_zero_processed(self) -> None:
        """Test yield rate calculation with zero items processed."""
        metrics = get_mock_flow_metrics({"items_processed": 0, "items_yielded": 0})

        assert metrics.yield_rate == 0.0

    def test_yield_rate_normal_execution(self) -> None:
        """Test yield rate calculation with normal execution."""
        metrics = get_mock_flow_metrics({"items_processed": 100, "items_yielded": 80})

        expected_rate = 0.8  # 80% yield rate
        assert abs(metrics.yield_rate - expected_rate) < 0.01

    def test_yield_rate_full_yield(self) -> None:
        """Test yield rate calculation with 100% yield."""
        metrics = get_mock_flow_metrics({"items_processed": 50, "items_yielded": 50})

        assert metrics.yield_rate == 1.0

    def test_to_dict_serialization(self) -> None:
        """Test conversion to dictionary for serialization."""
        metrics = self._create_test_metrics_with_error()
        result = metrics.to_dict()
        self._assert_complete_serialization(result)

    def _create_test_metrics_with_error(self) -> FlowMetrics:
        """Create test metrics with comprehensive data."""
        start_time = time.time()
        end_time = start_time + 2.0
        test_error = ValueError("test error")

        metrics = get_mock_flow_metrics(
            {
                "name": "test_flow",
                "start_time": start_time,
                "end_time": end_time,
                "items_processed": 200,
                "items_yielded": 180,
                "memory_usage_kb": 1024.0,
                "peak_memory_kb": 2048.0,
            }
        )
        metrics.record_error(test_error)
        return metrics

    def _assert_complete_serialization(
        self, result: dict[str, float | int | str | list[str]]
    ) -> None:
        """Assert that all fields are correctly serialized."""
        assert result["name"] == "test_flow"
        assert result["items_processed"] == 200
        assert result["items_yielded"] == 180
        assert result["error_count"] == 1
        assert result["errors"] == ["test error"]
        assert result["memory_usage_kb"] == 1024.0
        assert result["peak_memory_kb"] == 2048.0
        self._assert_numeric_fields(result)

    def _assert_numeric_fields(
        self, result: dict[str, float | int | str | list[str]]
    ) -> None:
        """Assert numeric fields with proper type checking."""
        self._assert_duration_field(result)
        self._assert_throughput_field(result)
        self._assert_yield_rate_field(result)

    def _assert_duration_field(
        self, result: dict[str, float | int | str | list[str]]
    ) -> None:
        """Assert duration field is correct."""
        duration_ms = result["duration_ms"]
        assert isinstance(duration_ms, (float, int))
        assert abs(float(duration_ms) - 2000.0) < 1.0

    def _assert_throughput_field(
        self, result: dict[str, float | int | str | list[str]]
    ) -> None:
        """Assert throughput field is correct."""
        throughput = result["throughput_items_per_sec"]
        assert isinstance(throughput, (float, int))
        assert abs(float(throughput) - 100.0) < 0.1

    def _assert_yield_rate_field(
        self, result: dict[str, float | int | str | list[str]]
    ) -> None:
        """Assert yield rate field is correct."""
        yield_rate = result["yield_rate"]
        assert isinstance(yield_rate, (float, int))
        assert abs(float(yield_rate) - 0.9) < 0.01

    def test_to_dict_minimal_data(self) -> None:
        """Test dictionary conversion with minimal data."""
        start_time = time.time()
        metrics = get_mock_flow_metrics({"start_time": start_time})
        result = metrics.to_dict()
        self._assert_minimal_data_fields(result)

    def _assert_minimal_data_fields(self, result: dict[str, Any]) -> None:
        """Assert minimal data fields are present with defaults."""
        assert "name" in result
        assert "duration_ms" in result
        assert result["items_processed"] == 0
        assert result["items_yielded"] == 0
        assert result["throughput_items_per_sec"] == 0.0
        assert result["yield_rate"] == 0.0
        assert result["error_count"] == 0
        assert result["errors"] == []
        assert result["memory_usage_kb"] is None
        assert result["peak_memory_kb"] is None

    def test_error_list_handling(self) -> None:
        """Test that error list is properly handled."""
        error1 = ValueError("first error")
        error2 = RuntimeError("second error")

        metrics = get_mock_flow_metrics()
        # Record the errors to increment error_count
        metrics.record_error(error1)
        metrics.record_error(error2)

        result = metrics.to_dict()
        assert result["error_count"] == 2
        assert "first error" in result["errors"]
        assert "second error" in result["errors"]

    def test_memory_tracking_fields(self) -> None:
        """Test memory tracking field handling."""
        metrics = get_mock_flow_metrics(
            {"memory_usage_kb": 512.5, "peak_memory_kb": 1024.7}
        )

        result = metrics.to_dict()
        assert result["memory_usage_kb"] == 512.5
        assert result["peak_memory_kb"] == 1024.7

    def test_to_dict_includes_new_fields(self) -> None:
        """Test that to_dict includes all new fields from migration spec."""
        metrics = self._create_metrics_with_executions()
        result = metrics.to_dict()
        self._assert_migration_spec_fields(result)

    def _create_metrics_with_executions(self) -> FlowMetrics:
        """Create metrics with execution data."""
        start_time = time.time()
        metrics = get_mock_flow_metrics({"start_time": start_time})
        metrics.record_execution(100.0)
        metrics.record_execution(200.0)
        return metrics

    def _assert_migration_spec_fields(self, result: dict[str, Any]) -> None:
        """Assert migration spec fields are present."""
        assert "execution_count" in result
        assert "total_duration" in result
        assert "average_duration" in result
        assert "min_duration" in result
        assert "max_duration" in result
        assert "success_rate" in result
        self._assert_execution_values(result)

    def _assert_execution_values(self, result: dict[str, Any]) -> None:
        """Assert execution values are correct."""
        assert result["execution_count"] == 2
        assert result["total_duration"] == 300.0
        assert result["average_duration"] == 150.0
        assert result["min_duration"] == 100.0
        assert result["max_duration"] == 200.0
        assert result["success_rate"] == 1.0

    def test_execution_count_tracking(self) -> None:
        """Test execution count tracking."""
        metrics = get_mock_flow_metrics()
        assert metrics.execution_count == 0

        metrics.record_execution(100.0)
        assert metrics.execution_count == 1
        assert metrics.total_duration == 100.0

        metrics.record_execution(200.0)
        assert metrics.execution_count == 2
        assert metrics.total_duration == 300.0

    def test_average_duration_calculation(self) -> None:
        """Test average duration calculation."""
        metrics = get_mock_flow_metrics()
        assert metrics.average_duration == 0.0

        metrics.record_execution(100.0)
        assert metrics.average_duration == 100.0

        metrics.record_execution(200.0)
        assert metrics.average_duration == 150.0

    def test_success_rate_calculation(self) -> None:
        """Test success rate calculation."""
        metrics = get_mock_flow_metrics()
        assert metrics.success_rate == 0.0

        metrics.record_execution(100.0)
        assert metrics.success_rate == 1.0

        metrics.record_error(ValueError("test error"))
        assert metrics.success_rate == 0.0

    def test_min_max_duration_tracking(self) -> None:
        """Test min/max duration tracking."""
        metrics = get_mock_flow_metrics()
        assert metrics.min_duration == float("inf")
        assert metrics.max_duration == 0.0

        metrics.record_execution(100.0)
        assert metrics.min_duration == 100.0
        assert metrics.max_duration == 100.0

        metrics.record_execution(50.0)
        assert metrics.min_duration == 50.0
        assert metrics.max_duration == 100.0

        metrics.record_execution(200.0)
        assert metrics.min_duration == 50.0
        assert metrics.max_duration == 200.0

    def test_reset_functionality(self) -> None:
        """Test metrics reset functionality."""
        metrics = self._setup_metrics_with_data()
        metrics.reset()
        self._assert_reset_state(metrics)

    def _setup_metrics_with_data(self) -> FlowMetrics:
        """Setup metrics with test data."""
        metrics = get_mock_flow_metrics()
        metrics.record_execution(100.0)
        metrics.record_error(ValueError("test error"))
        metrics.items_processed = 10
        metrics.items_yielded = 8
        return metrics

    def _assert_reset_state(self, metrics: FlowMetrics) -> None:
        """Assert metrics are in reset state."""
        assert metrics.execution_count == 0
        assert metrics.total_duration == 0.0
        assert metrics.min_duration == float("inf")
        assert metrics.max_duration == 0.0
        assert metrics.error_count == 0
        assert metrics.items_processed == 0
        assert metrics.items_yielded == 0
        assert len(metrics.errors) == 0


class TestPerformanceMonitor:
    """Test PerformanceMonitor class functionality."""

    def test_monitor_creation(self) -> None:
        """Test monitor creation."""
        monitor = PerformanceMonitor()
        assert len(monitor.metrics) == 0
        assert not monitor.memory_tracking

    def test_start_stop_monitoring(self) -> None:
        """Test start and stop monitoring."""
        monitor = PerformanceMonitor()
        metrics_id = monitor.start_monitoring("test_flow")

        assert metrics_id in monitor.metrics
        assert monitor.metrics[metrics_id].name == "test_flow"

        metrics = monitor.stop_monitoring(metrics_id)
        assert metrics.end_time is not None

    def test_get_metrics(self) -> None:
        """Test get_metrics functionality."""
        monitor = PerformanceMonitor()
        metrics_id = monitor.start_monitoring("test_flow")

        retrieved_metrics = monitor.get_metrics(metrics_id)
        assert retrieved_metrics is not None
        assert retrieved_metrics.name == "test_flow"

        assert monitor.get_metrics("nonexistent") is None

    def test_reset_metrics(self) -> None:
        """Test reset_metrics functionality."""
        monitor = PerformanceMonitor()
        monitor.start_monitoring("test_flow")

        assert len(monitor.metrics) == 1
        monitor.reset_metrics()
        assert len(monitor.metrics) == 0

    def test_record_item_processed(self) -> None:
        """Test record_item_processed functionality."""
        monitor = PerformanceMonitor()
        metrics_id = monitor.start_monitoring("test_flow")

        monitor.record_item_processed(metrics_id)
        assert monitor.metrics[metrics_id].items_processed == 1

        monitor.record_item_processed(metrics_id)
        assert monitor.metrics[metrics_id].items_processed == 2

    def test_record_item_yielded(self) -> None:
        """Test record_item_yielded functionality."""
        monitor = PerformanceMonitor()
        metrics_id = monitor.start_monitoring("test_flow")

        monitor.record_item_yielded(metrics_id)
        assert monitor.metrics[metrics_id].items_yielded == 1

    def test_record_error(self) -> None:
        """Test record_error functionality."""
        monitor = PerformanceMonitor()
        metrics_id = monitor.start_monitoring("test_flow")

        test_error = ValueError("test error")
        monitor.record_error(metrics_id, test_error)

        assert monitor.metrics[metrics_id].error_count == 1
        assert test_error in monitor.metrics[metrics_id].errors

    def test_get_summary_stats_empty(self) -> None:
        """Test get_summary_stats with no metrics."""
        monitor = PerformanceMonitor()
        stats = monitor.get_summary_stats()
        assert "message" in stats
        assert stats["message"] == "No metrics collected yet"

    def test_get_summary_stats_with_data(self) -> None:
        """Test get_summary_stats with metrics."""
        monitor = self._create_monitor_with_data()
        stats = monitor.get_summary_stats()
        self._assert_summary_stats_fields(stats)

    def _create_monitor_with_data(self) -> PerformanceMonitor:
        """Create monitor with test data."""
        monitor = PerformanceMonitor()
        metrics_id = monitor.start_monitoring("test_flow")
        monitor.record_item_processed(metrics_id)
        monitor.record_item_yielded(metrics_id)
        time.sleep(0.1)  # Small delay
        monitor.stop_monitoring(metrics_id)
        return monitor

    def _assert_summary_stats_fields(self, stats: dict[str, Any]) -> None:
        """Assert summary stats have required fields."""
        assert "duration_ms" in stats
        assert "throughput_items_per_sec" in stats
        assert "yield_rate" in stats
        assert "total_flows_monitored" in stats
        assert stats["total_flows_monitored"] == 1

    @patch("builtins.open", new_callable=mock_open)
    @patch("json.dump")
    def test_export_metrics(self, mock_json_dump: Any, mock_file: Any) -> None:
        """Test export_metrics functionality."""
        monitor = PerformanceMonitor()
        metrics_id = monitor.start_monitoring("test_flow")
        monitor.stop_monitoring(metrics_id)

        monitor.export_metrics("test_export.json")

        mock_file.assert_called_once_with("test_export.json", "w")
        mock_json_dump.assert_called_once()


class TestPerformanceFunctions:
    """Test standalone performance functions."""

    def test_get_performance_monitor(self) -> None:
        """Test get_performance_monitor function."""
        monitor = get_performance_monitor()
        assert isinstance(monitor, PerformanceMonitor)

    def test_get_performance_summary(self) -> None:
        """Test get_performance_summary function."""
        summary = get_performance_summary()
        assert isinstance(summary, dict)

    def test_export_performance_metrics(self) -> None:
        """Test export_performance_metrics function."""
        result = export_performance_metrics("json")
        assert isinstance(result, dict)

    def test_enable_memory_tracking(self) -> None:
        """Test enable_memory_tracking function."""
        # This function doesn't raise errors even if psutil is not available
        enable_memory_tracking()
        # Just verify it doesn't crash
        assert True


class TestFlowIntegration:
    """Test integration with Flow class."""

    @pytest.mark.asyncio
    async def test_monitored_stream_decorator(self) -> None:
        """Test monitored_stream decorator."""

        # Create a base flow first
        async def _flow(stream: AsyncGenerator[Any, None]) -> AsyncGenerator[Any, None]:
            async for item in stream:
                yield item * 2

        base_flow = Flow(_flow, name="test_flow")

        # Use monitored_stream decorator
        @monitored_stream("test_monitored")
        def create_test_flow() -> Any:
            return base_flow

        monitored_flow = create_test_flow
        assert "monitored" in monitored_flow.name

        # Test execution
        result: list[int] = []
        async for item in monitored_flow(async_range(3)):
            result.append(item)

        assert result == [0, 2, 4]

    @pytest.mark.asyncio
    async def test_performance_stream(self) -> None:
        """Test performance_stream function."""
        perf_flow = performance_stream()
        assert perf_flow.name == "performance"

        # Test execution
        result: list[int] = []
        async for item in perf_flow(async_range(3)):
            result.append(item)

        assert result == [0, 1, 2]

    @pytest.mark.asyncio
    async def test_memory_profile_stream(self) -> None:
        """Test memory_profile_stream function."""
        mem_flow = memory_profile_stream()
        assert mem_flow.name == "memory_profile"

        # Test execution
        result: list[int] = []
        async for item in mem_flow(async_range(3)):
            result.append(item)

        assert result == [0, 1, 2]

    @pytest.mark.asyncio
    async def test_benchmark_stream(self) -> None:
        """Test benchmark_stream function."""
        test_flow = self._create_simple_test_flow()
        result = await self._run_benchmark_test(test_flow)
        self._assert_benchmark_result(result)

    def _create_simple_test_flow(self) -> Any:
        """Create a simple test flow for benchmarking."""

        async def simple_flow(
            stream: AsyncGenerator[Any, None],
        ) -> AsyncGenerator[Any, None]:
            async for item in stream:
                yield item * 2

        return Flow(simple_flow, name="test_flow")

    async def _run_benchmark_test(self, test_flow: Any) -> Any:
        """Run the benchmark test and return results."""
        benchmark_func = benchmark_stream(iterations=5)
        run_benchmark = benchmark_func(test_flow)

        def test_stream_factory() -> Any:
            return async_range(10)

        return await run_benchmark(test_stream_factory)

    def _assert_benchmark_result(self, result: Any) -> None:
        """Assert benchmark result contains expected fields."""
        self._assert_result_has_required_fields(result)
        self._assert_result_values_are_valid(result)

    def _assert_result_has_required_fields(self, result: Any) -> None:
        """Assert result has all required fields."""
        assert "flow_name" in result
        assert "iterations" in result
        assert "min_duration_ms" in result
        assert "max_duration_ms" in result
        assert "avg_duration_ms" in result

    def _assert_result_values_are_valid(self, result: Any) -> None:
        """Assert result values are valid."""
        assert result["flow_name"] == "test_flow"

        # Calculate expected trimmed count using same logic as benchmark_stream
        original_iterations = 5
        trim_percent = 10.0
        trim_count = max(1, int(original_iterations * (trim_percent / 100)))
        if original_iterations > 2 * trim_count:
            expected_trimmed = original_iterations - 2 * trim_count
        else:
            expected_trimmed = max(
                1, original_iterations - 2
            )  # Remove most extreme outliers

        assert result["original_iterations"] == original_iterations
        assert result["iterations"] == expected_trimmed
        assert result["min_duration_ms"] >= 0
        assert result["max_duration_ms"] >= result["min_duration_ms"]
        assert result["avg_duration_ms"] >= result["min_duration_ms"]


class TestErrorHandling:
    """Test error handling in performance monitoring."""

    def test_stop_monitoring_nonexistent(self) -> None:
        """Test stop_monitoring with nonexistent ID."""
        monitor = PerformanceMonitor()
        metrics = monitor.stop_monitoring("nonexistent")
        assert metrics.name == "unknown"
        assert metrics.end_time is not None

    def test_record_operations_nonexistent(self) -> None:
        """Test record operations with nonexistent ID."""
        monitor = PerformanceMonitor()

        # These should not raise errors
        monitor.record_item_processed("nonexistent")
        monitor.record_item_yielded("nonexistent")
        monitor.record_error("nonexistent", ValueError("test"))
        monitor.record_memory_usage("nonexistent")

        # No metrics should be created
        assert len(monitor.metrics) == 0

    def test_memory_tracking_import_error(self) -> None:
        """Test memory tracking when psutil is not available."""
        monitor = PerformanceMonitor()
        metrics_id = monitor.start_monitoring("test")

        # Memory tracking should work normally or fail silently
        enable_memory_tracking()  # Use public API instead
        monitor.record_memory_usage(metrics_id)

        # Should not crash - memory may or may not be None depending on psutil availability
        assert True  # Just verify no exception is raised

    @pytest.mark.asyncio
    async def test_monitored_stream_error_handling(self) -> None:
        """Test error handling in monitored streams."""
        error_flow = self._create_error_flow()

        with pytest.raises(ValueError):
            async for item in error_flow(async_range(5)):
                pass

        self._assert_error_was_recorded()

    def _create_error_flow(self) -> Any:
        """Create an error flow for testing."""
        base_error_flow = self._create_base_error_flow()
        return self._wrap_with_monitoring(base_error_flow)

    def _create_base_error_flow(self) -> Any:
        """Create the base error flow."""
        return Flow(self._error_flow_function, name="error_flow")

    async def _error_flow_function(
        self, stream: AsyncGenerator[Any, None]
    ) -> AsyncGenerator[Any, None]:
        """Error flow function that raises on item 2."""
        async for item in stream:
            if item == 2:
                raise ValueError("Test error")
            yield item

    def _wrap_with_monitoring(self, base_flow: Any) -> Any:
        """Wrap flow with monitoring decorator."""

        @monitored_stream("error_test")
        def create_error_flow() -> Any:
            return base_flow

        return create_error_flow

    def _assert_error_was_recorded(self) -> None:
        """Assert that error was recorded in monitoring."""
        monitor = get_performance_monitor()
        error_metrics = None
        for metrics in monitor.metrics.values():
            if "error_test" in metrics.name:
                error_metrics = metrics
                break

        assert error_metrics is not None
        assert error_metrics.error_count > 0
