"""Core health monitoring functionality for Flow systems.

This module provides the foundational classes for health monitoring,
including health status definitions, health checks, and system health tracking.
"""

from __future__ import annotations

from enum import Enum


class HealthStatus(Enum):
    """Health status levels for system components."""

    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"
    UNKNOWN = "unknown"
