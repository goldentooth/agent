"""Tests for core health monitoring functionality."""

import pytest

from flowengine.observability.health.core import HealthStatus


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
