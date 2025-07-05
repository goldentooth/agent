"""Tests for performance monitoring utilities."""

import time
from typing import Any
from unittest.mock import patch

import pytest

from flowengine.observability.performance import FlowMetrics


def get_mock_flow_metrics(overrides: dict[str, Any] | None = None) -> FlowMetrics:
    """Factory for creating test FlowMetrics instances."""
    base: dict[str, Any] = {
        "name": "test_flow",
        "start_time": time.time(),
        "end_time": None,
        "items_processed": 0,
        "items_yielded": 0,
        "errors": [],
        "memory_usage_kb": None,
        "peak_memory_kb": None,
    }
    if overrides:
        base.update(overrides)
    return FlowMetrics(**base)


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
                "errors": [test_error],
                "memory_usage_kb": 1024.0,
                "peak_memory_kb": 2048.0,
            }
        )

        result = metrics.to_dict()
        self._assert_complete_serialization(result)

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
        duration_ms = result["duration_ms"]
        assert isinstance(duration_ms, (float, int))
        assert abs(float(duration_ms) - 2000.0) < 1.0

        throughput = result["throughput_items_per_sec"]
        assert isinstance(throughput, (float, int))
        assert abs(float(throughput) - 100.0) < 0.1

        yield_rate = result["yield_rate"]
        assert isinstance(yield_rate, (float, int))
        assert abs(float(yield_rate) - 0.9) < 0.01

    def test_to_dict_minimal_data(self) -> None:
        """Test dictionary conversion with minimal data."""
        start_time = time.time()
        metrics = get_mock_flow_metrics({"start_time": start_time})

        result = metrics.to_dict()

        # Check that all fields are present with default values
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

        metrics = get_mock_flow_metrics({"errors": [error1, error2]})

        result = metrics.to_dict()
        assert result["error_count"] == 2
        assert result["errors"] == ["first error", "second error"]

    def test_memory_tracking_fields(self) -> None:
        """Test memory tracking field handling."""
        metrics = get_mock_flow_metrics(
            {"memory_usage_kb": 512.5, "peak_memory_kb": 1024.7}
        )

        result = metrics.to_dict()
        assert result["memory_usage_kb"] == 512.5
        assert result["peak_memory_kb"] == 1024.7
