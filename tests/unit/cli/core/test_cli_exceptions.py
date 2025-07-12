"""Tests for CLI exceptions."""

import pytest

from goldentooth_agent.cli.core.exceptions import (
    AuthenticationError,
    CLIError,
    CommandNotFoundError,
    ExecutionError,
    InvalidInputError,
    NetworkError,
)


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

    def test_cli_error_with_show_traceback_true(self) -> None:
        """Test CLIError with show_traceback set to True."""
        error = CLIError("test error", show_traceback=True)

        assert str(error) == "test error"
        assert error.exit_code == 1
        assert error.show_traceback is True

    def test_cli_error_with_show_traceback_false(self) -> None:
        """Test CLIError with show_traceback set to False (default)."""
        error = CLIError("test error", show_traceback=False)

        assert str(error) == "test error"
        assert error.exit_code == 1
        assert error.show_traceback is False

    def test_cli_error_all_parameters(self) -> None:
        """Test CLIError with all parameters set."""
        error = CLIError("test error", exit_code=5, show_traceback=True)

        assert str(error) == "test error"
        assert error.exit_code == 5
        assert error.show_traceback is True


class TestCommandNotFoundError:
    """Test CommandNotFoundError exception functionality."""

    def test_command_not_found_error_basic(self) -> None:
        """Test CommandNotFoundError with basic command name."""
        error = CommandNotFoundError("nonexistent")

        assert str(error) == "Command 'nonexistent' not found"
        assert error.exit_code == 2
        assert isinstance(error, CLIError)

    def test_command_not_found_error_empty_command(self) -> None:
        """Test CommandNotFoundError with empty command name."""
        error = CommandNotFoundError("")

        assert str(error) == "Command '' not found"
        assert error.exit_code == 2

    def test_command_not_found_error_special_characters(self) -> None:
        """Test CommandNotFoundError with special characters in command name."""
        error = CommandNotFoundError("my-command_123")

        assert str(error) == "Command 'my-command_123' not found"
        assert error.exit_code == 2

    def test_command_not_found_error_inheritance(self) -> None:
        """Test CommandNotFoundError inheritance."""
        error = CommandNotFoundError("test")

        assert isinstance(error, CLIError)
        assert isinstance(error, Exception)

    def test_command_not_found_error_raise(self) -> None:
        """Test raising CommandNotFoundError."""
        with pytest.raises(CommandNotFoundError) as exc_info:
            raise CommandNotFoundError("missing")

        assert "Command 'missing' not found" in str(exc_info.value)
        assert exc_info.value.exit_code == 2


class TestInvalidInputError:
    """Test InvalidInputError exception functionality."""

    def test_invalid_input_error_without_suggestion(self) -> None:
        """Test InvalidInputError without suggestion."""
        error = InvalidInputError("Invalid input provided")

        assert str(error) == "Invalid input provided"
        assert error.exit_code == 1
        assert isinstance(error, CLIError)

    def test_invalid_input_error_with_suggestion(self) -> None:
        """Test InvalidInputError with suggestion."""
        error = InvalidInputError("Invalid input provided", "Try using --help")

        expected_message = "Invalid input provided\n\nSuggestion: Try using --help"
        assert str(error) == expected_message
        assert error.exit_code == 1

    def test_invalid_input_error_with_none_suggestion(self) -> None:
        """Test InvalidInputError with None suggestion."""
        error = InvalidInputError("Invalid input provided", None)

        assert str(error) == "Invalid input provided"
        assert error.exit_code == 1

    def test_invalid_input_error_with_empty_suggestion(self) -> None:
        """Test InvalidInputError with empty suggestion."""
        error = InvalidInputError("Invalid input provided", "")

        # Empty string is falsy, so suggestion should NOT be included
        assert str(error) == "Invalid input provided"
        assert error.exit_code == 1

    def test_invalid_input_error_with_space_suggestion(self) -> None:
        """Test InvalidInputError with space-only suggestion (truthy)."""
        error = InvalidInputError("Invalid input provided", " ")

        # Space string is truthy, so suggestion should be included
        expected_message = "Invalid input provided\n\nSuggestion:  "
        assert str(error) == expected_message
        assert error.exit_code == 1

    def test_invalid_input_error_inheritance(self) -> None:
        """Test InvalidInputError inheritance."""
        error = InvalidInputError("test")

        assert isinstance(error, CLIError)
        assert isinstance(error, Exception)

    def test_invalid_input_error_raise(self) -> None:
        """Test raising InvalidInputError."""
        with pytest.raises(InvalidInputError) as exc_info:
            raise InvalidInputError("Bad input", "Use correct format")

        assert "Bad input" in str(exc_info.value)
        assert "Suggestion: Use correct format" in str(exc_info.value)
        assert exc_info.value.exit_code == 1


