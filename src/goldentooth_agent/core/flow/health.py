"""Health checking and configuration validation for Flow systems.

This module provides comprehensive health monitoring, configuration validation,
and system diagnostics for Flow-based applications.
"""

from __future__ import annotations
import asyncio
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Callable, AsyncIterator, Union
from enum import Enum
import json
from datetime import datetime, timedelta

from .main import Flow
from .exceptions import FlowError, FlowConfigurationError


class HealthStatus(Enum):
    """Health status levels."""

    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"
    UNKNOWN = "unknown"


@dataclass
class HealthCheck:
    """Individual health check definition."""

    name: str
    description: str
    check_function: Callable[[], AsyncIterator[bool]]
    timeout_seconds: float = 5.0
    critical: bool = False
    enabled: bool = True
    tags: List[str] = field(default_factory=list)

    async def run(self) -> "HealthCheckResult":
        """Execute the health check."""
        start_time = time.time()

        try:
            # Run with timeout
            result = await asyncio.wait_for(
                self._execute_check(), timeout=self.timeout_seconds
            )

            duration = time.time() - start_time

            return HealthCheckResult(
                name=self.name,
                status=HealthStatus.HEALTHY if result else HealthStatus.WARNING,
                message="Check passed" if result else "Check failed",
                duration_seconds=duration,
                critical=self.critical,
            )

        except asyncio.TimeoutError:
            duration = time.time() - start_time
            return HealthCheckResult(
                name=self.name,
                status=HealthStatus.CRITICAL,
                message=f"Health check timed out after {self.timeout_seconds}s",
                duration_seconds=duration,
                critical=True,
            )

        except Exception as e:
            duration = time.time() - start_time
            return HealthCheckResult(
                name=self.name,
                status=HealthStatus.CRITICAL,
                message=f"Health check failed with error: {str(e)}",
                duration_seconds=duration,
                critical=self.critical,
                error=str(e),
            )

    async def _execute_check(self) -> bool:
        """Execute the check function and return the result."""
        async for result in self.check_function():
            return result
        return False


