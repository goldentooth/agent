from __future__ import annotations

import pytest

from flow_command.core.exceptions import (
    FlowCommandError,
    FlowCommandExecutionError,
    FlowCommandTimeoutError,
)


class TestFlowCommandError:
    """Test suite for FlowCommandError base exception."""

    def test_flow_command_error_basic(self) -> None:
        """FlowCommandError should create with message only."""
        error = FlowCommandError("Test error")
        assert str(error) == "Test error"
        assert error.message == "Test error"
        assert error.details is None

    def test_flow_command_error_with_details(self) -> None:
        """FlowCommandError should support additional details."""
        error = FlowCommandError("Test error", "Additional details")
        assert str(error) == "Test error"
        assert error.message == "Test error"
        assert error.details == "Additional details"

    def test_flow_command_error_inheritance(self) -> None:
        """FlowCommandError should inherit from Exception."""
        error = FlowCommandError("Test error")
        assert isinstance(error, Exception)


class TestFlowCommandExecutionError:
    """Test suite for FlowCommandExecutionError."""

    def test_flow_command_execution_error_basic(self) -> None:
        """FlowCommandExecutionError should create with message."""
        error = FlowCommandExecutionError("Execution failed")
        assert str(error) == "Execution failed"
        assert error.message == "Execution failed"

    def test_flow_command_execution_error_inheritance(self) -> None:
        """FlowCommandExecutionError should inherit from FlowCommandError."""
        error = FlowCommandExecutionError("Execution failed")
        assert isinstance(error, FlowCommandError)
        assert isinstance(error, Exception)


class TestFlowCommandTimeoutError:
    """Test suite for FlowCommandTimeoutError."""

    def test_flow_command_timeout_error_basic(self) -> None:
        """FlowCommandTimeoutError should create with message."""
        error = FlowCommandTimeoutError("Operation timed out")
        assert str(error) == "Operation timed out"
        assert error.message == "Operation timed out"

    def test_flow_command_timeout_error_inheritance(self) -> None:
        """FlowCommandTimeoutError should inherit from FlowCommandError."""
        error = FlowCommandTimeoutError("Operation timed out")
        assert isinstance(error, FlowCommandError)
        assert isinstance(error, Exception)

    def test_flow_command_timeout_error_with_details(self) -> None:
        """FlowCommandTimeoutError should support details."""
        error = FlowCommandTimeoutError("Timeout", "After 30 seconds")
        assert error.message == "Timeout"
        assert error.details == "After 30 seconds"
