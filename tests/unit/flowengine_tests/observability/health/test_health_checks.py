"""Tests for health check implementations."""

# pyright: reportPrivateUsage=false

import asyncio
from collections.abc import AsyncGenerator
from typing import Any

import pytest

from flowengine.observability.health.checks import FlowHealthMonitor
from flowengine.observability.health.core import HealthStatus


class TestFlowHealthMonitor:
    """Tests for FlowHealthMonitor class."""

    def test_flow_health_monitor_initialization(self) -> None:
        """Test FlowHealthMonitor initialization."""
        monitor = FlowHealthMonitor()

        assert isinstance(monitor.checks, dict)
        assert isinstance(monitor.history, list)
        assert monitor.max_history == 100
        assert len(monitor.checks) == 2  # Default checks

    def test_register_check(self) -> None:
        """Test registering a health check."""
        monitor = FlowHealthMonitor()

        async def test_check() -> bool:
            return True

        monitor.register_check(
            name="test_check",
            description="Test health check",
            check_function=test_check,
            critical=True,
            tags=["test", "custom"],
        )

        assert "test_check" in monitor.checks
        check = monitor.checks["test_check"]
        assert check.name == "test_check"
        assert check.description == "Test health check"
        assert check.critical is True
        assert check.tags == ["test", "custom"]

    def test_unregister_check(self) -> None:
        """Test unregistering a health check."""
        monitor = FlowHealthMonitor()

        async def test_check() -> bool:
            return True

        monitor.register_check(
            name="test_check",
            description="Test health check",
            check_function=test_check,
        )

        assert "test_check" in monitor.checks
        monitor.unregister_check("test_check")
        assert "test_check" not in monitor.checks

    @pytest.mark.asyncio
    async def test_run_check(self) -> None:
        """Test running a specific health check."""
        monitor = FlowHealthMonitor()

        async def test_check() -> bool:
            return True

        monitor.register_check(
            name="test_check",
            description="Test health check",
            check_function=test_check,
        )

        result = await monitor.run_check("test_check")
        assert result is not None
        assert result.name == "test_check"
        assert result.status == HealthStatus.HEALTHY

        # Test non-existent check
        result = await monitor.run_check("non_existent")
        assert result is None

    @pytest.mark.asyncio
    async def test_run_check_disabled(self) -> None:
        """Test running a disabled health check."""
        monitor = FlowHealthMonitor()

        async def test_check() -> bool:
            return True

        monitor.register_check(
            name="test_check",
            description="Test health check",
            check_function=test_check,
        )

        # Disable the check
        monitor.checks["test_check"].enabled = False

        result = await monitor.run_check("test_check")
        assert result is None

    @pytest.mark.asyncio
    async def test_run_all_checks(self) -> None:
        """Test running all health checks."""
        monitor = FlowHealthMonitor()

        async def healthy_check() -> bool:
            return True

        async def failing_check() -> bool:
            return False

        monitor.register_check(
            name="healthy",
            description="Healthy check",
            check_function=healthy_check,
        )

        monitor.register_check(
            name="failing",
            description="Failing check",
            check_function=failing_check,
            critical=True,
        )

        system_health = await monitor.run_all_checks()

        assert system_health.status == HealthStatus.WARNING
        assert len(system_health.checks) == 4  # 2 default + 2 custom
        assert len(monitor.history) == 1

    @pytest.mark.asyncio
    async def test_run_all_checks_with_exception(self) -> None:
        """Test running all checks when one throws an exception."""
        monitor = FlowHealthMonitor()

        async def failing_check() -> bool:
            raise ValueError("Test error")

        monitor.register_check(
            name="failing",
            description="Failing check",
            check_function=failing_check,
            critical=True,
        )

        system_health = await monitor.run_all_checks()

        assert system_health.status == HealthStatus.CRITICAL
        failing_result = next(
            (r for r in system_health.checks if r.name == "failing"), None
        )
        assert failing_result is not None
        assert failing_result.status == HealthStatus.CRITICAL
        assert "Test error" in failing_result.message

    def test_determine_overall_status(self) -> None:
        """Test determining overall system status."""
        monitor = FlowHealthMonitor()

        # Test empty results
        assert (
            monitor._determine_overall_status([])  # pyright: ignore[reportPrivateUsage]
            == HealthStatus.UNKNOWN
        )

        # Test all healthy
        from flowengine.observability.health.core import HealthCheckResult

        healthy_results = [
            HealthCheckResult("check1", HealthStatus.HEALTHY, "OK", 0.1),
            HealthCheckResult("check2", HealthStatus.HEALTHY, "OK", 0.1),
        ]
        assert (
            monitor._determine_overall_status(
                healthy_results
            )  # pyright: ignore[reportPrivateUsage]
            == HealthStatus.HEALTHY
        )

        # Test with warnings
        warning_results = healthy_results + [
            HealthCheckResult("check3", HealthStatus.WARNING, "Warning", 0.1)
        ]
        assert (
            monitor._determine_overall_status(
                warning_results
            )  # pyright: ignore[reportPrivateUsage]
            == HealthStatus.WARNING
        )

        # Test with critical
        critical_results = warning_results + [
            HealthCheckResult(
                "check4", HealthStatus.CRITICAL, "Critical", 0.1, critical=True
            )
        ]
        assert (
            monitor._determine_overall_status(
                critical_results
            )  # pyright: ignore[reportPrivateUsage]
            == HealthStatus.CRITICAL
        )

    def test_generate_overall_message(self) -> None:
        """Test generating overall system health message."""
        monitor = FlowHealthMonitor()

        from flowengine.observability.health.core import HealthCheckResult

        # Test critical message
        critical_results = [
            HealthCheckResult(
                "check1", HealthStatus.CRITICAL, "Critical", 0.1, critical=True
            ),
            HealthCheckResult(
                "check2", HealthStatus.CRITICAL, "Critical", 0.1, critical=True
            ),
        ]
        message = (
            monitor._generate_overall_message(  # pyright: ignore[reportPrivateUsage]
                critical_results,
                HealthStatus.CRITICAL,
            )
        )
        assert "System critical: 2 critical health check(s) failed" in message

        # Test warning message
        warning_results = [
            HealthCheckResult("check1", HealthStatus.WARNING, "Warning", 0.1),
        ]
        message = (
            monitor._generate_overall_message(  # pyright: ignore[reportPrivateUsage]
                warning_results, HealthStatus.WARNING
            )
        )
        assert "System has warnings: 1 health check(s) in warning state" in message

        # Test healthy message
        healthy_results = [
            HealthCheckResult("check1", HealthStatus.HEALTHY, "OK", 0.1),
            HealthCheckResult("check2", HealthStatus.HEALTHY, "OK", 0.1),
        ]
        message = (
            monitor._generate_overall_message(  # pyright: ignore[reportPrivateUsage]
                healthy_results, HealthStatus.HEALTHY
            )
        )
        assert "System healthy: All 2 health checks passed" in message

        # Test unknown message
        message = (
            monitor._generate_overall_message(  # pyright: ignore[reportPrivateUsage]
                [], HealthStatus.UNKNOWN
            )
        )
        assert "System health unknown: No health checks available" in message

    def test_get_health_history(self) -> None:
        """Test getting health history."""
        monitor = FlowHealthMonitor()

        # Initially empty
        assert monitor.get_health_history() == []

        # Add some history
        from datetime import datetime, timedelta

        from flowengine.observability.health.core import SystemHealth

        now = datetime.now()
        past = now - timedelta(hours=2)

        monitor.history.append(
            SystemHealth(HealthStatus.HEALTHY, "Old check", [], timestamp=past)
        )
        monitor.history.append(
            SystemHealth(HealthStatus.HEALTHY, "Recent check", [], timestamp=now)
        )

        # Get last hour
        recent = monitor.get_health_history(hours=1)
        assert len(recent) == 1
        assert recent[0].message == "Recent check"

        # Get all
        all_history = monitor.get_health_history(hours=3)
        assert len(all_history) == 2

    @pytest.mark.asyncio
    async def test_default_memory_check(self) -> None:
        """Test default memory usage check."""
        monitor = FlowHealthMonitor()

        # Run memory check
        result = await monitor.run_check("memory_usage")
        assert result is not None
        assert result.name == "memory_usage"
        # Can't predict the status without mocking psutil

    @pytest.mark.asyncio
    async def test_default_event_loop_check(self) -> None:
        """Test default event loop responsiveness check."""
        monitor = FlowHealthMonitor()

        # Run event loop check
        result = await monitor.run_check("event_loop_responsiveness")
        assert result is not None
        assert result.name == "event_loop_responsiveness"
        # Should normally be healthy unless system is under heavy load
        assert result.status in [HealthStatus.HEALTHY, HealthStatus.WARNING]

    def test_max_history_limit(self) -> None:
        """Test that history is limited to max_history."""
        monitor = FlowHealthMonitor()
        monitor.max_history = 5

        from flowengine.observability.health.core import SystemHealth

        # Add more than max_history items
        for i in range(10):
            monitor._add_to_history(  # pyright: ignore[reportPrivateUsage]
                SystemHealth(HealthStatus.HEALTHY, f"Check {i}", [])
            )

        assert len(monitor.history) == 5
        assert monitor.history[0].message == "Check 5"
        assert monitor.history[-1].message == "Check 9"


