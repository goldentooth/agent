"""Core health monitoring functionality for Flow systems.

This module provides the foundational classes for health monitoring,
including health status definitions, health checks, and system health tracking.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

# Type aliases
HealthMetadata = dict[str, Any]
HealthData = dict[str, Any]


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
