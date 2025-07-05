"""Health reporting and configuration validation for Flow systems.

This module provides configuration validation capabilities and reporting
functions for the health monitoring system.
"""

from __future__ import annotations

from collections.abc import AsyncGenerator, Awaitable, Callable
from typing import Any, Union

from ...exceptions import FlowConfigurationError
from ...flow import Flow
from .checks import FlowHealthMonitor
from .core import HealthStatus, SystemHealth

# Type aliases
AnyValue = Any
ValidatorRegistry = dict[str, Callable[[Any], bool]]
ConfigData = dict[str, Any]
ConfigSchema = dict[str, Any]
AnyFlow = Flow[Any, Any]
CheckFunction = Union[
    Callable[[], Awaitable[bool]], Callable[[], AsyncGenerator[bool, None]]
]


class FlowConfigValidator:
    """Configuration validation for Flow systems."""

    def __init__(self) -> None:  # pyright: ignore[reportMissingSuperCall]
        """Initialize the configuration validator."""
        self.validators: ValidatorRegistry = {}
        self.config_schema: ConfigSchema = {}

        # Register default validators
        self._register_default_validators()

    def _register_default_validators(self) -> None:
        """Register default configuration validators."""

        def validate_positive_number(value: AnyValue) -> bool:
            """Validate that value is a positive number."""
            return isinstance(value, int | float) and value > 0

        def validate_non_negative_number(value: AnyValue) -> bool:
            """Validate that value is a non-negative number."""
            return isinstance(value, int | float) and value >= 0

        def validate_string(value: AnyValue) -> bool:
            """Validate that value is a non-empty string."""
            return isinstance(value, str) and len(value.strip()) > 0

        def validate_boolean(value: AnyValue) -> bool:
            """Validate that value is a boolean."""
            return isinstance(value, bool)

        self.validators.update(
            {
                "positive_number": validate_positive_number,
                "non_negative_number": validate_non_negative_number,
                "string": validate_string,
                "boolean": validate_boolean,
            }
        )

    def register_validator(self, name: str, validator: Callable[[Any], bool]) -> None:
        """Register a custom validator."""
        self.validators[name] = validator

    def set_config_schema(self, schema: ConfigSchema) -> None:
        """Set the configuration schema for validation."""
        self.config_schema = schema

    def validate_config(self, config: ConfigData) -> list[str]:
        """Validate configuration against the schema.

        Returns:
            List of validation error messages. Empty list if valid.
        """
        errors: list[str] = []

        if not self.config_schema:
            return errors

        # Check required fields
        for field_name, field_config in self.config_schema.items():
            if field_config.get("required", False) and field_name not in config:
                errors.append(f"Required field '{field_name}' is missing")
                continue

            if field_name not in config:
                continue

            value = config[field_name]

            # Check type validator
            validator_name = field_config.get("validator")
            if validator_name and validator_name in self.validators:
                validator = self.validators[validator_name]
                if not validator(value):
                    errors.append(
                        f"Field '{field_name}' failed validation '{validator_name}'"
                    )

            # Check allowed values
            allowed_values = field_config.get("allowed_values")
            if allowed_values and value not in allowed_values:
                errors.append(
                    f"Field '{field_name}' value '{value}' not in allowed values: {allowed_values}"
                )

            # Check range for numbers
            if isinstance(value, int | float):
                min_value = field_config.get("min_value")
                max_value = field_config.get("max_value")

                if min_value is not None and value < min_value:
                    errors.append(
                        f"Field '{field_name}' value {value} is below minimum {min_value}"
                    )

                if max_value is not None and value > max_value:
                    errors.append(
                        f"Field '{field_name}' value {value} is above maximum {max_value}"
                    )

        return errors

    def validate_flow_config(self, flow: AnyFlow, config: ConfigData) -> list[str]:
        """Validate configuration specific to a Flow.

        Args:
            flow: The Flow to validate configuration for
            config: Configuration dictionary

        Returns:
            List of validation error messages.
        """
        errors: list[str] = []

        # Basic Flow configuration validation
        if "max_items" in config:
            if not isinstance(config["max_items"], int) or config["max_items"] <= 0:
                errors.append("max_items must be a positive integer")

        if "timeout_seconds" in config:
            if (
                not isinstance(config["timeout_seconds"], int | float)
                or config["timeout_seconds"] <= 0
            ):
                errors.append("timeout_seconds must be a positive number")

        if "batch_size" in config:
            if not isinstance(config["batch_size"], int) or config["batch_size"] <= 0:
                errors.append("batch_size must be a positive integer")

        if "memory_limit_mb" in config:
            if (
                not isinstance(config["memory_limit_mb"], int | float)
                or config["memory_limit_mb"] <= 0
            ):
                errors.append("memory_limit_mb must be a positive number")

        return errors


# Global instances
_health_monitor = FlowHealthMonitor()
_config_validator = FlowConfigValidator()


def health_check_stream(
    health_monitor: FlowHealthMonitor | None = None,
) -> Flow[Any, Any]:
    """Create a flow that performs health checks during stream processing.

    Args:
        health_monitor: Optional health monitor instance. Uses global if None.

    Returns:
        A flow that runs health checks and passes items through unchanged.
    """
    monitor = health_monitor or _health_monitor

    async def _flow(stream: AsyncGenerator[Any, None]) -> AsyncGenerator[Any, None]:
        """Internal flow function that adds health checking."""
        item_count = 0
        async for item in stream:
            # Run a quick health check every 100 items
            item_count += 1

            if item_count % 100 == 0:
                # Run a subset of critical health checks
                critical_checks = [
                    name
                    for name, check in monitor.checks.items()
                    if check.critical and check.enabled
                ]

                for check_name in critical_checks[
                    :2
                ]:  # Limit to 2 checks for performance
                    result = await monitor.run_check(check_name)
                    if (
                        result
                        and result.critical
                        and result.status != HealthStatus.HEALTHY
                    ):
                        raise FlowConfigurationError(
                            f"Critical health check failed: {result.message}"
                        )

            yield item

    return Flow(_flow, name="health_check")


# Convenience functions
def get_health_monitor() -> FlowHealthMonitor:
    """Get the global health monitor instance."""
    return _health_monitor


def get_config_validator() -> FlowConfigValidator:
    """Get the global configuration validator instance."""
    return _config_validator


async def check_system_health() -> SystemHealth:
    """Check overall system health."""
    return await _health_monitor.run_all_checks()


def validate_flow_configuration(config: ConfigData) -> list[str]:
    """Validate flow configuration."""
    return _config_validator.validate_config(config)


def register_health_check(
    name: str,
    description: str,
    check_function: CheckFunction,
    **kwargs: AnyValue,
) -> None:
    """Register a custom health check."""
    _health_monitor.register_check(name, description, check_function, **kwargs)


def export_health_report(filepath: str) -> None:
    """Export system health report to file."""
    _health_monitor.export_health_report(filepath)
