from __future__ import annotations


class FlowCommandError(Exception):
    """Base exception for flow command operations."""

    def __init__(self, message: str, details: str | None = None) -> None:
        """Initialize flow command error.

        Args:
            message: Error message
            details: Optional additional error details
        """
        super().__init__(message)
        self.message = message
        self.details = details


class FlowCommandExecutionError(FlowCommandError):
    """Exception raised when flow execution fails."""


class FlowCommandTimeoutError(FlowCommandError):
    """Exception raised when flow execution times out."""
