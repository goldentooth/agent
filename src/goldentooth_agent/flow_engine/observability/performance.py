"""Performance monitoring utilities for Flow streams.

This module provides comprehensive performance monitoring, timing, and observability
tools for Flow stream processing pipelines.
"""

from __future__ import annotations

import json
import time
from collections import defaultdict
from collections.abc import AsyncIterator, Awaitable, Callable
from dataclasses import dataclass, field
from typing import Any

from ..main import Flow

# Type aliases for performance monitoring
PerformanceData = dict[str, Any]
AnyFlow = Flow[Any, Any]
StatsList = list[Any]
AnyIteratorFactory = Callable[[], AsyncIterator[Any]]
BenchmarkResult = dict[str, Any]


@dataclass
class FlowMetrics:
    """Metrics collected for a Flow execution."""

    name: str
    start_time: float
    end_time: float | None = None
    items_processed: int = 0
    items_yielded: int = 0
    errors: list[Exception] = field(default_factory=list)
    memory_usage_kb: float | None = None
    peak_memory_kb: float | None = None

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

    def to_dict(self) -> PerformanceData:
        """Convert metrics to dictionary for serialization."""
        return {
            "name": self.name,
            "duration_ms": self.duration_ms,
            "items_processed": self.items_processed,
            "items_yielded": self.items_yielded,
            "throughput_items_per_sec": self.throughput_items_per_sec,
            "yield_rate": self.yield_rate,
            "error_count": len(self.errors),
            "errors": [str(e) for e in self.errors],
            "memory_usage_kb": self.memory_usage_kb,
            "peak_memory_kb": self.peak_memory_kb,
        }


class PerformanceMonitor:
    """Performance monitoring system for Flow executions."""

    def __init__(self) -> None:
        self.metrics: dict[str, FlowMetrics] = {}
        self.global_stats: defaultdict[str, StatsList] = defaultdict(list)
        self._memory_tracking = False

    def enable_memory_tracking(self) -> None:
        """Enable memory usage tracking (requires psutil)."""
        try:
            import psutil

            self._psutil = psutil  # Store reference for potential future use
            self._memory_tracking = True
        except ImportError:
            print("Warning: psutil not available, memory tracking disabled")

    def start_monitoring(self, flow_name: str) -> str:
        """Start monitoring a flow execution."""
        metrics_id = f"{flow_name}_{int(time.time() * 1000)}"
        self.metrics[metrics_id] = FlowMetrics(name=flow_name, start_time=time.time())
        return metrics_id

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
            self.metrics[metrics_id].errors.append(error)

    def record_memory_usage(self, metrics_id: str) -> None:
        """Record current memory usage."""
        if not self._memory_tracking or metrics_id not in self.metrics:
            return

        try:
            import psutil

            process = psutil.Process()
            memory_info = process.memory_info()
            current_usage = memory_info.rss / 1024  # Convert to KB

            metrics = self.metrics[metrics_id]
            metrics.memory_usage_kb = current_usage
            if metrics.peak_memory_kb is None or current_usage > metrics.peak_memory_kb:
                metrics.peak_memory_kb = current_usage
        except Exception:
            pass  # Silently fail memory tracking

    def finish_monitoring(self, metrics_id: str) -> FlowMetrics:
        """Finish monitoring and return final metrics."""
        if metrics_id in self.metrics:
            metrics = self.metrics[metrics_id]
            metrics.end_time = time.time()

            # Update global stats
            self.global_stats["duration_ms"].append(metrics.duration_ms)
            self.global_stats["throughput"].append(metrics.throughput_items_per_sec)
            self.global_stats["yield_rate"].append(metrics.yield_rate)

            return metrics

        # Return empty metrics if not found
        return FlowMetrics(name="unknown", start_time=time.time(), end_time=time.time())

    def get_summary_stats(self) -> PerformanceData:
        """Get summary statistics across all monitored flows."""
        if not self.global_stats["duration_ms"]:
            return {"message": "No metrics collected yet"}

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
            "duration_ms": stats(self.global_stats["duration_ms"]),
            "throughput_items_per_sec": stats(self.global_stats["throughput"]),
            "yield_rate": stats(self.global_stats["yield_rate"]),
            "total_flows_monitored": len(self.metrics),
        }

    def export_metrics(self, filepath: str) -> None:
        """Export all metrics to a JSON file."""
        export_data = {
            "summary": self.get_summary_stats(),
            "individual_flows": {
                metrics_id: metrics.to_dict()
                for metrics_id, metrics in self.metrics.items()
            },
        }

        with open(filepath, "w") as f:
            json.dump(export_data, f, indent=2)


# Global performance monitor instance
_performance_monitor = PerformanceMonitor()