class TestBuiltInHealthChecks:
    """Tests for built-in health check functions."""

    @pytest.mark.asyncio
    async def test_check_flow_performance(self) -> None:
        """Test check_flow_performance function."""
        from flowengine.flow import Flow
        from flowengine.observability.health.checks import check_flow_performance

        async def test_fn(
            stream: AsyncGenerator[Any, None],
        ) -> AsyncGenerator[Any, None]:
            async for item in stream:
                yield item

        flow = Flow(test_fn, name="test_flow")

        # Test with reasonable threshold
        async for result in check_flow_performance(flow, threshold_ms=1000.0):
            assert isinstance(result, bool)
            # Should be True for simple flow creation
            assert result is True
            break

    @pytest.mark.asyncio
    async def test_check_flow_errors(self) -> None:
        """Test check_flow_errors function."""
        from flowengine.flow import Flow
        from flowengine.observability.health.checks import check_flow_errors

        async def test_fn(
            stream: AsyncGenerator[Any, None],
        ) -> AsyncGenerator[Any, None]:
            async for item in stream:
                yield item

        flow = Flow(test_fn, name="test_flow")

        # Test error rate check
        async for result in check_flow_errors(flow, error_threshold=0.05):
            assert isinstance(result, bool)
            # Should be True as placeholder implementation
            assert result is True
            break

    @pytest.mark.asyncio
    async def test_check_memory_usage(self) -> None:
        """Test check_memory_usage function."""
        from flowengine.observability.health.checks import check_memory_usage

        # Test with very high threshold (should pass)
        async for result in check_memory_usage(threshold_mb=100000.0):  # 100GB
            assert isinstance(result, bool)
            # Should be True with very high threshold
            assert result is True
            break

        # Test with very low threshold (should fail)
        async for result in check_memory_usage(threshold_mb=1.0):  # 1MB
            assert isinstance(result, bool)
            # Should be False with very low threshold
            assert result is False
            break

    @pytest.mark.asyncio
    async def test_check_flow_dependencies(self) -> None:
        """Test check_flow_dependencies function."""
        from flowengine.flow import Flow
        from flowengine.observability.health.checks import check_flow_dependencies

        async def test_fn(
            stream: AsyncGenerator[Any, None],
        ) -> AsyncGenerator[Any, None]:
            async for item in stream:
                yield item

        flow = Flow(test_fn, name="test_flow")

        # Test with valid flow
        async for result in check_flow_dependencies(flow):
            assert isinstance(result, bool)
            assert result is True
            break

        # Test with invalid object
        async for result in check_flow_dependencies({}):
            assert isinstance(result, bool)
            assert result is False
            break

    @pytest.mark.asyncio
    async def test_check_flow_configuration(self) -> None:
        """Test check_flow_configuration function."""
        from flowengine.observability.health.checks import check_flow_configuration

        # Test with valid config
        valid_config = {"name": "test", "timeout": 30}
        async for result in check_flow_configuration(valid_config):
            assert isinstance(result, bool)
            assert result is True
            break

        # Test with invalid config (None values for critical keys)
        invalid_config = {"name": None, "fn": None}
        async for result in check_flow_configuration(invalid_config):
            assert isinstance(result, bool)
            assert result is False
            break

    @pytest.mark.asyncio
    async def test_check_resource_limits(self) -> None:
        """Test check_resource_limits function."""
        from flowengine.observability.health.checks import check_resource_limits

        # Test with high thresholds (should pass)
        async for result in check_resource_limits(
            cpu_threshold=99.0, memory_threshold=99.0
        ):
            assert isinstance(result, bool)
            # Should be True with high thresholds or when psutil unavailable
            assert result is True
            break

    @pytest.mark.asyncio
    async def test_check_flow_responsiveness(self) -> None:
        """Test check_flow_responsiveness function."""
        from flowengine.flow import Flow
        from flowengine.observability.health.checks import check_flow_responsiveness

        async def test_fn(
            stream: AsyncGenerator[Any, None],
        ) -> AsyncGenerator[Any, None]:
            async for item in stream:
                yield item

        flow = Flow(test_fn, name="test_flow")

        # Test with reasonable timeout
        async for result in check_flow_responsiveness(flow, timeout_ms=5000.0):
            assert isinstance(result, bool)
            # Should be True for simple check
            assert result is True
            break

    @pytest.mark.asyncio
    async def test_check_system_resources(self) -> None:
        """Test check_system_resources function."""
        from flowengine.observability.health.checks import check_system_resources

        # Test with high thresholds (should pass)
        async for result in check_system_resources(
            disk_threshold=99.0, load_threshold=10.0
        ):
            assert isinstance(result, bool)
            # Should be True with high thresholds or when psutil unavailable
            assert result is True
            break
