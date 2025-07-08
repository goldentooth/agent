"""Tests for health reporting and configuration validation."""

# pyright: reportPrivateUsage=false

import asyncio
import json
import tempfile
from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest

from flowengine.flow import Flow
from flowengine.observability.health.core import HealthStatus
from flowengine.observability.health.reporting import (
    FlowConfigValidator,
    check_system_health,
    export_health_report,
    get_config_validator,
    get_health_monitor,
    health_check_stream,
    register_health_check,
    validate_flow_configuration,
)


class TestFlowConfigValidator:
    """Tests for FlowConfigValidator class."""

    def test_flow_config_validator_initialization(self) -> None:
        """Test FlowConfigValidator initialization."""
        validator = FlowConfigValidator()

        assert isinstance(validator.validators, dict)
        assert isinstance(validator.config_schema, dict)
        assert len(validator.validators) == 4  # Default validators

    def test_positive_number_validator(self) -> None:
        """Test positive number validator."""
        validator = FlowConfigValidator()
        pos_validator = validator.validators["positive_number"]

        assert pos_validator(5) is True
        assert pos_validator(5.5) is True
        assert pos_validator(0) is False
        assert pos_validator(-1) is False
        assert pos_validator("5") is False

    def test_non_negative_number_validator(self) -> None:
        """Test non-negative number validator."""
        validator = FlowConfigValidator()
        non_neg_validator = validator.validators["non_negative_number"]

        assert non_neg_validator(0) is True
        assert non_neg_validator(5) is True
        assert non_neg_validator(-1) is False

    def test_string_validator(self) -> None:
        """Test string validator."""
        validator = FlowConfigValidator()
        str_validator = validator.validators["string"]

        assert str_validator("hello") is True
        assert str_validator("  world  ") is True
        assert str_validator("") is False
        assert str_validator("   ") is False
        assert str_validator(123) is False

    def test_boolean_validator(self) -> None:
        """Test boolean validator."""
        validator = FlowConfigValidator()
        bool_validator = validator.validators["boolean"]

        assert bool_validator(True) is True
        assert bool_validator(False) is True
        assert bool_validator(1) is False
        assert bool_validator("true") is False

    def test_register_validator(self) -> None:
        """Test registering custom validators."""
        validator = FlowConfigValidator()

        def custom_validator(value: Any) -> bool:
            return isinstance(value, str) and value.startswith("test_")

        validator.register_validator("custom", custom_validator)

        assert "custom" in validator.validators
        assert validator.validators["custom"]("test_value") is True
        assert validator.validators["custom"]("value") is False

    def test_set_config_schema(self) -> None:
        """Test setting configuration schema."""
        validator = FlowConfigValidator()

        schema = {
            "name": {"required": True, "validator": "string"},
            "count": {"required": False, "validator": "positive_number"},
        }

        validator.set_config_schema(schema)
        assert validator.config_schema == schema

    def test_validate_config_empty_schema(self) -> None:
        """Test validation with empty schema."""
        validator = FlowConfigValidator()

        config = {"any": "value"}
        errors = validator.validate_config(config)

        assert errors == []

    def test_validate_config_required_fields(self) -> None:
        """Test validation of required fields."""
        validator = FlowConfigValidator()

        schema = {
            "name": {"required": True, "validator": "string"},
            "count": {"required": True, "validator": "positive_number"},
            "optional": {"required": False, "validator": "string"},
        }
        validator.set_config_schema(schema)

        # Missing required fields
        config = {"optional": "test"}
        errors = validator.validate_config(config)

        assert len(errors) == 2
        assert "Required field 'name' is missing" in errors
        assert "Required field 'count' is missing" in errors

    def test_validate_config_validator_checks(self) -> None:
        """Test validator function checks."""
        validator = FlowConfigValidator()

        schema = {
            "name": {"required": True, "validator": "string"},
            "count": {"required": True, "validator": "positive_number"},
        }
        validator.set_config_schema(schema)

        # Invalid values
        config = {"name": "", "count": -1}
        errors = validator.validate_config(config)

        assert len(errors) == 2
        assert "Field 'name' failed validation 'string'" in errors
        assert "Field 'count' failed validation 'positive_number'" in errors

    def test_validate_config_allowed_values(self) -> None:
        """Test allowed values validation."""
        validator = FlowConfigValidator()

        schema = {
            "mode": {
                "required": True,
                "allowed_values": ["development", "production", "testing"],
            }
        }
        validator.set_config_schema(schema)

        # Valid value
        config = {"mode": "development"}
        errors = validator.validate_config(config)
        assert errors == []

        # Invalid value
        config = {"mode": "invalid"}
        errors = validator.validate_config(config)
        assert len(errors) == 1
        assert "not in allowed values" in errors[0]

    @pytest.mark.parametrize(
        "temp_value,expected_error_count,error_keywords",
        [
            (50, 0, []),
            (-10, 2, ["below minimum"]),
            (150, 1, ["above maximum"]),
        ],
    )
    def test_validate_config_range_checks(
        self, temp_value: int, expected_error_count: int, error_keywords: list[str]
    ) -> None:
        """Test numeric range validation."""
        validator = FlowConfigValidator()
        schema = {
            "temperature": {
                "required": True,
                "validator": "non_negative_number",
                "min_value": 0,
                "max_value": 100,
            }
        }
        validator.set_config_schema(schema)
        config = {"temperature": temp_value}
        errors = validator.validate_config(config)
        assert len(errors) == expected_error_count
        for keyword in error_keywords:
            assert any(keyword in error for error in errors)

    def test_validate_flow_config_basic(self) -> None:
        """Test basic flow configuration validation."""
        validator = FlowConfigValidator()

        # Valid config
        config = {
            "max_items": 100,
            "timeout_seconds": 30.0,
            "batch_size": 10,
            "memory_limit_mb": 512,
        }

        flow = MagicMock()
        errors = validator.validate_flow_config(flow, config)
        assert errors == []

    def test_validate_flow_config_invalid_values(self) -> None:
        """Test flow configuration with invalid values."""
        validator = FlowConfigValidator()

        config = {
            "max_items": -1,  # Must be positive
            "timeout_seconds": "invalid",  # Must be number
            "batch_size": 0,  # Must be positive
            "memory_limit_mb": -100,  # Must be positive
        }

        flow = MagicMock()
        errors = validator.validate_flow_config(flow, config)

        assert len(errors) == 4
        assert any("max_items must be a positive integer" in error for error in errors)
        assert any(
            "timeout_seconds must be a positive number" in error for error in errors
        )
        assert any("batch_size must be a positive integer" in error for error in errors)
        assert any(
            "memory_limit_mb must be a positive number" in error for error in errors
        )


