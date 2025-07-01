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
            # Generate debugging suggestions for errors
            debugging_suggestions = ""
            if exc_val is not None:
                debugging_suggestions = self._generate_error_debugging_suggestions(
                    exc_type, exc_val
                )

            logger.error(
                f"{self.operation_name} failed after {duration:.2f}s\n\n"
                f"🔧 DEBUGGING SUGGESTIONS:\n{debugging_suggestions}\n\n"
                f"📚 See: guidelines/debugging-guide.md for complete debugging reference",
                extra={
                    "operation": self.operation_name,
                    "duration": duration,
                    "error_type": exc_type.__name__,
                    "error_message": str(exc_val),
                    "metadata": self.metadata,
                    "debugging_suggestions": debugging_suggestions,
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

    def _generate_error_debugging_suggestions(
        self, exc_type: type[Exception], exc_val: Exception
    ) -> str:
        """Generate context-aware debugging suggestions based on error type."""
        suggestions = []

        # Error-specific suggestions
        if exc_type.__name__ == "AttributeError":
            suggestions.extend(
                [
                    "• Check for dict vs object access patterns (result.attr vs result['attr'])",
                    "• Use DetailedAttributeError from core/util/error_reporting.py for enhanced context",
                    "• Trace execution: goldentooth-agent debug trace --verbose",
                ]
            )
        elif exc_type.__name__ == "KeyError":
            suggestions.extend(
                [
                    "• Verify dictionary structure and available keys",
                    "• Use safe_dict_access() from core/util/error_reporting.py",
                    "• Check system health: goldentooth-agent debug health",
                ]
            )
        elif exc_type.__name__ in ["TimeoutError", "asyncio.TimeoutError"]:
            suggestions.extend(
                [
                    "• Profile performance: goldentooth-agent debug profile [command]",
                    "• Use PerformanceMonitor for detailed timing analysis",
                    "• Check for deadlocks or blocking operations",
                ]
            )
        elif "Flow" in exc_type.__name__:
            suggestions.extend(
                [
                    "• Use FlowDebugger for interactive debugging",
                    "• Add observability with monitored_stream() combinator",
                    "• Analyze flow composition with flow_engine/observability/analysis.py",
                ]
            )
        else:
            suggestions.extend(
                [
                    "• General health check: goldentooth-agent debug health",
                    "• Trace execution: goldentooth-agent debug trace --verbose",
                ]
            )

        # Operation-specific suggestions based on metadata
        if "agent" in self.operation_name.lower():
            suggestions.append(
                "• Agent-specific: goldentooth-agent debug health --component agents"
            )
        elif "flow" in self.operation_name.lower():
            suggestions.append(
                "• Flow-specific: Use flow observability tools in flow_engine/observability/"
            )

        # Always add general debugging tools
        suggestions.extend(
            [
                "",
                "🔍 ADVANCED DEBUGGING:",
                "• Interactive debugging: FlowDebugger in flow_engine/observability/debugging.py",
                "• Performance analysis: PerformanceMonitor in flow_engine/observability/performance.py",
                "• Stream inspection: Use inspect_stream() combinator for runtime analysis",
            ]
        )

        return "\n".join(suggestions)


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
    ctx.__enter__()
    try:
        yield ctx
    except Exception as e:
        ctx.__exit__(type(e), e, e.__traceback__)
        raise
    else:
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
        extra={
            "function": func_name,
            "function_args": safe_args,
            "function_kwargs": safe_kwargs,
        },
    )
