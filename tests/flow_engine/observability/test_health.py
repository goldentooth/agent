"""Tests for health checking and configuration validation."""

import asyncio
import json
from datetime import datetime, timedelta

import pytest

from goldentooth_agent.flow_engine.exceptions import FlowConfigurationError
from goldentooth_agent.flow_engine.observability.health import (
    FlowConfigValidator,
    FlowHealthMonitor,
    HealthCheck,
    HealthCheckResult,
    HealthStatus,
    SystemHealth,
    check_system_health,
    export_health_report,
    get_config_validator,
    get_health_monitor,
    health_check_stream,
    register_health_check,
    validate_flow_configuration,
)


async def async_range(n: int):
    """Generate an async range of integers."""
    for i in range(n):
        yield i


class TestHealthStatus:
    """Tests for HealthStatus enum."""

    def test_health_status_values(self):
        """Test HealthStatus enum values."""
        assert HealthStatus.HEALTHY.value == "healthy"
        assert HealthStatus.WARNING.value == "warning"
        assert HealthStatus.CRITICAL.value == "critical"
        assert HealthStatus.UNKNOWN.value == "unknown"


class TestHealthCheck:
    """Tests for HealthCheck class."""

    def test_health_check_creation(self):
        """Test basic HealthCheck creation."""

        async def simple_check():
            yield True

        check = HealthCheck(
            name="test_check",
            description="Test health check",
            check_function=simple_check,
            timeout_seconds=2.0,
            critical=True,
        )

        assert check.name == "test_check"
        assert check.description == "Test health check"
        assert check.timeout_seconds == 2.0
        assert check.critical is True
        assert check.enabled is True

    @pytest.mark.asyncio
    async def test_health_check_run_success(self):
        """Test running a successful health check."""

        async def passing_check():
            yield True

        check = HealthCheck(
            name="passing_check",
            description="Always passes",
            check_function=passing_check,
        )

        result = await check.run()

        assert result.name == "passing_check"
        assert result.status == HealthStatus.HEALTHY
        assert "passed" in result.message.lower()
        assert result.duration_seconds >= 0

    @pytest.mark.asyncio
    async def test_health_check_run_failure(self):
        """Test running a failing health check."""

        async def failing_check():
            yield False

        check = HealthCheck(
            name="failing_check",
            description="Always fails",
            check_function=failing_check,
        )

        result = await check.run()

        assert result.name == "failing_check"
        assert result.status == HealthStatus.WARNING
        assert "failed" in result.message.lower()

    @pytest.mark.asyncio
    async def test_health_check_run_timeout(self):
        """Test health check timeout."""

        async def slow_check():
            await asyncio.sleep(0.1)  # 100ms delay
            yield True

        check = HealthCheck(
            name="slow_check",
            description="Slow check",
            check_function=slow_check,
            timeout_seconds=0.01,  # 10ms timeout
        )

        result = await check.run()

        assert result.name == "slow_check"
        assert result.status == HealthStatus.CRITICAL
        assert "timed out" in result.message.lower()
        assert result.critical is True

    @pytest.mark.asyncio
    async def test_health_check_run_exception(self):
        """Test health check that raises exception."""

        async def error_check():
            raise ValueError("Test error")

        check = HealthCheck(
            name="error_check",
            description="Raises error",
            check_function=error_check,
        )

        result = await check.run()

        assert result.name == "error_check"
        assert result.status == HealthStatus.CRITICAL
        assert "Test error" in result.message
        assert result.error == "Test error"


class TestHealthCheckResult:
    """Tests for HealthCheckResult class."""

    def test_health_check_result_creation(self):
        """Test HealthCheckResult creation."""
        result = HealthCheckResult(
            name="test_result",
            status=HealthStatus.HEALTHY,
            message="All good",
            duration_seconds=0.5,
            critical=False,
        )

        assert result.name == "test_result"
        assert result.status == HealthStatus.HEALTHY
        assert result.message == "All good"
        assert result.duration_seconds == 0.5
        assert result.critical is False

    def test_health_check_result_to_dict(self):
        """Test HealthCheckResult to_dict conversion."""
        result = HealthCheckResult(
            name="test_result",
            status=HealthStatus.WARNING,
            message="Warning message",
            duration_seconds=1.0,
            error="Test error",
        )

        result_dict = result.to_dict()

        assert result_dict["name"] == "test_result"
        assert result_dict["status"] == "warning"
        assert result_dict["message"] == "Warning message"
        assert result_dict["duration_seconds"] == 1.0
        assert result_dict["error"] == "Test error"
        assert "timestamp" in result_dict


