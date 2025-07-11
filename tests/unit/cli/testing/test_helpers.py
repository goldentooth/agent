"""Tests for CLI testing helpers."""

from unittest.mock import Mock

import pytest
from click.testing import Result

from goldentooth_agent.cli.core.context import CommandContext, CommandResult
from goldentooth_agent.cli.testing.helpers import (
    CLITestCase,
    assert_command_called_with,
    create_test_context,
    mock_command_implementation,
    run_command,
)


class TestCLITestCase:
    """Test CLITestCase functionality."""

    def test_cli_test_case_init(self) -> None:
        """Test CLITestCase initialization."""
        test_case = CLITestCase()

        assert test_case.runner is not None

    def test_assert_success(self) -> None:
        """Test assert_success method."""
        test_case = CLITestCase()
        result = Mock(spec=Result)
        result.exit_code = 0
        result.output = "success"

        # Should not raise
        test_case.assert_success(result)

    def test_assert_success_failure(self) -> None:
        """Test assert_success method with failure."""
        test_case = CLITestCase()
        result = Mock(spec=Result)
        result.exit_code = 1
        result.output = "error"

        with pytest.raises(AssertionError):
            test_case.assert_success(result)

    def test_assert_failure(self) -> None:
        """Test assert_failure method."""
        test_case = CLITestCase()
        result = Mock(spec=Result)
        result.exit_code = 1

        # Should not raise
        test_case.assert_failure(result)

    def test_assert_failure_wrong_code(self) -> None:
        """Test assert_failure method with wrong exit code."""
        test_case = CLITestCase()
        result = Mock(spec=Result)
        result.exit_code = 2

        with pytest.raises(AssertionError):
            test_case.assert_failure(result, expected_exit_code=1)

    def test_assert_output_contains(self) -> None:
        """Test assert_output_contains method."""
        test_case = CLITestCase()
        result = Mock(spec=Result)
        result.output = "test output with expected text"

        # Should not raise
        test_case.assert_output_contains(result, "expected text")

    def test_assert_output_contains_failure(self) -> None:
        """Test assert_output_contains method with failure."""
        test_case = CLITestCase()
        result = Mock(spec=Result)
        result.output = "test output"

        with pytest.raises(AssertionError):
            test_case.assert_output_contains(result, "missing text")

    def test_assert_output_not_contains(self) -> None:
        """Test assert_output_not_contains method."""
        test_case = CLITestCase()
        result = Mock(spec=Result)
        result.output = "test output"

        # Should not raise
        test_case.assert_output_not_contains(result, "missing text")

    def test_assert_output_not_contains_failure(self) -> None:
        """Test assert_output_not_contains method with failure."""
        test_case = CLITestCase()
        result = Mock(spec=Result)
        result.output = "test output with unwanted text"

        with pytest.raises(AssertionError):
            test_case.assert_output_not_contains(result, "unwanted text")


class TestHelperFunctions:
    """Test helper functions."""

    def test_mock_command_implementation_default(self) -> None:
        """Test mock_command_implementation with defaults."""
        mock_func = mock_command_implementation()

        result = mock_func()
        assert isinstance(result, CommandResult)
        assert result.success is True
        assert result.error_message is None
        assert result.execution_time == 0.1

    def test_mock_command_implementation_custom(self) -> None:
        """Test mock_command_implementation with custom values."""
        mock_func = mock_command_implementation(
            return_value={"key": "value"},
            success=False,
            error_message="test error",
            execution_time=0.5,
        )

        result = mock_func()
        assert isinstance(result, CommandResult)
        assert result.data == {"key": "value"}
        assert result.success is False
        assert result.error_message == "test error"
        assert result.execution_time == 0.5

    def test_assert_command_called_with_args_only(self) -> None:
        """Test assert_command_called_with with args only."""
        mock_func = Mock()
        mock_func("arg1", "arg2")

        # Should not raise
        assert_command_called_with(mock_func, ("arg1", "arg2"))

    def test_assert_command_called_with_args_and_kwargs(self) -> None:
        """Test assert_command_called_with with args and kwargs."""
        mock_func = Mock()
        mock_func("arg1", key="value")

        # Should not raise
        assert_command_called_with(mock_func, ("arg1",), {"key": "value"})

    def test_assert_command_called_with_failure(self) -> None:
        """Test assert_command_called_with with failure."""
        mock_func = Mock()
        mock_func("wrong_arg")

        with pytest.raises(AssertionError):
            assert_command_called_with(mock_func, ("correct_arg",))

    def test_create_test_context_default(self) -> None:
        """Test create_test_context with defaults."""
        context = create_test_context()

        assert isinstance(context, CommandContext)
        assert context.output_format == "text"
        assert context.plain_output is True
        assert context.interactive is False
        assert context.console is not None

    def test_create_test_context_custom(self) -> None:
        """Test create_test_context with custom values."""
        context = create_test_context(
            output_format="json", plain_output=False, interactive=True, record_svg=True
        )

        assert isinstance(context, CommandContext)
        assert context.output_format == "json"
        assert context.plain_output is False
        assert context.interactive is True
        assert context.record_svg is True
