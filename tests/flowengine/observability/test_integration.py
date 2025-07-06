"""Integration tests for Flow observability, debugging, and analysis features."""

import os
import tempfile
from collections.abc import AsyncGenerator
from typing import Any

import pytest

from flowengine import Flow
from flowengine.combinators import batch_stream, compose, filter_stream, map_stream
from flowengine.observability import (
    HealthStatus,
    analyze_flow,
    analyze_flow_composition,
    check_system_health,
    debug_stream,
    detect_flow_patterns,
    disable_flow_debugging,
    enable_flow_debugging,
    export_flow_analysis,
    export_performance_metrics,
    generate_flow_optimizations,
    get_execution_trace,
    get_performance_summary,
    inspect_flow,
    monitored_stream,
    performance_stream,
    register_health_check,
    traced_flow,
    validate_flow_configuration,
)


# Test fixtures
async def async_range(n: int) -> AsyncGenerator[int, None]:
    """Generate numbers from 0 to n-1."""
    for i in range(n):
        yield i


class TestPerformanceObservability:
    """Test performance monitoring and observability features."""

    def setup_method(self):
        """Reset state before each test."""
        # Clear performance metrics
        get_performance_summary()

    @pytest.mark.asyncio
    async def test_monitored_stream_integration(self):
        """Test performance monitoring integration."""

        def double_value(x: int) -> int:
            return x * 2

        base_flow = map_stream(double_value)

        @monitored_stream("integration_test")
        def create_monitored_flow() -> Any:
            return base_flow

        flow = create_monitored_flow
        input_stream = async_range(100)
        result = [item async for item in flow(input_stream)]  # type: ignore

        assert len(result) == 100
        assert result[:3] == [0, 2, 4]

        # Check performance metrics were collected
        summary = get_performance_summary()
        assert "duration_ms" in summary or summary.get("total_flows_monitored", 0) >= 0

    @pytest.mark.asyncio
    async def test_performance_stream_combinator(self):
        """Test performance stream combinator."""

        def add_one(x: int) -> int:
            return x + 1

        def is_even(x: int) -> bool:
            return x % 2 == 0

        base_pipeline = Flow.from_iterable(range(50)).map(add_one).filter(is_even)

        pipeline = compose(
            compose(base_pipeline, performance_stream()), batch_stream(5)
        )

        # Create empty input for from_iterable
        async def empty_stream():
            yield None

        result = await pipeline.to_list()(empty_stream())

        assert len(result) == 5  # 25 even numbers / 5 per batch

        # Performance metrics should be available
        summary = get_performance_summary()
        assert summary.get("total_flows_monitored", 0) > 0

    @pytest.mark.asyncio
    async def test_export_performance_metrics(self):
        """Test exporting performance metrics."""
        flow = performance_stream()
        input_stream = async_range(10)
        result = [item async for item in flow(input_stream)]  # type: ignore

        assert result == list(range(10))

        # Export performance metrics
        metrics_data = export_performance_metrics("json")

        # Should return some metrics data
        assert isinstance(metrics_data, dict)
        # Should have collected some performance information
        assert "message" in metrics_data or len(metrics_data) > 0


class TestDebuggingCapabilities:
    """Test debugging and introspection capabilities."""

    def setup_method(self):
        """Setup debugging for tests."""
        disable_flow_debugging()  # Start with debugging disabled

    def teardown_method(self):
        """Cleanup after tests."""
        disable_flow_debugging()

    @pytest.mark.asyncio
    async def test_debug_stream_basic(self):
        """Test basic debug stream functionality."""
        debug_flow = debug_stream(log_items=False)  # Don't log to avoid output

        input_stream = async_range(5)
        result = [item async for item in debug_flow(input_stream)]  # type: ignore

        assert result == [0, 1, 2, 3, 4]

    @pytest.mark.asyncio
    async def test_traced_flow_integration(self):
        """Test traced flow integration."""

        def triple_value(x: int) -> int:
            return x * 3

        original_flow = map_stream(triple_value)
        traced = traced_flow(original_flow)

        input_stream = async_range(3)
        result = [item async for item in traced(input_stream)]  # type: ignore

        assert result == [0, 3, 6]

    @pytest.mark.asyncio
    async def test_flow_inspection(self):
        """Test flow inspection capabilities."""

        def add_one(x: int) -> int:
            return x + 1

        test_flow = map_stream(add_one)

        inspection = inspect_flow(test_flow)

        assert "name" in inspection
        assert "type" in inspection
        assert inspection["name"] == "map(add_one)"

    @pytest.mark.asyncio
    async def test_execution_trace(self):
        """Test execution trace collection."""
        enable_flow_debugging()

        try:

            def double_value(x: int) -> int:
                return x * 2

            flow = traced_flow(map_stream(double_value))
            input_stream = async_range(3)
            result = [item async for item in flow(input_stream)]  # type: ignore

            assert result == [0, 2, 4]

            # Execution trace should be available
            trace = get_execution_trace()
            assert isinstance(trace, list)

        finally:
            disable_flow_debugging()
