"""Test that observability fixtures work correctly."""

import pytest

from flowengine.observability.analysis import FlowAnalyzer
from flowengine.observability.debugging import FlowDebugger
from flowengine.observability.health import FlowHealthMonitor
from flowengine.observability.performance import PerformanceMonitor


class TestObservabilityFixtures:
    """Test observability test fixtures."""

    def test_performance_monitor_fixture(self, performance_monitor: PerformanceMonitor):
        """Test performance_monitor fixture creates valid instance."""
        assert isinstance(performance_monitor, PerformanceMonitor)
        assert len(performance_monitor.metrics) == 0
        assert performance_monitor.memory_tracking is False

    def test_flow_analyzer_fixture(self, flow_analyzer: FlowAnalyzer):
        """Test flow_analyzer fixture creates valid instance."""
        assert isinstance(flow_analyzer, FlowAnalyzer)
        assert flow_analyzer.node_id_counter == 0

    def test_flow_debugger_fixture(self, flow_debugger: FlowDebugger):
        """Test flow_debugger fixture creates valid instance."""
        assert isinstance(flow_debugger, FlowDebugger)
        assert flow_debugger.debug_enabled is False
        assert len(flow_debugger.execution_stack) == 0

    def test_health_monitor_fixture(self, health_monitor: FlowHealthMonitor):
        """Test health_monitor fixture creates valid instance."""
        assert isinstance(health_monitor, FlowHealthMonitor)
        # Health monitor has default checks, so should not be empty
        assert len(health_monitor.checks) > 0
