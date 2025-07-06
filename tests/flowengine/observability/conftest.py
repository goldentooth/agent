"""Observability test configuration fixtures."""

from __future__ import annotations

from typing import Any

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
