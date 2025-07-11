"""CLI-specific exceptions and error handling."""

from typing import Optional


class CLIError(Exception):
    """Base exception for CLI-related errors."""

    def __init__(
        self,
        message: str,
        exit_code: int = 1,
        show_traceback: bool = False,
    ) -> None:
        super().__init__(message)
        self.exit_code = exit_code
        self.show_traceback = show_traceback


class CommandNotFoundError(CLIError):
    """Raised when a requested command is not found."""

    def __init__(self, command_name: str) -> None:
        super().__init__(
            f"Command '{command_name}' not found",
            exit_code=2,
        )


class InvalidInputError(CLIError):
    """Raised when command input is invalid."""

    def __init__(self, message: str, suggestion: Optional[str] = None) -> None:
        full_message = message
        if suggestion:
            full_message += f"\n\nSuggestion: {suggestion}"

        super().__init__(full_message, exit_code=1)


class ExecutionError(CLIError):
    """Raised when command execution fails."""

    def __init__(
        self,
        message: str,
        original_error: Optional[Exception] = None,
        show_traceback: bool = False,
    ) -> None:
        if original_error:
            full_message = f"{message}\nCaused by: {str(original_error)}"
        else:
            full_message = message

        super().__init__(
            full_message,
            exit_code=1,
            show_traceback=show_traceback,
        )
        self.original_error = original_error


class AuthenticationError(CLIError):
    """Raised when authentication fails."""

    def __init__(self, message: str = "Authentication failed") -> None:
        super().__init__(message, exit_code=3)


class NetworkError(CLIError):
    """Raised when network operations fail."""

    def __init__(self, message: str = "Network operation failed") -> None:
        super().__init__(message, exit_code=4)
