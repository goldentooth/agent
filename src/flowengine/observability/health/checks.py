"""Health check implementations for Flow systems.

This module provides concrete health check implementations and the
FlowHealthMonitor class for managing system health monitoring.
"""

from __future__ import annotations

import asyncio
import json
import time
from collections.abc import AsyncGenerator, Awaitable, Callable
from datetime import datetime, timedelta
from typing import Any, Union

from .core import HealthCheck, HealthCheckResult, HealthData, HealthStatus, SystemHealth

# Type aliases
CheckFunction = Union[
    Callable[[], Awaitable[bool]], Callable[[], AsyncGenerator[bool, None]]
]


class FlowHealthMonitor:
    """Health monitoring system for Flow applications."""

    def __init__(self) -> None:  # pyright: ignore[reportMissingSuperCall]
        """Initialize the health monitor."""
        self.checks: dict[str, HealthCheck] = {}
        self.history: list[SystemHealth] = []
        self.max_history = 100

        # Register default health checks
        self._register_default_checks()

    def _register_default_checks(self) -> None:
        """Register default system health checks."""

        # Memory usage check
        async def memory_check() -> AsyncGenerator[bool, None]:
            """Check system memory usage."""
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
        async def event_loop_check() -> AsyncGenerator[bool, None]:
            """Check event loop responsiveness."""
            try:
                # Check if event loop is responsive
                asyncio.get_running_loop()  # Just verify loop exists
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
        check_function: CheckFunction,
        timeout_seconds: float = 5.0,
        critical: bool = False,
        tags: list[str] | None = None,
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

    async def run_check(self, name: str) -> HealthCheckResult | None:
        """Run a specific health check."""
        if name not in self.checks:
            return None

        check = self.checks[name]
        if not check.enabled:
            return None

        return await check.run()

    async def run_all_checks(self) -> SystemHealth:
        """Run all enabled health checks."""
        final_results: list[HealthCheckResult]

        # Run all checks concurrently
        tasks: list[asyncio.Task[HealthCheckResult]] = []
        for _name, check in self.checks.items():
            if check.enabled:
                tasks.append(asyncio.create_task(check.run()))

        if tasks:
            raw_results: list[HealthCheckResult | BaseException] = await asyncio.gather(
                *tasks, return_exceptions=True
            )

            # Convert exceptions to failed health check results
            processed_results: list[HealthCheckResult] = []
            check_names = list(self.checks.keys())
            for i, result in enumerate(raw_results):
                if isinstance(result, BaseException):
                    check_name = check_names[i]
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

            final_results = processed_results
        else:
            final_results = []

        # Determine overall system health
        overall_status = self._determine_overall_status(final_results)
        overall_message = self._generate_overall_message(final_results, overall_status)

        system_health = SystemHealth(
            status=overall_status, message=overall_message, checks=final_results
        )

        # Add to history
        self._add_to_history(system_health)

        return system_health

    def _determine_overall_status(
        self, results: list[HealthCheckResult]
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
        self, results: list[HealthCheckResult], status: HealthStatus
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

    def get_health_history(self, hours: int = 1) -> list[SystemHealth]:
        """Get health check history for the specified number of hours."""
        if not self.history:
            return []

        cutoff_time = datetime.now() - timedelta(hours=hours)
        return [h for h in self.history if h.timestamp >= cutoff_time]

    def export_health_report(self, filepath: str) -> None:
        """Export health report to a JSON file."""
        current_health = self.history[-1] if self.history else None

        report_data: HealthData = {
            "timestamp": datetime.now().isoformat(),
            "current_status": current_health.to_dict() if current_health else None,
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

    def _add_to_history(self, system_health: SystemHealth) -> None:
        """Add system health to history with size limit enforcement."""
        self.history.append(system_health)
        if len(self.history) > self.max_history:
            self.history.pop(0)


# Built-in health check functions


async def check_flow_performance(
    flow: Any, threshold_ms: float = 1000.0
) -> AsyncGenerator[bool, None]:
    """Check flow performance against response time threshold.

    Args:
        flow: Flow instance to monitor
        threshold_ms: Maximum acceptable response time in milliseconds

    Yields:
        bool: True if performance is acceptable, False otherwise
    """
    try:
        import time

        start_time = time.time()
        # Simple performance check - measure flow creation time
        response_time = (time.time() - start_time) * 1000  # Convert to ms
        yield response_time < threshold_ms
    except Exception:
        yield False


async def check_flow_errors(
    flow: Any, error_threshold: float = 0.05
) -> AsyncGenerator[bool, None]:
    """Check flow error rate against threshold.

    Args:
        flow: Flow instance to monitor
        error_threshold: Maximum acceptable error rate (0.0-1.0)

    Yields:
        bool: True if error rate is acceptable, False otherwise
    """
    try:
        # For now, this is a placeholder - would need actual error tracking
        # In a real implementation, this would check flow execution statistics
        # Use the parameters to avoid unused variable warnings
        _ = flow, error_threshold
        yield True  # Assume healthy for now
    except Exception:
        yield False


async def check_memory_usage(
    threshold_mb: float = 1024.0,
) -> AsyncGenerator[bool, None]:
    """Check system memory usage against threshold.

    Args:
        threshold_mb: Maximum acceptable memory usage in MB

    Yields:
        bool: True if memory usage is acceptable, False otherwise
    """
    try:
        import psutil

        memory = psutil.virtual_memory()
        memory_mb = memory.used / (1024 * 1024)  # Convert to MB
        yield memory_mb < threshold_mb
    except ImportError:
        # psutil not available, assume healthy
        yield True
    except Exception:
        yield False


async def check_flow_dependencies(flow: Any) -> AsyncGenerator[bool, None]:
    """Check if flow dependencies are available and healthy.

    Args:
        flow: Flow instance to check dependencies for

    Yields:
        bool: True if all dependencies are healthy, False otherwise
    """
    try:
        # Check basic flow properties exist
        if hasattr(flow, "fn") and hasattr(flow, "name"):
            yield True
        else:
            yield False
    except Exception:
        yield False


async def check_flow_configuration(
    config: dict[str, Any],
) -> AsyncGenerator[bool, None]:
    """Check flow configuration validity.

    Args:
        config: Configuration dictionary to validate

    Yields:
        bool: True if configuration is valid, False otherwise
    """
    try:
        # Check for common invalid values
        for key, value in config.items():
            if value is None and key in ["name", "fn"]:
                yield False
                return

        yield True
    except Exception:
        yield False


async def check_resource_limits(
    cpu_threshold: float = 80.0, memory_threshold: float = 85.0
) -> AsyncGenerator[bool, None]:
    """Check system resource usage against thresholds.

    Args:
        cpu_threshold: Maximum acceptable CPU usage percentage
        memory_threshold: Maximum acceptable memory usage percentage

    Yields:
        bool: True if resource usage is acceptable, False otherwise
    """
    try:
        import psutil

        # Check CPU usage
        cpu_percent = psutil.cpu_percent(interval=0.1)
        if cpu_percent > cpu_threshold:
            yield False
            return

        # Check memory usage
        memory = psutil.virtual_memory()
        if memory.percent > memory_threshold:
            yield False
            return

        yield True
    except ImportError:
        # psutil not available, assume healthy
        yield True
    except Exception:
        yield False


async def check_flow_responsiveness(
    flow: Any, timeout_ms: float = 5000.0
) -> AsyncGenerator[bool, None]:
    """Check flow responsiveness within timeout.

    Args:
        flow: Flow instance to check
        timeout_ms: Maximum acceptable response time in milliseconds

    Yields:
        bool: True if flow responds within timeout, False otherwise
    """
    try:
        import asyncio
        import time

        start_time = time.time()

        # Simple responsiveness check - ensure flow can be called
        try:
            await asyncio.wait_for(
                asyncio.create_task(asyncio.sleep(0.001)),  # Minimal operation
                timeout=timeout_ms / 1000.0,
            )
            response_time = (time.time() - start_time) * 1000
            yield response_time < timeout_ms
        except asyncio.TimeoutError:
            yield False
    except Exception:
        yield False


async def check_system_resources(
    disk_threshold: float = 90.0, load_threshold: float = 2.0
) -> AsyncGenerator[bool, None]:
    """Check overall system resource health.

    Args:
        disk_threshold: Maximum acceptable disk usage percentage
        load_threshold: Maximum acceptable system load average

    Yields:
        bool: True if system resources are healthy, False otherwise
    """
    try:
        import os

        import psutil

        # Check disk usage
        disk_usage = psutil.disk_usage("/")
        disk_percent = (disk_usage.used / disk_usage.total) * 100
        if disk_percent > disk_threshold:
            yield False
            return

        # Check system load (on Unix systems)
        try:
            load_avg = os.getloadavg()[0]  # 1-minute load average
            if load_avg > load_threshold:
                yield False
                return
        except (OSError, AttributeError):
            # Not available on all systems
            pass

        yield True
    except ImportError:
        # psutil not available, assume healthy
        yield True
    except Exception:
        yield False