class TestExecutionError:
    """Test ExecutionError exception functionality."""

    def test_execution_error_without_original_error(self) -> None:
        """Test ExecutionError without original error."""
        error = ExecutionError("Command failed")

        assert str(error) == "Command failed"
        assert error.exit_code == 1
        assert error.show_traceback is False
        assert error.original_error is None
        assert isinstance(error, CLIError)

    def test_execution_error_with_original_error(self) -> None:
        """Test ExecutionError with original error."""
        original = ValueError("Original error message")
        error = ExecutionError("Command failed", original_error=original)

        expected_message = "Command failed\nCaused by: Original error message"
        assert str(error) == expected_message
        assert error.exit_code == 1
        assert error.show_traceback is False
        assert error.original_error is original

    def test_execution_error_with_original_error_and_traceback(self) -> None:
        """Test ExecutionError with original error and show_traceback=True."""
        original = RuntimeError("Runtime issue")
        error = ExecutionError(
            "Command failed", original_error=original, show_traceback=True
        )

        expected_message = "Command failed\nCaused by: Runtime issue"
        assert str(error) == expected_message
        assert error.exit_code == 1
        assert error.show_traceback is True
        assert error.original_error is original

    def test_execution_error_with_none_original_error(self) -> None:
        """Test ExecutionError with None original error."""
        error = ExecutionError("Command failed", original_error=None)

        assert str(error) == "Command failed"
        assert error.exit_code == 1
        assert error.original_error is None

    def test_execution_error_show_traceback_only(self) -> None:
        """Test ExecutionError with only show_traceback parameter."""
        error = ExecutionError("Command failed", show_traceback=True)

        assert str(error) == "Command failed"
        assert error.exit_code == 1
        assert error.show_traceback is True
        assert error.original_error is None

    def test_execution_error_inheritance(self) -> None:
        """Test ExecutionError inheritance."""
        error = ExecutionError("test")

        assert isinstance(error, CLIError)
        assert isinstance(error, Exception)

    def test_execution_error_raise(self) -> None:
        """Test raising ExecutionError."""
        original = FileNotFoundError("File not found")
        with pytest.raises(ExecutionError) as exc_info:
            raise ExecutionError("Failed to process", original)

        assert "Failed to process" in str(exc_info.value)
        assert "Caused by: File not found" in str(exc_info.value)
        assert exc_info.value.exit_code == 1
        assert exc_info.value.original_error is original


class TestAuthenticationError:
    """Test AuthenticationError exception functionality."""

    def test_authentication_error_default_message(self) -> None:
        """Test AuthenticationError with default message."""
        error = AuthenticationError()

        assert str(error) == "Authentication failed"
        assert error.exit_code == 3
        assert isinstance(error, CLIError)

    def test_authentication_error_custom_message(self) -> None:
        """Test AuthenticationError with custom message."""
        error = AuthenticationError("Invalid credentials provided")

        assert str(error) == "Invalid credentials provided"
        assert error.exit_code == 3

    def test_authentication_error_empty_message(self) -> None:
        """Test AuthenticationError with empty message."""
        error = AuthenticationError("")

        assert str(error) == ""
        assert error.exit_code == 3

    def test_authentication_error_inheritance(self) -> None:
        """Test AuthenticationError inheritance."""
        error = AuthenticationError()

        assert isinstance(error, CLIError)
        assert isinstance(error, Exception)

    def test_authentication_error_raise(self) -> None:
        """Test raising AuthenticationError."""
        with pytest.raises(AuthenticationError) as exc_info:
            raise AuthenticationError("Token expired")

        assert str(exc_info.value) == "Token expired"
        assert exc_info.value.exit_code == 3


