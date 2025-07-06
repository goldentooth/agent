"""Observability test configuration fixtures."""

from __future__ import annotations

from typing import Any, AsyncGenerator, Callable

import pytest

from flowengine.flow import Flow
from flowengine.observability.analysis import FlowAnalyzer
from flowengine.observability.debugging import FlowDebugger
from flowengine.observability.health import FlowHealthMonitor
from flowengine.observability.performance import PerformanceMonitor


@pytest.fixture
def performance_monitor() -> PerformanceMonitor:
    """Configured performance monitor."""
    return PerformanceMonitor()


@pytest.fixture
def flow_analyzer() -> FlowAnalyzer:
    """Configured flow analyzer."""
    return FlowAnalyzer()


@pytest.fixture
def flow_debugger() -> FlowDebugger:
    """Configured debugger."""
    return FlowDebugger()


@pytest.fixture
def health_monitor() -> FlowHealthMonitor:
    """Configured health monitor."""
    return FlowHealthMonitor()


@pytest.fixture
def sample_flows() -> dict[str, Flow[int, int]]:
    """Sample flows for testing."""
    from typing import AsyncGenerator

    async def identity_fn(
        stream: AsyncGenerator[int, None],
    ) -> AsyncGenerator[int, None]:
        async for item in stream:
            yield item

    async def double_fn(stream: AsyncGenerator[int, None]) -> AsyncGenerator[int, None]:
        async for item in stream:
            yield item * 2

    async def filter_even_fn(
        stream: AsyncGenerator[int, None],
    ) -> AsyncGenerator[int, None]:
        async for item in stream:
            if item % 2 == 0:
                yield item

    return {
        "identity": Flow(identity_fn, "identity"),
        "double": Flow(double_fn, "double"),
        "filter_even": Flow(filter_even_fn, "filter_even"),
    }


@pytest.fixture
def benchmark_data() -> dict[str, Any]:
    """Benchmark test data for performance testing."""
    return {
        "small_dataset": list(range(100)),
        "medium_dataset": list(range(1000)),
        "large_dataset": list(range(10000)),
        "nested_data": [{"id": i, "value": i * 2} for i in range(500)],
        "string_data": [f"item_{i}" for i in range(1000)],
        "mixed_data": [i if i % 2 == 0 else f"str_{i}" for i in range(500)],
        "performance_thresholds": {
            "small_processing_time": 0.1,
            "medium_processing_time": 1.0,
            "large_processing_time": 10.0,
            "memory_limit_mb": 100,
            "max_cpu_usage_percent": 80,
        },
    }


@pytest.fixture
def observability_config() -> dict[str, Any]:
    """Test configuration for observability components."""
    return {
        "performance": {
            "enable_monitoring": True,
            "sample_rate": 1.0,
            "buffer_size": 1000,
            "flush_interval": 0.1,
        },
        "debugging": {
            "enable_tracing": True,
            "max_trace_depth": 10,
            "capture_locals": False,
            "trace_exceptions": True,
        },
        "health": {
            "check_interval": 1.0,
            "failure_threshold": 3,
            "recovery_threshold": 2,
            "enable_system_checks": True,
        },
        "analysis": {
            "enable_flow_analysis": True,
            "max_graph_depth": 20,
            "analyze_performance": True,
            "collect_statistics": True,
        },
    }


def create_test_flow(
    name: str = "test_flow",
    transform_fn: Callable[[int], int] | None = None,
    metadata: dict[str, Any] | None = None,
) -> Flow[int, int]:
    """Create a test flow with optional transformation function."""
    from typing import AsyncGenerator

    if transform_fn is None:
        transform_fn = lambda x: x  # Identity function

    async def flow_fn(stream: AsyncGenerator[int, None]) -> AsyncGenerator[int, None]:
        async for item in stream:
            yield transform_fn(item)

    return Flow(flow_fn, name, metadata or {})


async def generate_test_stream(
    items: list[int] | None = None,
    size: int = 10,
    delay: float = 0.0,
) -> AsyncGenerator[int, None]:
    """Generate a test data stream."""
    import asyncio

    if items is None:
        items = list(range(size))

    for item in items:
        if delay > 0:
            await asyncio.sleep(delay)
        yield item


def assert_performance_within_bounds(
    actual_time: float,
    expected_max_time: float,
    tolerance: float = 0.1,
) -> None:
    """Assert that performance is within acceptable bounds."""
    max_allowed = expected_max_time * (1 + tolerance)
    assert actual_time <= max_allowed, (
        f"Performance exceeded bounds: {actual_time:.3f}s > {max_allowed:.3f}s "
        f"(expected max: {expected_max_time:.3f}s, tolerance: {tolerance:.1%})"
    )


def cleanup_observability() -> None:
    """Clean up observability resources after tests."""
    # This utility provides a centralized way to clean up observability
    # state between tests. Currently a no-op but can be extended as needed.
    pass
