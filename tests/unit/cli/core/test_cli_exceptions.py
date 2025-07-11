"""Tests for CLI exceptions."""

import pytest

from goldentooth_agent.cli.core.exceptions import CLIError


class TestCLIError:
    """Test CLIError exception functionality."""

    def test_cli_error_default(self) -> None:
        """Test CLIError with default exit code."""
        error = CLIError("test error")

        assert str(error) == "test error"
        assert error.exit_code == 1

    def test_cli_error_custom_exit_code(self) -> None:
        """Test CLIError with custom exit code."""
        error = CLIError("test error", exit_code=2)

        assert str(error) == "test error"
        assert error.exit_code == 2

    def test_cli_error_raise(self) -> None:
        """Test raising CLIError."""
        with pytest.raises(CLIError) as exc_info:
            raise CLIError("test error", exit_code=3)

        assert str(exc_info.value) == "test error"
        assert exc_info.value.exit_code == 3

    def test_cli_error_inheritance(self) -> None:
        """Test CLIError inheritance."""
        error = CLIError("test error")

        assert isinstance(error, Exception)
        assert hasattr(error, "exit_code")
