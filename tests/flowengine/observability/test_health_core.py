"""Tests for core health monitoring functionality."""

import asyncio
from datetime import datetime

import pytest

from flowengine.observability.health.core import (
    HealthCheck,
    HealthCheckResult,
    HealthStatus,
    SystemHealth,
)


class TestHealthStatus:
    """Tests for HealthStatus enum."""

    def test_health_status_values(self) -> None:
        """Test that HealthStatus has correct values."""
        assert HealthStatus.HEALTHY.value == "healthy"
        assert HealthStatus.WARNING.value == "warning"
        assert HealthStatus.CRITICAL.value == "critical"
        assert HealthStatus.UNKNOWN.value == "unknown"

    def test_health_status_members(self) -> None:
        """Test that HealthStatus has all expected members."""
        expected_members = {"HEALTHY", "WARNING", "CRITICAL", "UNKNOWN"}
        actual_members = {member.name for member in HealthStatus}
        assert actual_members == expected_members

    def test_health_status_from_value(self) -> None:
        """Test creating HealthStatus from string value."""
        assert HealthStatus("healthy") == HealthStatus.HEALTHY
        assert HealthStatus("warning") == HealthStatus.WARNING
        assert HealthStatus("critical") == HealthStatus.CRITICAL
        assert HealthStatus("unknown") == HealthStatus.UNKNOWN

    def test_health_status_invalid_value(self) -> None:
        """Test that invalid values raise ValueError."""
        with pytest.raises(ValueError, match="'invalid' is not a valid HealthStatus"):
            HealthStatus("invalid")


class TestHealthCheckResult:
    """Tests for HealthCheckResult class."""

    def test_health_check_result_creation(self) -> None:
        """Test creating a HealthCheckResult with required fields."""
        result = HealthCheckResult(
            name="test_check",
            status=HealthStatus.HEALTHY,
            message="Check passed",
            duration_seconds=0.5,
        )

        assert result.name == "test_check"
        assert result.status == HealthStatus.HEALTHY
        assert result.message == "Check passed"
        assert result.duration_seconds == 0.5
        assert result.critical is False
        assert result.error is None
        assert isinstance(result.timestamp, datetime)
        assert result.metadata == {}

    def test_health_check_result_with_all_fields(self) -> None:
        """Test creating a HealthCheckResult with all fields."""
        timestamp = datetime.now()
        metadata = {"key": "value"}

        result = HealthCheckResult(
            name="test_check",
            status=HealthStatus.CRITICAL,
            message="Check failed",
            duration_seconds=1.5,
            critical=True,
            error="Connection timeout",
            timestamp=timestamp,
            metadata=metadata,
        )

        assert result.critical is True
        assert result.error == "Connection timeout"
        assert result.timestamp == timestamp
        assert result.metadata == metadata

    def test_health_check_result_to_dict(self) -> None:
        """Test converting HealthCheckResult to dictionary."""
        timestamp = datetime.now()
        result = HealthCheckResult(
            name="test_check",
            status=HealthStatus.WARNING,
            message="Check warning",
            duration_seconds=0.75,
            timestamp=timestamp,
        )

        result_dict = result.to_dict()

        assert result_dict["name"] == "test_check"
        assert result_dict["status"] == "warning"
        assert result_dict["message"] == "Check warning"
        assert result_dict["duration_seconds"] == 0.75
        assert result_dict["critical"] is False
        assert result_dict["error"] is None
        assert result_dict["timestamp"] == timestamp.isoformat()
        assert result_dict["metadata"] == {}

    def test_health_check_result_to_dict_with_metadata(self) -> None:
        """Test converting HealthCheckResult with metadata to dictionary."""
        metadata = {"cpu_usage": 85.5, "memory_mb": 1024}
        result = HealthCheckResult(
            name="resource_check",
            status=HealthStatus.WARNING,
            message="High resource usage",
            duration_seconds=0.1,
            metadata=metadata,
        )

        result_dict = result.to_dict()
        assert result_dict["metadata"] == metadata