def monitored_stream(
    monitor_name: str | None = None,
) -> Callable[[Callable[[], AnyFlow]], AnyFlow]:
    """Decorator to add performance monitoring to a Flow.

    Args:
        monitor_name: Optional custom name for monitoring. Defaults to flow name.

    Returns:
        Decorated flow with performance monitoring.

    Example:
        @monitored_stream("my_pipeline")
        def my_flow():
            return Flow(...)
    """

    def decorator(flow_factory: Callable[[], AnyFlow]) -> AnyFlow:
        flow = flow_factory()
        name = monitor_name or flow.name

        async def _monitored_flow(stream: AsyncIterator[Any]) -> AsyncIterator[Any]:
            metrics_id = _performance_monitor.start_monitoring(name)

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
                metrics = _performance_monitor.finish_monitoring(metrics_id)
                # Optionally log metrics
                if metrics.duration_ms > 1000:  # Log slow operations
                    print(
                        f"Flow '{name}' took {metrics.duration_ms:.1f}ms, "
                        f"processed {metrics.items_processed} items"
                    )

        return Flow(_monitored_flow, name=f"monitored({name})")

    return decorator


def performance_stream() -> AnyFlow:
    """Create a flow that adds performance monitoring to the pipeline.

    This combinator automatically tracks timing, throughput, and memory usage
    for the stream processing without requiring decoration.

    Returns:
        A flow that monitors performance and passes items through unchanged.
    """

    async def _flow(stream: AsyncIterator[Any]) -> AsyncIterator[Any]:
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
            _performance_monitor.finish_monitoring(metrics_id)

    return Flow(_flow, name="performance")


def benchmark_stream(iterations: int = 100, warmup_iterations: int = 10) -> Callable[
    [AnyFlow],
    Callable[[AnyIteratorFactory], Awaitable[BenchmarkResult]],
]:
    """Benchmark a Flow's performance over multiple iterations.

    Args:
        iterations: Number of benchmark iterations to run
        warmup_iterations: Number of warmup iterations (not counted in results)

    Returns:
        Function that benchmarks the given flow and returns performance stats.

    Example:
        benchmark = benchmark_stream(iterations=1000)
        stats = await benchmark(my_flow)
        print(f"Average duration: {stats['avg_duration_ms']:.2f}ms")
    """

    def benchmark_func(
        flow: AnyFlow,
    ) -> Callable[[AnyIteratorFactory], Awaitable[BenchmarkResult]]:
        async def run_benchmark(
            test_stream_factory: AnyIteratorFactory,
        ) -> BenchmarkResult:
            """Run the benchmark with a test stream factory."""
            durations = []

            # Warmup
            for _ in range(warmup_iterations):
                test_stream = test_stream_factory()
                start_time = time.time()
                async for _ in flow(test_stream):
                    pass
                # Don't record warmup times

            # Actual benchmark
            for _ in range(iterations):
                test_stream = test_stream_factory()
                start_time = time.time()
                item_count = 0
                async for _ in flow(test_stream):
                    item_count += 1
                duration_ms = (time.time() - start_time) * 1000
                durations.append(duration_ms)

            # Calculate statistics
            min_duration = min(durations)
            max_duration = max(durations)
            avg_duration = sum(durations) / len(durations)

            # Calculate percentiles
            sorted_durations = sorted(durations)
            p50 = sorted_durations[len(sorted_durations) // 2]
            p95 = sorted_durations[int(len(sorted_durations) * 0.95)]
            p99 = sorted_durations[int(len(sorted_durations) * 0.99)]

            return {
                "flow_name": flow.name,
                "iterations": iterations,
                "min_duration_ms": min_duration,
                "max_duration_ms": max_duration,
                "avg_duration_ms": avg_duration,
                "p50_duration_ms": p50,
                "p95_duration_ms": p95,
                "p99_duration_ms": p99,
                "std_deviation_ms": (
                    sum((d - avg_duration) ** 2 for d in durations) / len(durations)
                )
                ** 0.5,
            }

        return run_benchmark

    return benchmark_func


# Convenience functions for accessing the global monitor
def get_performance_monitor() -> PerformanceMonitor:
    """Get the global performance monitor instance."""
    return _performance_monitor


def enable_memory_tracking() -> None:
    """Enable memory tracking for all monitored flows."""
    _performance_monitor.enable_memory_tracking()


def get_performance_summary() -> PerformanceData:
    """Get summary of all performance metrics."""
    return _performance_monitor.get_summary_stats()


def export_performance_metrics(filepath: str) -> None:
    """Export all performance metrics to a JSON file."""
    _performance_monitor.export_metrics(filepath)