class TestHealthReportingFunctions:
    """Tests for health reporting functions."""

    @pytest.mark.asyncio
    async def test_health_check_stream(self) -> None:
        """Test health_check_stream function."""
        # Create test data
        test_data = list(range(250))  # More than 100 to trigger health checks

        # Create health check stream
        health_stream = health_check_stream()

        # Helper function to create async generator from list
        async def async_data():
            for item in test_data:
                yield item

        # Process the stream
        results: list[int] = []
        async for item in health_stream(async_data()):
            results.append(item)

        # All items should pass through unchanged
        assert results == test_data

    @pytest.mark.asyncio
    async def test_health_check_stream_with_custom_monitor(self) -> None:
        """Test health_check_stream with custom monitor."""
        from flowengine.observability.health.checks import FlowHealthMonitor

        custom_monitor = FlowHealthMonitor()

        # Add a healthy check
        async def healthy_check():
            yield True

        custom_monitor.register_check(
            name="custom_test",
            description="Custom test check",
            check_function=healthy_check,
        )

        # Create health check stream with custom monitor
        health_stream = health_check_stream(custom_monitor)

        # Process small amount of data
        test_data = list(range(10))

        async def async_data():
            for item in test_data:
                yield item

        # Should process without error
        results: list[int] = []
        async for item in health_stream(async_data()):
            results.append(item)

        assert results == test_data

    def test_get_health_monitor(self) -> None:
        """Test get_health_monitor function."""
        from flowengine.observability.health.checks import FlowHealthMonitor

        monitor = get_health_monitor()
        assert isinstance(monitor, FlowHealthMonitor)

        # Should return the same instance
        monitor2 = get_health_monitor()
        assert monitor is monitor2

    def test_get_config_validator(self) -> None:
        """Test get_config_validator function."""
        validator = get_config_validator()
        assert isinstance(validator, FlowConfigValidator)

        # Should return the same instance
        validator2 = get_config_validator()
        assert validator is validator2

    @pytest.mark.asyncio
    async def test_check_system_health(self) -> None:
        """Test check_system_health function."""
        system_health = await check_system_health()

        assert system_health.status in [
            HealthStatus.HEALTHY,
            HealthStatus.WARNING,
            HealthStatus.CRITICAL,
        ]
        assert len(system_health.checks) >= 2  # At least default checks

    def test_validate_flow_configuration(self) -> None:
        """Test validate_flow_configuration function."""
        # Valid config
        config = {"timeout_seconds": 30}
        errors = validate_flow_configuration(config)
        assert errors == []

        # Invalid config (empty schema by default)
        config = {"invalid_field": "value"}
        errors = validate_flow_configuration(config)
        assert errors == []  # No schema set by default

    @pytest.mark.asyncio
    async def test_register_health_check(self) -> None:
        """Test register_health_check function."""

        async def custom_check() -> bool:
            return True

        register_health_check(
            name="test_custom_check",
            description="Test custom check",
            check_function=custom_check,
            critical=True,
        )

        # Verify it was registered
        monitor = get_health_monitor()
        assert "test_custom_check" in monitor.checks

        # Clean up
        monitor.unregister_check("test_custom_check")

    def test_export_health_report(self) -> None:
        """Test export_health_report function."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            filepath = f.name

        try:
            export_health_report(filepath)

            # Verify file was created and contains valid JSON
            with open(filepath, "r") as f:
                data = json.load(f)

            assert "timestamp" in data
            assert "registered_checks" in data
            assert isinstance(data["registered_checks"], dict)

        finally:
            import os

            os.unlink(filepath)
