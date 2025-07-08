"""Core health monitoring functionality for Flow systems.

This module provides the foundational classes for health monitoring,
including health status definitions, health checks, and system health tracking.
"""

from __future__ import annotations

import asyncio
import time
from collections.abc import AsyncGenerator, Awaitable, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, TypeVar, Union, cast

# Type aliases
HealthMetadata = dict[str, Any]
HealthData = dict[str, Any]
CheckFunction = Union[
    Callable[[], Awaitable[bool]], Callable[[], AsyncGenerator[bool, None]]
]


class HealthStatus(Enum):
    """Health status levels for system components."""

    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"
    UNKNOWN = "unknown"


@dataclass
class HealthCheckResult:
    """Result of a health check execution."""

    name: str
    status: HealthStatus
    message: str
    duration_seconds: float
    critical: bool = False
    error: str | None = None
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: HealthMetadata = field(default_factory=lambda: {})

    def to_dict(self) -> HealthData:
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
    checks: list[HealthCheckResult]
    timestamp: datetime = field(default_factory=datetime.now)

    @property
    def healthy_checks(self) -> list[HealthCheckResult]:
        """Get all healthy checks."""
        return [check for check in self.checks if check.status == HealthStatus.HEALTHY]

    @property
    def warning_checks(self) -> list[HealthCheckResult]:
        """Get all warning checks."""
        return [check for check in self.checks if check.status == HealthStatus.WARNING]

    @property
    def critical_checks(self) -> list[HealthCheckResult]:
        """Get all critical checks."""
        return [check for check in self.checks if check.status == HealthStatus.CRITICAL]

    def to_dict(self) -> HealthData:
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


@dataclass
class HealthCheck:
    """Individual health check definition."""

    name: str
    description: str
    check_function: CheckFunction
    timeout_seconds: float = 5.0
    critical: bool = False
    enabled: bool = True
    tags: list[str] = field(default_factory=lambda: [])

    async def run(self) -> HealthCheckResult:
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
        check_result = self.check_function()

        # Handle both async generators and regular async functions
        if hasattr(check_result, "__aiter__"):
            # It's an async generator - safe to cast since we checked
            gen = cast(AsyncGenerator[bool, None], check_result)
            async for result in gen:
                return bool(result)
            return False
        else:
            # It's a regular coroutine - safe to cast since not a generator
            coro = check_result
            result = (
                await coro
            )  # pyright: ignore[reportGeneralTypeIssues, reportUnknownVariableType]
            return bool(
                result
            )  # pyright: ignore[reportUnknownArgumentType, reportUnknownVariableType]