class TestSystemHealth:
    """Tests for SystemHealth class."""

    def test_system_health_creation(self):
        """Test SystemHealth creation."""
        results = [
            HealthCheckResult("check1", HealthStatus.HEALTHY, "OK", 0.1),
            HealthCheckResult("check2", HealthStatus.WARNING, "Warning", 0.2),
        ]

        health = SystemHealth(
            status=HealthStatus.WARNING,
            message="System has warnings",
            checks=results,
        )

        assert health.status == HealthStatus.WARNING
        assert health.message == "System has warnings"
        assert len(health.checks) == 2

    def test_system_health_properties(self):
        """Test SystemHealth property methods."""
        results = [
            HealthCheckResult("healthy", HealthStatus.HEALTHY, "OK", 0.1),
            HealthCheckResult("warning", HealthStatus.WARNING, "Warning", 0.2),
            HealthCheckResult("critical", HealthStatus.CRITICAL, "Critical", 0.3),
        ]

        health = SystemHealth(
            status=HealthStatus.CRITICAL,
            message="System critical",
            checks=results,
        )

        assert len(health.healthy_checks) == 1
        assert len(health.warning_checks) == 1
        assert len(health.critical_checks) == 1

    def test_system_health_to_dict(self):
        """Test SystemHealth to_dict conversion."""
        results = [
            HealthCheckResult("check1", HealthStatus.HEALTHY, "OK", 0.1),
        ]

        health = SystemHealth(
            status=HealthStatus.HEALTHY,
            message="All good",
            checks=results,
        )

        health_dict = health.to_dict()

        assert health_dict["status"] == "healthy"
        assert health_dict["message"] == "All good"
        assert "timestamp" in health_dict
        assert "summary" in health_dict
        assert health_dict["summary"]["total_checks"] == 1
        assert len(health_dict["checks"]) == 1


