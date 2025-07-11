"""Performance monitoring utilities for Flow streams.

This module provides comprehensive performance monitoring, timing, and observability
tools for Flow stream processing pipelines.
"""

from __future__ import annotations

import json
import time
from collections.abc import AsyncGenerator, Awaitable, Callable
from dataclasses import dataclass, field
from typing import Any

from ..flow import Flow

# Optional import for memory tracking
_psutil_available = False
try:
    import psutil

    _psutil_available = True
except ImportError:
    psutil = None  # type: ignore[assignment]

# Type aliases for performance monitoring
PerformanceData = dict[str, Any]
AnyFlow = Flow[Any, Any]
AnyIteratorFactory = Callable[[], AsyncGenerator[Any, None]]
BenchmarkResult = dict[str, Any]


@dataclass
class FlowMetrics:
    """Performance metrics data class."""

    execution_count: int = 0
    total_duration: float = 0.0
    min_duration: float = float("inf")
    max_duration: float = 0.0
    error_count: int = 0
    name: str = "unknown"
    start_time: float = field(default_factory=time.time)
    end_time: float | None = None
    items_processed: int = 0
    items_yielded: int = 0
    errors: list[Exception] = field(default_factory=lambda: [])
    memory_usage_kb: float | None = None
    peak_memory_kb: float | None = None

    @property
    def average_duration(self) -> float:
        """Average execution duration."""
        if self.execution_count == 0:
            return 0.0
        return self.total_duration / self.execution_count

    @property
    def success_rate(self) -> float:
        """Success rate as percentage."""
        if self.execution_count == 0:
            return 0.0
        return (self.execution_count - self.error_count) / self.execution_count

    @property
    def duration_ms(self) -> float:
        """Total execution duration in milliseconds."""
        if self.end_time is None:
            return (time.time() - self.start_time) * 1000
        return (self.end_time - self.start_time) * 1000

    @property
    def throughput_items_per_sec(self) -> float:
        """Items processed per second."""
        duration_sec = self.duration_ms / 1000
        if duration_sec == 0:
            return 0.0
        return self.items_processed / duration_sec

    @property
    def yield_rate(self) -> float:
        """Ratio of items yielded to items processed."""
        if self.items_processed == 0:
            return 0.0
        return self.items_yielded / self.items_processed

    def record_execution(self, duration: float) -> None:
        """Record an execution with its duration."""
        self.execution_count += 1
        self.total_duration += duration
        self.min_duration = min(self.min_duration, duration)
        self.max_duration = max(self.max_duration, duration)

    def record_error(self, error: Exception) -> None:
        """Record an error."""
        self.error_count += 1
        self.errors.append(error)

    def reset(self) -> None:
        """Reset all metrics."""
        self.execution_count = 0
        self.total_duration = 0.0
        self.min_duration = float("inf")
        self.max_duration = 0.0
        self.error_count = 0
        self.items_processed = 0
        self.items_yielded = 0
        self.errors.clear()
        self.memory_usage_kb = None
        self.peak_memory_kb = None

    def to_dict(self) -> PerformanceData:
        """Convert metrics to dictionary for serialization."""
        return {
            "name": self.name,
            "execution_count": self.execution_count,
            "total_duration": self.total_duration,
            "average_duration": self.average_duration,
            "min_duration": (
                self.min_duration if self.min_duration != float("inf") else 0.0
            ),
            "max_duration": self.max_duration,
            "error_count": self.error_count,
            "success_rate": self.success_rate,
            "duration_ms": self.duration_ms,
            "items_processed": self.items_processed,
            "items_yielded": self.items_yielded,
            "throughput_items_per_sec": self.throughput_items_per_sec,
            "yield_rate": self.yield_rate,
            "errors": [str(e) for e in self.errors],
            "memory_usage_kb": self.memory_usage_kb,
            "peak_memory_kb": self.peak_memory_kb,
        }


