"""Enhanced debugging utilities for development."""

import logging
import time
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class DebugStats:
    """Statistics collected during debug context."""

    operation_name: str
    duration: float
    success: bool
    error_type: str | None = None
    error_message: str | None = None
    metadata: dict[str, Any] | None = None


class DebugContext:
    """Context manager for enhanced debugging information."""

    def __init__(self, operation_name: str, **metadata: Any) -> None:
        """Initialize debug context.

        Args:
            operation_name: Name of the operation being tracked
            **metadata: Additional metadata to log
        """
        self.operation_name = operation_name
        self.metadata = metadata
        self.start_time: float | None = None
        self.stats: DebugStats | None = None

    def __enter__(self) -> "DebugContext":
        """Enter the debug context."""
        self.start_time = time.time()
        logger.debug(
            f"Starting {self.operation_name}",
            extra={"operation": self.operation_name, "metadata": self.metadata},
        )
        return self

    def __exit__(
        self, exc_type: type[Exception] | None, exc_val: Exception | None, exc_tb: Any
    ) -> None:
        """Exit the debug context and log results."""
        duration = time.time() - (self.start_time or 0)

        self.stats = DebugStats(
            operation_name=self.operation_name,
            duration=duration,
            success=exc_type is None,
            error_type=exc_type.__name__ if exc_type else None,
            error_message=str(exc_val) if exc_val else None,
            metadata=self.metadata,
        )

        if exc_type:
            logger.error(
                f"{self.operation_name} failed after {duration:.2f}s",
                extra={
                    "operation": self.operation_name,
                    "duration": duration,
                    "error_type": exc_type.__name__,
                    "error_message": str(exc_val),
                    "metadata": self.metadata,
                },
                exc_info=True,
            )
        else:
            logger.debug(
                f"{self.operation_name} completed in {duration:.2f}s",
                extra={
                    "operation": self.operation_name,
                    "duration": duration,
                    "metadata": self.metadata,
                },
            )

    def add_metadata(self, **kwargs: Any) -> None:
        """Add additional metadata during execution.

        Args:
            **kwargs: Metadata to add
        """
        self.metadata.update(kwargs)


@contextmanager
def debug_operation(operation_name: str, **metadata: Any) -> Iterator[DebugContext]:
    """Context manager for tracking operation execution.

    Args:
        operation_name: Name of the operation
        **metadata: Additional metadata

    Yields:
        DebugContext instance
    """
    ctx = DebugContext(operation_name, **metadata)
    try:
        yield ctx
    finally:
        ctx.__exit__(None, None, None)


def log_function_call(func_name: str, *args: Any, **kwargs: Any) -> None:
    """Log a function call with arguments (safely).

    Args:
        func_name: Name of the function
        *args: Positional arguments
        **kwargs: Keyword arguments
    """
    # Safely convert args to string representations
    safe_args = []
    for arg in args:
        try:
            if isinstance(arg, str | int | float | bool | type(None)):
                safe_args.append(repr(arg))
            else:
                safe_args.append(f"<{type(arg).__name__}>")
        except Exception:
            safe_args.append("<unknown>")

    # Safely convert kwargs
    safe_kwargs = {}
    for key, value in kwargs.items():
        try:
            if isinstance(value, str | int | float | bool | type(None)):
                safe_kwargs[key] = repr(value)
            else:
                safe_kwargs[key] = f"<{type(value).__name__}>"
        except Exception:
            safe_kwargs[key] = "<unknown>"

    logger.debug(
        f"Calling {func_name}",
        extra={"function": func_name, "args": safe_args, "kwargs": safe_kwargs},
    )
