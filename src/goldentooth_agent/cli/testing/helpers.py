"""Test helpers for CLI command testing."""

from typing import Any, Optional
from unittest.mock import Mock

from click.testing import Result
from typer.testing import CliRunner

from ..core import CommandContext, CommandResult
from ..main import app


class CLITestCase:
    """Base class for CLI test cases with common utilities."""

    def __init__(self) -> None:
        super().__init__()
        self.runner = CliRunner()

    def run_command(
        self,
        command: list[str],
        input_data: Optional[str] = None,
        catch_exceptions: bool = True,
    ) -> Result:
        """Run a CLI command and return the result."""
        return self.runner.invoke(
            app,
            command,
            input=input_data,
            catch_exceptions=catch_exceptions,
        )

    def assert_success(self, result: Result) -> None:
        """Assert that a command result indicates success."""
        assert result.exit_code == 0, f"Command failed with: {result.output}"

    def assert_failure(self, result: Result, expected_exit_code: int = 1) -> None:
        """Assert that a command result indicates failure."""
        assert (
            result.exit_code == expected_exit_code
        ), f"Expected exit code {expected_exit_code}, got {result.exit_code}"

    def assert_output_contains(self, result: Result, expected: str) -> None:
        """Assert that command output contains expected text."""
        assert (
            expected in result.output
        ), f"Expected '{expected}' in output: {result.output}"

    def assert_output_not_contains(self, result: Result, unexpected: str) -> None:
        """Assert that command output does not contain unexpected text."""
        assert (
            unexpected not in result.output
        ), f"Unexpected '{unexpected}' in output: {result.output}"


def run_command(
    command: list[str],
    input_data: Optional[str] = None,
    catch_exceptions: bool = True,
) -> Result:
    """Run a CLI command and return the result."""
    runner = CliRunner()
    return runner.invoke(
        app,
        command,
        input=input_data,
        catch_exceptions=catch_exceptions,
    )


def mock_command_implementation(
    return_value: Any = None,
    success: bool = True,
    error_message: Optional[str] = None,
    execution_time: float = 0.1,
) -> Mock:
    """Create a mock command implementation function."""
    result = CommandResult(
        data=return_value,
        success=success,
        error_message=error_message,
        execution_time=execution_time,
    )

    mock_func = Mock(return_value=result)
    return mock_func


def assert_command_called_with(
    mock_func: Mock,
    expected_args: tuple[Any, ...],
    expected_kwargs: Optional[dict[str, Any]] = None,
) -> None:
    """Assert that a mock command function was called with expected arguments."""
    if expected_kwargs is None:
        expected_kwargs = {}

    mock_func.assert_called_once_with(*expected_args, **expected_kwargs)


def create_test_context(
    output_format: str = "text",
    plain_output: bool = True,
    interactive: bool = False,
    **kwargs: Any,
) -> CommandContext:
    """Create a test command context with specified options."""
    return CommandContext(
        output_format=output_format,
        plain_output=plain_output,
        interactive=interactive,
        console=Mock(),
        **kwargs,
    )
