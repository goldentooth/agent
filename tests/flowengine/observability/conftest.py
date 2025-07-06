"""Observability test configuration fixtures."""

from __future__ import annotations

import pytest

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