class TestFlowHealthMonitor:
    """Tests for FlowHealthMonitor class."""

    def test_health_monitor_creation(self):
        """Test FlowHealthMonitor creation."""
        monitor = FlowHealthMonitor()

        assert isinstance(monitor.checks, dict)
        assert isinstance(monitor.history, list)
        assert monitor.max_history == 100

        # Should have default checks registered
        assert len(monitor.checks) > 0

    def test_register_unregister_check(self):
        """Test registering and unregistering health checks."""
        monitor = FlowHealthMonitor()

        async def test_check():
            yield True

        monitor.register_check(
            name="test_check",
            description="Test check",
            check_function=test_check,
            timeout_seconds=5.0,
            critical=True,
            tags=["test"],
        )

        assert "test_check" in monitor.checks
        check = monitor.checks["test_check"]
        assert check.name == "test_check"
        assert check.critical is True
        assert "test" in check.tags

        monitor.unregister_check("test_check")
        assert "test_check" not in monitor.checks

    @pytest.mark.asyncio
    async def test_run_check_exists(self):
        """Test running an existing check."""
        monitor = FlowHealthMonitor()

        async def test_check():
            yield True

        monitor.register_check("test_check", "Test", test_check)

        result = await monitor.run_check("test_check")

        assert result is not None
        assert result.name == "test_check"

    @pytest.mark.asyncio
    async def test_run_check_not_exists(self):
        """Test running a non-existent check."""
        monitor = FlowHealthMonitor()

        result = await monitor.run_check("nonexistent")

        assert result is None

    @pytest.mark.asyncio
    async def test_run_check_disabled(self):
        """Test running a disabled check."""
        monitor = FlowHealthMonitor()

        async def test_check():
            yield True

        monitor.register_check("test_check", "Test", test_check)
        monitor.checks["test_check"].enabled = False

        result = await monitor.run_check("test_check")

        assert result is None

    @pytest.mark.asyncio
    async def test_run_all_checks(self):
        """Test running all health checks."""
        monitor = FlowHealthMonitor()

        # Clear default checks for predictable testing
        monitor.checks.clear()

        async def passing_check():
            yield True

        async def failing_check():
            yield False

        monitor.register_check("passing", "Passing check", passing_check)
        monitor.register_check("failing", "Failing check", failing_check)

        system_health = await monitor.run_all_checks()

        assert len(system_health.checks) == 2
        assert system_health.status == HealthStatus.WARNING  # Has failures
        assert len(monitor.history) == 1

    @pytest.mark.asyncio
    async def test_run_all_checks_with_exception(self):
        """Test running checks when one raises exception."""
        monitor = FlowHealthMonitor()
        monitor.checks.clear()

        async def error_check():
            raise RuntimeError("Test error")

        monitor.register_check("error_check", "Error check", error_check)

        system_health = await monitor.run_all_checks()

        assert len(system_health.checks) == 1
        assert system_health.checks[0].status == HealthStatus.CRITICAL

    def test_determine_overall_status_empty(self):
        """Test determining status with no checks."""
        monitor = FlowHealthMonitor()

        status = monitor._determine_overall_status([])

        assert status == HealthStatus.UNKNOWN

    def test_determine_overall_status_critical(self):
        """Test determining status with critical failures."""
        monitor = FlowHealthMonitor()

        results = [
            HealthCheckResult(
                "critical", HealthStatus.CRITICAL, "Critical", 0.1, critical=True
            ),
            HealthCheckResult("healthy", HealthStatus.HEALTHY, "OK", 0.1),
        ]

        status = monitor._determine_overall_status(results)

        assert status == HealthStatus.CRITICAL

    def test_determine_overall_status_warning(self):
        """Test determining status with warnings."""
        monitor = FlowHealthMonitor()

        results = [
            HealthCheckResult("warning", HealthStatus.WARNING, "Warning", 0.1),
            HealthCheckResult("healthy", HealthStatus.HEALTHY, "OK", 0.1),
        ]

        status = monitor._determine_overall_status(results)

        assert status == HealthStatus.WARNING

    def test_determine_overall_status_healthy(self):
        """Test determining status when all healthy."""
        monitor = FlowHealthMonitor()

        results = [
            HealthCheckResult("healthy1", HealthStatus.HEALTHY, "OK", 0.1),
            HealthCheckResult("healthy2", HealthStatus.HEALTHY, "OK", 0.1),
        ]

        status = monitor._determine_overall_status(results)

        assert status == HealthStatus.HEALTHY

    def test_get_health_history(self):
        """Test getting health history."""
        monitor = FlowHealthMonitor()

        # Add some history
        old_health = SystemHealth(HealthStatus.HEALTHY, "Old", [])
        old_health.timestamp = datetime.now() - timedelta(hours=2)

        recent_health = SystemHealth(HealthStatus.HEALTHY, "Recent", [])
        recent_health.timestamp = datetime.now()

        monitor.history = [old_health, recent_health]

        # Get last 1 hour
        recent_history = monitor.get_health_history(hours=1)

        assert len(recent_history) == 1
        assert recent_history[0] == recent_health

    def test_export_health_report(self, tmp_path):
        """Test exporting health report."""
        monitor = FlowHealthMonitor()

        # Add some history
        health = SystemHealth(HealthStatus.HEALTHY, "All good", [])
        monitor.history = [health]

        filepath = tmp_path / "health_report.json"
        monitor.export_health_report(str(filepath))

        assert filepath.exists()

        with open(filepath) as f:
            data = json.load(f)

        assert "report_generated" in data
        assert "current_health" in data
        assert "recent_history" in data
        assert "registered_checks" in data

    def test_export_health_report_no_history(self, tmp_path):
        """Test exporting health report with no history."""
        monitor = FlowHealthMonitor()
        monitor.history = []

        filepath = tmp_path / "health_report.json"
        monitor.export_health_report(str(filepath))

        assert filepath.exists()

        with open(filepath) as f:
            data = json.load(f)

        assert data["message"] == "No health data available"