class TestNetworkError:
    """Test NetworkError exception functionality."""

    def test_network_error_default_message(self) -> None:
        """Test NetworkError with default message."""
        error = NetworkError()

        assert str(error) == "Network operation failed"
        assert error.exit_code == 4
        assert isinstance(error, CLIError)

    def test_network_error_custom_message(self) -> None:
        """Test NetworkError with custom message."""
        error = NetworkError("Connection timeout")

        assert str(error) == "Connection timeout"
        assert error.exit_code == 4

    def test_network_error_empty_message(self) -> None:
        """Test NetworkError with empty message."""
        error = NetworkError("")

        assert str(error) == ""
        assert error.exit_code == 4

    def test_network_error_inheritance(self) -> None:
        """Test NetworkError inheritance."""
        error = NetworkError()

        assert isinstance(error, CLIError)
        assert isinstance(error, Exception)

    def test_network_error_raise(self) -> None:
        """Test raising NetworkError."""
        with pytest.raises(NetworkError) as exc_info:
            raise NetworkError("DNS resolution failed")

        assert str(exc_info.value) == "DNS resolution failed"
        assert exc_info.value.exit_code == 4


class TestExceptionIntegration:
    """Integration tests for all exception classes."""

    def test_all_exceptions_inherit_from_cli_error(self) -> None:
        """Test that all custom exceptions inherit from CLIError."""
        exceptions = [
            CommandNotFoundError("test"),
            InvalidInputError("test"),
            ExecutionError("test"),
            AuthenticationError("test"),
            NetworkError("test"),
        ]

        for exception in exceptions:
            assert isinstance(exception, CLIError)
            assert isinstance(exception, Exception)
            assert hasattr(exception, "exit_code")

    def test_all_exceptions_have_unique_exit_codes(self) -> None:
        """Test that different exception types have different exit codes."""
        exceptions = {
            CLIError("test"): 1,
            CommandNotFoundError("test"): 2,
            InvalidInputError("test"): 1,
            ExecutionError("test"): 1,
            AuthenticationError("test"): 3,
            NetworkError("test"): 4,
        }

        for exception, expected_exit_code in exceptions.items():
            assert exception.exit_code == expected_exit_code

    def test_exception_messages_are_preserved(self) -> None:
        """Test that exception messages are properly preserved."""
        test_message = "Test error message"
        exceptions = [
            CLIError(test_message),
            CommandNotFoundError("test"),  # This has a formatted message
            InvalidInputError(test_message),
            ExecutionError(test_message),
            AuthenticationError(test_message),
            NetworkError(test_message),
        ]

        # Check that messages contain expected content
        assert str(exceptions[0]) == test_message
        assert "test" in str(exceptions[1])
        assert str(exceptions[2]) == test_message
        assert str(exceptions[3]) == test_message
        assert str(exceptions[4]) == test_message
        assert str(exceptions[5]) == test_message

    def test_exception_chaining_works(self) -> None:
        """Test that exception chaining works properly with ExecutionError."""
        original_error = ValueError("Original problem")
        execution_error = ExecutionError("Wrapper error", original_error)

        assert execution_error.original_error is original_error
        assert "Wrapper error" in str(execution_error)
        assert "Original problem" in str(execution_error)

    def test_raising_and_catching_all_exceptions(self) -> None:
        """Test raising and catching all exception types."""
        exception_types = [
            (CLIError, "CLI error"),
            (CommandNotFoundError, "missing"),
            (InvalidInputError, "invalid"),
            (ExecutionError, "execution failed"),
            (AuthenticationError, "auth failed"),
            (NetworkError, "network failed"),
        ]

        for exception_class, message in exception_types:
            with pytest.raises(exception_class):
                raise exception_class(message)
