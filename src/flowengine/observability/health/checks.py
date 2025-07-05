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
from typing import Union

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