class TestFlowConfigValidator:
    """Tests for FlowConfigValidator class."""

    def test_config_validator_creation(self):
        """Test FlowConfigValidator creation."""
        validator = FlowConfigValidator()

        assert isinstance(validator.validators, dict)
        assert isinstance(validator.config_schema, dict)

        # Should have default validators
        assert "positive_number" in validator.validators
        assert "string" in validator.validators
        assert "boolean" in validator.validators

    def test_register_validator(self):
        """Test registering custom validator."""
        validator = FlowConfigValidator()

        def custom_validator(value):
            return isinstance(value, str) and value.startswith("test_")

        validator.register_validator("custom", custom_validator)

        assert "custom" in validator.validators
        assert validator.validators["custom"]("test_value") is True
        assert validator.validators["custom"]("invalid") is False

    def test_set_config_schema(self):
        """Test setting configuration schema."""
        validator = FlowConfigValidator()

        schema = {
            "timeout": {"required": True, "validator": "positive_number"},
            "name": {"required": False, "validator": "string"},
        }

        validator.set_config_schema(schema)

        assert validator.config_schema == schema

    def test_validate_config_no_schema(self):
        """Test validation with no schema set."""
        validator = FlowConfigValidator()

        errors = validator.validate_config({"any": "config"})

        assert errors == []

    def test_validate_config_missing_required(self):
        """Test validation with missing required field."""
        validator = FlowConfigValidator()

        schema = {
            "timeout": {"required": True, "validator": "positive_number"},
        }
        validator.set_config_schema(schema)

        errors = validator.validate_config({})

        assert len(errors) == 1
        assert "Required field 'timeout' is missing" in errors[0]

    def test_validate_config_invalid_validator(self):
        """Test validation with invalid value."""
        validator = FlowConfigValidator()

        schema = {
            "timeout": {"required": True, "validator": "positive_number"},
        }
        validator.set_config_schema(schema)

        errors = validator.validate_config({"timeout": -5})

        assert len(errors) == 1
        assert "failed validation 'positive_number'" in errors[0]

    def test_validate_config_allowed_values(self):
        """Test validation with allowed values."""
        validator = FlowConfigValidator()

        schema = {
            "mode": {"allowed_values": ["dev", "prod", "test"]},
        }
        validator.set_config_schema(schema)

        # Valid value
        errors = validator.validate_config({"mode": "dev"})
        assert errors == []

        # Invalid value
        errors = validator.validate_config({"mode": "invalid"})
        assert len(errors) == 1
        assert "not in allowed values" in errors[0]

    def test_validate_config_numeric_ranges(self):
        """Test validation with numeric ranges."""
        validator = FlowConfigValidator()

        schema = {
            "count": {"min_value": 1, "max_value": 100},
        }
        validator.set_config_schema(schema)

        # Valid value
        errors = validator.validate_config({"count": 50})
        assert errors == []

        # Below minimum
        errors = validator.validate_config({"count": 0})
        assert len(errors) == 1
        assert "below minimum" in errors[0]

        # Above maximum
        errors = validator.validate_config({"count": 200})
        assert len(errors) == 1
        assert "above maximum" in errors[0]

    def test_validate_flow_config(self):
        """Test flow-specific configuration validation."""
        from goldentooth_agent.flow_engine import Flow

        validator = FlowConfigValidator()
        flow = Flow(lambda s: s, name="test_flow")

        # Valid config
        valid_config = {
            "max_items": 100,
            "timeout_seconds": 30.0,
            "batch_size": 10,
            "memory_limit_mb": 512,
        }

        errors = validator.validate_flow_config(flow, valid_config)
        assert errors == []

        # Invalid config
        invalid_config = {
            "max_items": -10,  # Should be positive
            "timeout_seconds": "invalid",  # Should be number
            "batch_size": 0,  # Should be positive
            "memory_limit_mb": -100,  # Should be positive
        }

        errors = validator.validate_flow_config(flow, invalid_config)
        assert len(errors) == 4


