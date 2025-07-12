from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any, Generic, TypeVar

T = TypeVar("T")


@dataclass
class FlowCommandResult(Generic[T]):
    """Structured result from flow command execution."""

    success: bool
    data: T | None = None
    error: str | None = None
    metadata: dict[str, Any] = field(default_factory=lambda: {})
    execution_time: float = 0.0

    def to_json(self) -> dict[str, Any]:
        """Convert result to JSON representation."""
        return {
            "success": self.success,
            "data": self.data,
            "error": self.error,
            "metadata": self.metadata,
            "execution_time": self.execution_time,
        }

    @classmethod
    def success_result(
        cls, data: T, execution_time: float = 0.0
    ) -> FlowCommandResult[T]:
        """Create successful result."""
        return cls(success=True, data=data, execution_time=execution_time)

    @classmethod
    def error_result(
        cls, error: str, execution_time: float = 0.0
    ) -> FlowCommandResult[T]:
        """Create error result."""
        return cls(success=False, error=error, execution_time=execution_time)

    @classmethod
    def timed_execution(
        cls, func: Any, *args: Any, **kwargs: Any
    ) -> FlowCommandResult[T]:
        """Execute function and create timed result."""
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            return cls.success_result(result, execution_time)
        except Exception as e:
            execution_time = time.time() - start_time
            return cls.error_result(str(e), execution_time)