class TestSystemHealth:
    """Tests for SystemHealth class."""

    def test_system_health_creation(self) -> None:
        """Test creating a SystemHealth instance."""
        checks = [
            HealthCheckResult(
                name="check1",
                status=HealthStatus.HEALTHY,
                message="OK",
                duration_seconds=0.1,
            ),
            HealthCheckResult(
                name="check2",
                status=HealthStatus.WARNING,
                message="Warning",
                duration_seconds=0.2,
            ),
        ]

        health = SystemHealth(
            status=HealthStatus.WARNING,
            message="System has warnings",
            checks=checks,
        )

        assert health.status == HealthStatus.WARNING
        assert health.message == "System has warnings"
        assert len(health.checks) == 2
        assert isinstance(health.timestamp, datetime)

    def test_healthy_checks_property(self) -> None:
        """Test healthy_checks property."""
        checks = [
            HealthCheckResult("check1", HealthStatus.HEALTHY, "OK", 0.1),
            HealthCheckResult("check2", HealthStatus.WARNING, "Warning", 0.2),
            HealthCheckResult("check3", HealthStatus.HEALTHY, "OK", 0.3),
        ]

        health = SystemHealth(HealthStatus.WARNING, "Mixed", checks)
        healthy = health.healthy_checks

        assert len(healthy) == 2
        assert all(check.status == HealthStatus.HEALTHY for check in healthy)

    def test_warning_checks_property(self) -> None:
        """Test warning_checks property."""
        checks = [
            HealthCheckResult("check1", HealthStatus.HEALTHY, "OK", 0.1),
            HealthCheckResult("check2", HealthStatus.WARNING, "Warning", 0.2),
            HealthCheckResult("check3", HealthStatus.WARNING, "Warning", 0.3),
        ]

        health = SystemHealth(HealthStatus.WARNING, "Has warnings", checks)
        warnings = health.warning_checks

        assert len(warnings) == 2
        assert all(check.status == HealthStatus.WARNING for check in warnings)

    def test_critical_checks_property(self) -> None:
        """Test critical_checks property."""
        checks = [
            HealthCheckResult("check1", HealthStatus.CRITICAL, "Critical", 0.1),
            HealthCheckResult("check2", HealthStatus.WARNING, "Warning", 0.2),
            HealthCheckResult("check3", HealthStatus.CRITICAL, "Critical", 0.3),
        ]

        health = SystemHealth(HealthStatus.CRITICAL, "Has critical issues", checks)
        critical = health.critical_checks

        assert len(critical) == 2
        assert all(check.status == HealthStatus.CRITICAL for check in critical)

    def test_system_health_to_dict(self) -> None:
        """Test converting SystemHealth to dictionary."""
        timestamp = datetime.now()
        checks = [
            HealthCheckResult("check1", HealthStatus.HEALTHY, "OK", 0.1),
            HealthCheckResult("check2", HealthStatus.WARNING, "Warning", 0.2),
            HealthCheckResult("check3", HealthStatus.CRITICAL, "Critical", 0.3),
        ]

        health = SystemHealth(
            status=HealthStatus.CRITICAL,
            message="System has critical issues",
            checks=checks,
            timestamp=timestamp,
        )

        health_dict = health.to_dict()

        assert health_dict["status"] == "critical"
        assert health_dict["message"] == "System has critical issues"
        assert health_dict["timestamp"] == timestamp.isoformat()
        assert health_dict["summary"]["total_checks"] == 3
        assert health_dict["summary"]["healthy"] == 1
        assert health_dict["summary"]["warning"] == 1
        assert health_dict["summary"]["critical"] == 1
        assert len(health_dict["checks"]) == 3

    def test_system_health_empty_checks(self) -> None:
        """Test SystemHealth with no checks."""
        health = SystemHealth(
            status=HealthStatus.UNKNOWN,
            message="No checks configured",
            checks=[],
        )

        assert len(health.healthy_checks) == 0
        assert len(health.warning_checks) == 0
        assert len(health.critical_checks) == 0

        health_dict = health.to_dict()
        assert health_dict["summary"]["total_checks"] == 0


