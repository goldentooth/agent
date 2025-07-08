"""Test the observability_config fixture."""

from typing import Any

import pytest


@pytest.mark.asyncio
async def test_observability_config_fixture(
    observability_config: dict[str, Any],
) -> None:
    """Test observability_config fixture provides test configuration."""
    assert "performance" in observability_config
    assert "debugging" in observability_config
    assert "health" in observability_config
    assert "analysis" in observability_config


@pytest.mark.asyncio
async def test_performance_config(observability_config: dict[str, Any]) -> None:
    """Test performance configuration structure."""
    perf_config = observability_config["performance"]
    assert perf_config["enable_monitoring"] is True
    assert perf_config["sample_rate"] == 1.0
    assert perf_config["buffer_size"] == 1000
    assert perf_config["flush_interval"] == 0.1


@pytest.mark.asyncio
async def test_debugging_config(observability_config: dict[str, Any]) -> None:
    """Test debugging configuration structure."""
    debug_config = observability_config["debugging"]
    assert debug_config["enable_tracing"] is True
    assert debug_config["max_trace_depth"] == 10
    assert debug_config["capture_locals"] is False
    assert debug_config["trace_exceptions"] is True


@pytest.mark.asyncio
async def test_health_config(observability_config: dict[str, Any]) -> None:
    """Test health configuration structure."""
    health_config = observability_config["health"]
    assert health_config["check_interval"] == 1.0
    assert health_config["failure_threshold"] == 3
    assert health_config["recovery_threshold"] == 2
    assert health_config["enable_system_checks"] is True


@pytest.mark.asyncio
async def test_analysis_config(observability_config: dict[str, Any]) -> None:
    """Test analysis configuration structure."""
    analysis_config = observability_config["analysis"]
    assert analysis_config["enable_flow_analysis"] is True
    assert analysis_config["max_graph_depth"] == 20
    assert analysis_config["analyze_performance"] is True
    assert analysis_config["collect_statistics"] is True
