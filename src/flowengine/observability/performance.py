"""Performance monitoring utilities for Flow streams.

This module provides comprehensive performance monitoring, timing, and observability
tools for Flow stream processing pipelines.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any

# Type aliases for performance monitoring
PerformanceData = dict[str, Any]


@dataclass
class FlowMetrics:
    """Metrics collected for a Flow execution."""

    name: str
    start_time: float
    end_time: float | None = None
    items_processed: int = 0
    items_yielded: int = 0
    errors: list[Exception] = field(default_factory=lambda: [])
    memory_usage_kb: float | None = None
    peak_memory_kb: float | None = None

    @property
    def duration_ms(self) -> float:
        """Total execution duration in milliseconds."""
        if self.end_time is None:
            return (time.time() - self.start_time) * 1000
        return (self.end_time - self.start_time) * 1000

    @property
    def throughput_items_per_sec(self) -> float:
        """Items processed per second."""
        duration_sec = self.duration_ms / 1000
        if duration_sec == 0:
            return 0.0
        return self.items_processed / duration_sec

    @property
    def yield_rate(self) -> float:
        """Ratio of items yielded to items processed."""
        if self.items_processed == 0:
            return 0.0
        return self.items_yielded / self.items_processed

    def to_dict(self) -> PerformanceData:
        """Convert metrics to dictionary for serialization."""
        return {
            "name": self.name,
            "duration_ms": self.duration_ms,
            "items_processed": self.items_processed,
            "items_yielded": self.items_yielded,
            "throughput_items_per_sec": self.throughput_items_per_sec,
            "yield_rate": self.yield_rate,
            "error_count": len(self.errors),
            "errors": [str(e) for e in self.errors],
            "memory_usage_kb": self.memory_usage_kb,
            "peak_memory_kb": self.peak_memory_kb,
        }