class TestHealthCheck:
    """Tests for HealthCheck class."""

    @pytest.mark.asyncio
    async def test_health_check_creation(self) -> None:
        """Test creating a HealthCheck instance."""

        async def check_function() -> bool:
            return True

        health_check = HealthCheck(
            name="test_check",
            description="Test health check",
            check_function=check_function,
        )

        assert health_check.name == "test_check"
        assert health_check.description == "Test health check"
        assert health_check.check_function == check_function
        assert health_check.timeout_seconds == 5.0
        assert health_check.critical is False
        assert health_check.enabled is True
        assert health_check.tags == []

    @pytest.mark.asyncio
    async def test_health_check_with_all_fields(self) -> None:
        """Test creating a HealthCheck with all fields."""

        async def check_function() -> bool:
            return True

        health_check = HealthCheck(
            name="test_check",
            description="Test health check",
            check_function=check_function,
            timeout_seconds=10.0,
            critical=True,
            enabled=False,
            tags=["database", "critical"],
        )

        assert health_check.timeout_seconds == 10.0
        assert health_check.critical is True
        assert health_check.enabled is False
        assert health_check.tags == ["database", "critical"]

    @pytest.mark.asyncio
    async def test_health_check_run_success(self) -> None:
        """Test running a successful health check."""

        async def check_function() -> bool:
            await asyncio.sleep(0.1)
            return True

        health_check = HealthCheck(
            name="test_check",
            description="Test health check",
            check_function=check_function,
        )

        result = await health_check.run()

        assert result.name == "test_check"
        assert result.status == HealthStatus.HEALTHY
        assert result.message == "Check passed"
        assert result.duration_seconds >= 0.1
        assert result.critical is False
        assert result.error is None

    @pytest.mark.asyncio
    async def test_health_check_run_failure(self) -> None:
        """Test running a failing health check."""

        async def check_function() -> bool:
            return False

        health_check = HealthCheck(
            name="test_check",
            description="Test health check",
            check_function=check_function,
            critical=True,
        )

        result = await health_check.run()

        assert result.status == HealthStatus.WARNING
        assert result.message == "Check failed"
        assert result.critical is True

    @pytest.mark.asyncio
    async def test_health_check_run_timeout(self) -> None:
        """Test health check timeout."""

        async def check_function() -> bool:
            await asyncio.sleep(2.0)
            return True

        health_check = HealthCheck(
            name="test_check",
            description="Test health check",
            check_function=check_function,
            timeout_seconds=0.1,
        )

        result = await health_check.run()

        assert result.status == HealthStatus.CRITICAL
        assert "timed out after 0.1s" in result.message
        assert result.critical is True
        assert result.duration_seconds >= 0.1

    @pytest.mark.asyncio
    async def test_health_check_run_exception(self) -> None:
        """Test health check with exception."""

        async def check_function() -> bool:
            raise ValueError("Test error")

        health_check = HealthCheck(
            name="test_check",
            description="Test health check",
            check_function=check_function,
        )

        result = await health_check.run()

        assert result.status == HealthStatus.CRITICAL
        assert "Test error" in result.message
        assert result.error == "Test error"

    @pytest.mark.asyncio
    async def test_health_check_with_async_generator(self) -> None:
        """Test health check with async generator."""

        async def check_function():
            await asyncio.sleep(0.05)
            yield True

        health_check = HealthCheck(
            name="test_check",
            description="Test health check",
            check_function=check_function,
        )

        result = await health_check.run()

        assert result.status == HealthStatus.HEALTHY
        assert result.message == "Check passed"

    @pytest.mark.asyncio
    async def test_health_check_async_generator_empty(self) -> None:
        """Test health check with empty async generator."""

        async def check_function():
            return
            yield  # This makes it a generator but never yields

        health_check = HealthCheck(
            name="test_check",
            description="Test health check",
            check_function=check_function,
        )

        result = await health_check.run()

        assert result.status == HealthStatus.WARNING
        assert result.message == "Check failed"