class TestHealthCheckStream:
    """Tests for health_check_stream function."""

    @pytest.mark.asyncio
    async def test_health_check_stream_basic(self):
        """Test basic health check stream functionality."""
        health_flow = health_check_stream()
        assert "health_check" in health_flow.name

        input_stream = async_range(10)  # Less than 100, no health checks
        result_stream = health_flow(input_stream)
        values = [item async for item in result_stream]

        assert values == list(range(10))

    @pytest.mark.asyncio
    async def test_health_check_stream_with_checks(self):
        """Test health check stream that triggers checks."""
        monitor = FlowHealthMonitor()
        monitor.checks.clear()  # Clear default checks

        # Add a critical check that passes
        async def passing_check():
            yield True

        monitor.register_check("test_check", "Test", passing_check, critical=True)

        health_flow = health_check_stream(monitor)

        # Generate enough items to trigger health check
        input_stream = async_range(150)  # Will trigger at 100
        result_stream = health_flow(input_stream)
        values = [item async for item in result_stream]

        assert values == list(range(150))

    @pytest.mark.asyncio
    async def test_health_check_stream_with_critical_failure(self):
        """Test health check stream with critical failure."""
        monitor = FlowHealthMonitor()
        monitor.checks.clear()

        # Add a critical check that fails
        async def failing_check():
            yield False

        monitor.register_check("failing_check", "Failing", failing_check, critical=True)

        health_flow = health_check_stream(monitor)

        with pytest.raises(FlowConfigurationError) as exc_info:
            input_stream = async_range(150)
            result_stream = health_flow(input_stream)
            _ = [item async for item in result_stream]

        assert "Critical health check failed" in str(exc_info.value)


class TestConvenienceFunctions:
    """Tests for module-level convenience functions."""

    def test_get_health_monitor(self):
        """Test get_health_monitor function."""
        monitor = get_health_monitor()
        assert isinstance(monitor, FlowHealthMonitor)

    def test_get_config_validator(self):
        """Test get_config_validator function."""
        validator = get_config_validator()
        assert isinstance(validator, FlowConfigValidator)

    @pytest.mark.asyncio
    async def test_check_system_health(self):
        """Test check_system_health function."""
        health = await check_system_health()
        assert isinstance(health, SystemHealth)

    def test_validate_flow_configuration(self):
        """Test validate_flow_configuration function."""
        errors = validate_flow_configuration({})
        assert isinstance(errors, list)

    def test_register_health_check(self):
        """Test register_health_check function."""

        async def test_check():
            yield True

        register_health_check("test_global", "Test global check", test_check)

        monitor = get_health_monitor()
        assert "test_global" in monitor.checks

    def test_export_health_report(self, tmp_path):
        """Test export_health_report function."""
        filepath = tmp_path / "global_report.json"
        export_health_report(str(filepath))

        # File should be created (even if empty)
        assert filepath.exists()


class TestDefaultValidators:
    """Tests for default validator functions."""

    def test_positive_number_validator(self):
        """Test positive number validator."""
        validator = FlowConfigValidator()
        positive_validator = validator.validators["positive_number"]

        assert positive_validator(5) is True
        assert positive_validator(0.1) is True
        assert positive_validator(0) is False
        assert positive_validator(-5) is False
        assert positive_validator("string") is False

    def test_non_negative_number_validator(self):
        """Test non-negative number validator."""
        validator = FlowConfigValidator()
        non_negative_validator = validator.validators["non_negative_number"]

        assert non_negative_validator(5) is True
        assert non_negative_validator(0) is True
        assert non_negative_validator(-1) is False
        assert non_negative_validator("string") is False

    def test_string_validator(self):
        """Test string validator."""
        validator = FlowConfigValidator()
        string_validator = validator.validators["string"]

        assert string_validator("valid") is True
        assert string_validator("  spaced  ") is True
        assert string_validator("") is False
        assert string_validator("   ") is False  # Only whitespace
        assert string_validator(123) is False

    def test_boolean_validator(self):
        """Test boolean validator."""
        validator = FlowConfigValidator()
        boolean_validator = validator.validators["boolean"]

        assert boolean_validator(True) is True
        assert boolean_validator(False) is True
        assert boolean_validator(1) is False
        assert boolean_validator("true") is False