class PerformanceMonitor:
    """Performance monitoring system."""

    def __init__(self) -> None:
        super().__init__()
        self.metrics: dict[str, FlowMetrics] = {}
        self.memory_tracking = False

    def start_monitoring(self, name: str) -> str:
        """Start monitoring a flow execution."""
        metrics_id = f"{name}_{int(time.time() * 1000)}"
        self.metrics[metrics_id] = FlowMetrics(name=name, start_time=time.time())
        return metrics_id

    def stop_monitoring(self, metrics_id: str) -> FlowMetrics:
        """Stop monitoring and return metrics."""
        if metrics_id in self.metrics:
            metrics = self.metrics[metrics_id]
            metrics.end_time = time.time()
            return metrics
        return FlowMetrics(name="unknown", start_time=time.time(), end_time=time.time())

    def get_metrics(self, metrics_id: str) -> FlowMetrics | None:
        """Get metrics for a specific monitoring session."""
        return self.metrics.get(metrics_id)

    def reset_metrics(self) -> None:
        """Reset all metrics."""
        self.metrics.clear()

    def export_metrics(self, filepath: str) -> None:
        """Export metrics to a file."""
        export_data = {
            "summary": self.get_summary_stats(),
            "individual_flows": {
                metrics_id: metrics.to_dict()
                for metrics_id, metrics in self.metrics.items()
            },
        }
        with open(filepath, "w") as f:
            json.dump(export_data, f, indent=2)

    def record_item_processed(self, metrics_id: str) -> None:
        """Record that an item was processed."""
        if metrics_id in self.metrics:
            self.metrics[metrics_id].items_processed += 1

    def record_item_yielded(self, metrics_id: str) -> None:
        """Record that an item was yielded."""
        if metrics_id in self.metrics:
            self.metrics[metrics_id].items_yielded += 1

    def record_error(self, metrics_id: str, error: Exception) -> None:
        """Record an error during execution."""
        if metrics_id in self.metrics:
            self.metrics[metrics_id].record_error(error)

    def record_memory_usage(self, metrics_id: str) -> None:
        """Record current memory usage."""
        if (
            not self.memory_tracking
            or metrics_id not in self.metrics
            or not _psutil_available
        ):
            return
        try:
            process = psutil.Process()  # pyright: ignore[reportOptionalMemberAccess]
            memory_info = process.memory_info()
            current_usage = memory_info.rss / 1024
            metrics = self.metrics[metrics_id]
            metrics.memory_usage_kb = current_usage
            if metrics.peak_memory_kb is None or current_usage > metrics.peak_memory_kb:
                metrics.peak_memory_kb = current_usage
        except Exception:
            pass

    def get_summary_stats(self) -> PerformanceData:
        """Get summary statistics across all monitored flows."""
        if not self.metrics:
            return {"message": "No metrics collected yet"}

        durations = [m.duration_ms for m in self.metrics.values()]
        throughputs = [m.throughput_items_per_sec for m in self.metrics.values()]
        yield_rates = [m.yield_rate for m in self.metrics.values()]

        def stats(values: list[float]) -> dict[str, float]:
            if not values:
                return {"min": 0, "max": 0, "avg": 0, "count": 0}
            return {
                "min": min(values),
                "max": max(values),
                "avg": sum(values) / len(values),
                "count": len(values),
            }

        return {
            "duration_ms": stats(durations),
            "throughput_items_per_sec": stats(throughputs),
            "yield_rate": stats(yield_rates),
            "total_flows_monitored": len(self.metrics),
        }


# Global performance monitor instance
_performance_monitor = PerformanceMonitor()


def monitored_stream(
    name: str | None = None,
) -> Callable[[Callable[[], AnyFlow]], AnyFlow]:
    """Add monitoring to stream."""

    def decorator(flow_factory: Callable[[], AnyFlow]) -> AnyFlow:
        flow = flow_factory()
        monitor_name = name or flow.name

        async def _monitored_flow(
            stream: AsyncGenerator[Any, None],
        ) -> AsyncGenerator[Any, None]:
            metrics_id = _performance_monitor.start_monitoring(monitor_name)
            try:
                async for item in flow(stream):
                    _performance_monitor.record_item_processed(metrics_id)
                    _performance_monitor.record_memory_usage(metrics_id)
                    yield item
                    _performance_monitor.record_item_yielded(metrics_id)
            except Exception as e:
                _performance_monitor.record_error(metrics_id, e)
                raise
            finally:
                _performance_monitor.stop_monitoring(metrics_id)

        return Flow(_monitored_flow, name=f"monitored({monitor_name})")

    return decorator