@dataclass
class HealthCheckResult:
    """Result of a health check execution."""

    name: str
    status: HealthStatus
    message: str
    duration_seconds: float
    critical: bool = False
    error: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary."""
        return {
            "name": self.name,
            "status": self.status.value,
            "message": self.message,
            "duration_seconds": self.duration_seconds,
            "critical": self.critical,
            "error": self.error,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata,
        }


@dataclass
class SystemHealth:
    """Overall system health status."""

    status: HealthStatus
    message: str
    checks: List[HealthCheckResult]
    timestamp: datetime = field(default_factory=datetime.now)

    @property
    def healthy_checks(self) -> List[HealthCheckResult]:
        """Get all healthy checks."""
        return [check for check in self.checks if check.status == HealthStatus.HEALTHY]

    @property
    def warning_checks(self) -> List[HealthCheckResult]:
        """Get all warning checks."""
        return [check for check in self.checks if check.status == HealthStatus.WARNING]

    @property
    def critical_checks(self) -> List[HealthCheckResult]:
        """Get all critical checks."""
        return [check for check in self.checks if check.status == HealthStatus.CRITICAL]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "status": self.status.value,
            "message": self.message,
            "timestamp": self.timestamp.isoformat(),
            "summary": {
                "total_checks": len(self.checks),
                "healthy": len(self.healthy_checks),
                "warning": len(self.warning_checks),
                "critical": len(self.critical_checks),
            },
            "checks": [check.to_dict() for check in self.checks],
        }


class FlowHealthMonitor:
    """Health monitoring system for Flow applications."""

    def __init__(self) -> None:
        self.checks: Dict[str, HealthCheck] = {}
        self.history: List[SystemHealth] = []
        self.max_history = 100

        # Register default health checks
        self._register_default_checks()

    def _register_default_checks(self) -> None:
        """Register default system health checks."""

        # Memory usage check
        async def memory_check() -> AsyncIterator[bool]:
            try:
                import psutil

                memory = psutil.virtual_memory()
                # Warning if memory usage > 85%, critical if > 95%
                if memory.percent > 95:
                    yield False
                elif memory.percent > 85:
                    yield False  # This will show as warning
                else:
                    yield True
            except ImportError:
                yield True  # Skip if psutil not available

        self.register_check(
            name="memory_usage",
            description="Check system memory usage",
            check_function=memory_check,
            critical=True,
        )

        # Async event loop check
        async def event_loop_check() -> AsyncIterator[bool]:
            try:
                loop = asyncio.get_running_loop()
                # Check if event loop is responsive
                start_time = time.time()
                await asyncio.sleep(0.001)  # 1ms sleep
                response_time = time.time() - start_time

                # Warning if response time > 10ms, critical if > 100ms
                if response_time > 0.1:  # 100ms
                    yield False
                elif response_time > 0.01:  # 10ms
                    yield False
                else:
                    yield True
            except Exception:
                yield False

        self.register_check(
            name="event_loop_responsiveness",
            description="Check async event loop responsiveness",
            check_function=event_loop_check,
            critical=True,
        )

    def register_check(
        self,
        name: str,
        description: str,
        check_function: Callable[[], AsyncIterator[bool]],
        timeout_seconds: float = 5.0,
        critical: bool = False,
        tags: Optional[List[str]] = None,
    ) -> None:
        """Register a new health check."""
        self.checks[name] = HealthCheck(
            name=name,
            description=description,
            check_function=check_function,
            timeout_seconds=timeout_seconds,
            critical=critical,
            tags=tags or [],
        )

    def unregister_check(self, name: str) -> None:
        """Unregister a health check."""
        self.checks.pop(name, None)

    async def run_check(self, name: str) -> Optional[HealthCheckResult]:
        """Run a specific health check."""
        if name not in self.checks:
            return None

        check = self.checks[name]
        if not check.enabled:
            return None

        return await check.run()

    async def run_all_checks(self) -> SystemHealth:
        """Run all enabled health checks."""
        results = []

        # Run all checks concurrently
        tasks = []
        for name, check in self.checks.items():
            if check.enabled:
                tasks.append(asyncio.create_task(check.run()))

        if tasks:
            raw_results = await asyncio.gather(*tasks, return_exceptions=True)

            # Convert exceptions to failed health check results
            processed_results: list[HealthCheckResult] = []
            for i, result in enumerate(raw_results):
                if isinstance(result, Exception):
                    check_name = list(self.checks.keys())[i]
                    processed_results.append(
                        HealthCheckResult(
                            name=check_name,
                            status=HealthStatus.CRITICAL,
                            message=f"Health check failed: {str(result)}",
                            duration_seconds=0.0,
                            critical=True,
                            error=str(result),
                        )
                    )
                else:
                    # Type check: ensure result is HealthCheckResult
                    assert isinstance(result, HealthCheckResult)
                    processed_results.append(result)

            results: list[HealthCheckResult] = processed_results
        else:
            results: list[HealthCheckResult] = []

        # Determine overall system health
        overall_status = self._determine_overall_status(results)
        overall_message = self._generate_overall_message(results, overall_status)

        system_health = SystemHealth(
            status=overall_status, message=overall_message, checks=results
        )

        # Add to history
        self.history.append(system_health)
        if len(self.history) > self.max_history:
            self.history.pop(0)

        return system_health

    def _determine_overall_status(
        self, results: List[HealthCheckResult]
    ) -> HealthStatus:
        """Determine overall system status from individual check results."""
        if not results:
            return HealthStatus.UNKNOWN

        # If any critical check fails, system is critical
        critical_failures = [
            r for r in results if r.critical and r.status == HealthStatus.CRITICAL
        ]
        if critical_failures:
            return HealthStatus.CRITICAL

        # If any check is in warning state, system has warnings
        warnings = [r for r in results if r.status == HealthStatus.WARNING]
        if warnings:
            return HealthStatus.WARNING

        # If all checks pass, system is healthy
        return HealthStatus.HEALTHY

    def _generate_overall_message(
        self, results: List[HealthCheckResult], status: HealthStatus
    ) -> str:
        """Generate overall system health message."""
        if status == HealthStatus.CRITICAL:
            critical_checks = [
                r for r in results if r.critical and r.status == HealthStatus.CRITICAL
            ]
            return f"System critical: {len(critical_checks)} critical health check(s) failed"
        elif status == HealthStatus.WARNING:
            warning_checks = [r for r in results if r.status == HealthStatus.WARNING]
            return f"System has warnings: {len(warning_checks)} health check(s) in warning state"
        elif status == HealthStatus.HEALTHY:
            return f"System healthy: All {len(results)} health checks passed"
        else:
            return "System health unknown: No health checks available"

    def get_health_history(self, hours: int = 1) -> List[SystemHealth]:
        """Get health check history for the specified number of hours."""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        return [h for h in self.history if h.timestamp >= cutoff_time]

    def export_health_report(self, filepath: str) -> None:
        """Export health report to JSON file."""
        if not self.history:
            report_data = {"message": "No health data available"}
        else:
            latest_health = self.history[-1]
            report_data = {
                "report_generated": datetime.now().isoformat(),
                "current_health": latest_health.to_dict(),
                "recent_history": [h.to_dict() for h in self.history[-10:]],
                "registered_checks": {
                    name: {
                        "description": check.description,
                        "timeout_seconds": check.timeout_seconds,
                        "critical": check.critical,
                        "enabled": check.enabled,
                        "tags": check.tags,
                    }
                    for name, check in self.checks.items()
                },
            }

        with open(filepath, "w") as f:
            json.dump(report_data, f, indent=2)


class FlowConfigValidator:
    """Configuration validation for Flow systems."""

    def __init__(self) -> None:
        self.validators: Dict[str, Callable[[Any], bool]] = {}
        self.config_schema: Dict[str, Any] = {}

        # Register default validators
        self._register_default_validators()

    def _register_default_validators(self) -> None:
        """Register default configuration validators."""

        def validate_positive_number(value: Any) -> bool:
            """Validate that value is a positive number."""
            return isinstance(value, (int, float)) and value > 0

        def validate_non_negative_number(value: Any) -> bool:
            """Validate that value is a non-negative number."""
            return isinstance(value, (int, float)) and value >= 0

        def validate_string(value: Any) -> bool:
            """Validate that value is a non-empty string."""
            return isinstance(value, str) and len(value.strip()) > 0

        def validate_boolean(value: Any) -> bool:
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

    def set_config_schema(self, schema: Dict[str, Any]) -> None:
        """Set the configuration schema for validation."""
        self.config_schema = schema

    def validate_config(self, config: Dict[str, Any]) -> List[str]:
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
            if isinstance(value, (int, float)):
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

    def validate_flow_config(self, flow: Flow, config: Dict[str, Any]) -> List[str]:
        """Validate configuration specific to a Flow.

        Args:
            flow: The Flow to validate configuration for
            config: Configuration dictionary

        Returns:
            List of validation error messages.
        """
        errors = []

        # Basic Flow configuration validation
        if "max_items" in config:
            if not isinstance(config["max_items"], int) or config["max_items"] <= 0:
                errors.append("max_items must be a positive integer")

        if "timeout_seconds" in config:
            if (
                not isinstance(config["timeout_seconds"], (int, float))
                or config["timeout_seconds"] <= 0
            ):
                errors.append("timeout_seconds must be a positive number")

        if "batch_size" in config:
            if not isinstance(config["batch_size"], int) or config["batch_size"] <= 0:
                errors.append("batch_size must be a positive integer")

        if "memory_limit_mb" in config:
            if (
                not isinstance(config["memory_limit_mb"], (int, float))
                or config["memory_limit_mb"] <= 0
            ):
                errors.append("memory_limit_mb must be a positive number")

        return errors


# Global instances
_health_monitor = FlowHealthMonitor()
_config_validator = FlowConfigValidator()


def health_check_stream(health_monitor: Optional[FlowHealthMonitor] = None) -> Flow:
    """Create a flow that performs health checks during stream processing.

    Args:
        health_monitor: Optional health monitor instance. Uses global if None.

    Returns:
        A flow that runs health checks and passes items through unchanged.
    """
    monitor = health_monitor or _health_monitor

    async def _flow(stream: AsyncIterator) -> AsyncIterator:
        async for item in stream:
            # Run a quick health check every 100 items
            if hasattr(_flow, "_item_count"):
                _flow._item_count += 1
            else:
                _flow._item_count = 1

            if _flow._item_count % 100 == 0:
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
                    if result and result.status == HealthStatus.CRITICAL:
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


def validate_flow_configuration(config: Dict[str, Any]) -> List[str]:
    """Validate flow configuration."""
    return _config_validator.validate_config(config)


def register_health_check(
    name: str,
    description: str,
    check_function: Callable[[], AsyncIterator[bool]],
    **kwargs: Any,
) -> None:
    """Register a custom health check."""
    _health_monitor.register_check(name, description, check_function, **kwargs)


def export_health_report(filepath: str) -> None:
    """Export system health report to file."""
    _health_monitor.export_health_report(filepath)