def performance_stream() -> AnyFlow:
    """Performance measurement wrapper."""

    async def _flow(stream: AsyncGenerator[Any, None]) -> AsyncGenerator[Any, None]:
        metrics_id = _performance_monitor.start_monitoring("performance_stream")
        try:
            async for item in stream:
                _performance_monitor.record_item_processed(metrics_id)
                _performance_monitor.record_memory_usage(metrics_id)
                yield item
                _performance_monitor.record_item_yielded(metrics_id)
        except Exception as e:
            _performance_monitor.record_error(metrics_id, e)
            raise
        finally:
            _performance_monitor.stop_monitoring(metrics_id)

    return Flow(_flow, name="performance")


def benchmark_stream(
    iterations: int = 100,
    warmup_iterations: int = 5,
    trim_percent: float = 10.0,
) -> Callable[[AnyFlow], Callable[[AnyIteratorFactory], Awaitable[BenchmarkResult]]]:
    """Benchmarking utilities with percentile-based outlier removal for stable measurements."""

    def benchmark_func(
        flow: AnyFlow,
    ) -> Callable[[AnyIteratorFactory], Awaitable[BenchmarkResult]]:
        async def run_benchmark(
            test_stream_factory: AnyIteratorFactory,
        ) -> BenchmarkResult:
            import statistics

            # More warmup iterations to stabilize performance
            for _ in range(warmup_iterations):
                test_stream = test_stream_factory()
                async for _ in flow(test_stream):
                    pass

            durations: list[float] = []
            for _ in range(iterations):
                test_stream = test_stream_factory()

                # Use high-precision timing
                start_time = time.perf_counter()
                async for _ in flow(test_stream):
                    pass
                duration_ms = (time.perf_counter() - start_time) * 1000
                durations.append(duration_ms)

            # Sort durations for percentile-based trimming
            durations.sort()

            # Calculate trim indices (remove top and bottom trim_percent)
            trim_count = max(1, int(len(durations) * (trim_percent / 100)))

            # Keep middle percentiles, removing outliers from both ends
            if len(durations) > 2 * trim_count:
                trimmed_durations = durations[trim_count:-trim_count]
            else:
                # If we don't have enough samples, just remove the most extreme outliers
                trimmed_durations = durations[1:-1] if len(durations) > 2 else durations

            # Calculate statistics from trimmed data
            min_duration = min(trimmed_durations)
            max_duration = max(trimmed_durations)
            avg_duration = statistics.mean(trimmed_durations)

            return {
                "flow_name": flow.name,
                "iterations": len(trimmed_durations),  # Report actual samples used
                "min_duration_ms": min_duration,
                "max_duration_ms": max_duration,
                "avg_duration_ms": avg_duration,
                "original_iterations": len(durations),  # Include original count
                "trim_percent": trim_percent,
            }

        return run_benchmark

    return benchmark_func


def get_performance_monitor() -> PerformanceMonitor:
    """Global monitor access."""
    return _performance_monitor


def enable_memory_tracking() -> None:
    """Memory usage tracking."""
    if _psutil_available:
        _performance_monitor.memory_tracking = True


def get_performance_summary() -> PerformanceData:
    """Summary statistics."""
    return _performance_monitor.get_summary_stats()


def export_performance_metrics(format_type: str) -> PerformanceData:
    """Export in various formats."""
    _ = format_type  # Future formats will use this parameter
    return _performance_monitor.get_summary_stats()


def memory_profile_stream() -> AnyFlow:
    """Memory profiling."""

    async def _flow(stream: AsyncGenerator[Any, None]) -> AsyncGenerator[Any, None]:
        metrics_id = _performance_monitor.start_monitoring("memory_profile")
        enable_memory_tracking()
        try:
            async for item in stream:
                _performance_monitor.record_memory_usage(metrics_id)
                yield item
        finally:
            _performance_monitor.stop_monitoring(metrics_id)

    return Flow(_flow, name="memory_profile")
