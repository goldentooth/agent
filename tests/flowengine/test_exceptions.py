"""Tests for flowengine.exceptions module."""

import pytest

from flowengine.exceptions import (
    FlowConfigurationError,
    FlowError,
    FlowExecutionError,
    FlowTimeoutError,
    FlowValidationError,
)


class TestFlowError:
    """Test the base FlowError exception."""

    def test_flow_error_is_exception(self) -> None:
        """FlowError should inherit from Exception."""
        assert issubclass(FlowError, Exception)

    def test_flow_error_can_be_raised(self) -> None:
        """FlowError can be raised with a message."""
        with pytest.raises(FlowError, match="test error"):
            raise FlowError("test error")

    def test_flow_error_can_be_raised_without_message(self) -> None:
        """FlowError can be raised without a message."""
        with pytest.raises(FlowError):
            raise FlowError()

    def test_flow_error_preserves_message(self) -> None:
        """FlowError preserves the error message."""
        message = "test error message"
        error = FlowError(message)
        assert str(error) == message


class TestFlowValidationError:
    """Test the FlowValidationError exception."""

    def test_inherits_from_flow_error(self) -> None:
        """FlowValidationError should inherit from FlowError."""
        assert issubclass(FlowValidationError, FlowError)

    def test_can_be_raised_with_message(self) -> None:
        """FlowValidationError can be raised with a message."""
        with pytest.raises(FlowValidationError, match="validation failed"):
            raise FlowValidationError("validation failed")

    def test_can_be_caught_as_flow_error(self) -> None:
        """FlowValidationError can be caught as FlowError."""
        with pytest.raises(FlowError):
            raise FlowValidationError("validation error")

    def test_preserves_message(self) -> None:
        """FlowValidationError preserves the error message."""
        message = "guard condition failed"
        error = FlowValidationError(message)
        assert str(error) == message


class TestFlowExecutionError:
    """Test the FlowExecutionError exception."""

    def test_inherits_from_flow_error(self) -> None:
        """FlowExecutionError should inherit from FlowError."""
        assert issubclass(FlowExecutionError, FlowError)

    def test_can_be_raised_with_message(self) -> None:
        """FlowExecutionError can be raised with a message."""
        with pytest.raises(FlowExecutionError, match="execution failed"):
            raise FlowExecutionError("execution failed")

    def test_can_be_caught_as_flow_error(self) -> None:
        """FlowExecutionError can be caught as FlowError."""
        with pytest.raises(FlowError):
            raise FlowExecutionError("execution error")

    def test_preserves_message(self) -> None:
        """FlowExecutionError preserves the error message."""
        message = "all retries exhausted"
        error = FlowExecutionError(message)
        assert str(error) == message


class TestFlowTimeoutError:
    """Test the FlowTimeoutError exception."""

    def test_inherits_from_flow_error(self) -> None:
        """FlowTimeoutError should inherit from FlowError."""
        assert issubclass(FlowTimeoutError, FlowError)

    def test_can_be_raised_with_message(self) -> None:
        """FlowTimeoutError can be raised with a message."""
        with pytest.raises(FlowTimeoutError, match="operation timed out"):
            raise FlowTimeoutError("operation timed out")

    def test_can_be_caught_as_flow_error(self) -> None:
        """FlowTimeoutError can be caught as FlowError."""
        with pytest.raises(FlowError):
            raise FlowTimeoutError("timeout error")

    def test_preserves_message(self) -> None:
        """FlowTimeoutError preserves the error message."""
        message = "operation timed out after 30 seconds"
        error = FlowTimeoutError(message)
        assert str(error) == message


class TestFlowConfigurationError:
    """Test the FlowConfigurationError exception."""

    def test_inherits_from_flow_error(self) -> None:
        """FlowConfigurationError should inherit from FlowError."""
        assert issubclass(FlowConfigurationError, FlowError)

    def test_can_be_raised_with_message(self) -> None:
        """FlowConfigurationError can be raised with a message."""
        with pytest.raises(FlowConfigurationError, match="invalid configuration"):
            raise FlowConfigurationError("invalid configuration")

    def test_can_be_caught_as_flow_error(self) -> None:
        """FlowConfigurationError can be caught as FlowError."""
        with pytest.raises(FlowError):
            raise FlowConfigurationError("config error")

    def test_preserves_message(self) -> None:
        """FlowConfigurationError preserves the error message."""
        message = "invalid parameter: timeout must be positive"
        error = FlowConfigurationError(message)
        assert str(error) == message


class TestExceptionHierarchy:
    """Test the exception hierarchy relationships."""

    def test_all_flow_exceptions_inherit_from_flow_error(self) -> None:
        """All flow exceptions should inherit from FlowError."""
        flow_exceptions = [
            FlowValidationError,
            FlowExecutionError,
            FlowTimeoutError,
            FlowConfigurationError,
        ]

        for exception_class in flow_exceptions:
            assert issubclass(exception_class, FlowError)

    def test_flow_error_inherits_from_exception(self) -> None:
        """FlowError should inherit from built-in Exception."""
        assert issubclass(FlowError, Exception)

    def test_can_catch_specific_exceptions(self) -> None:
        """Specific flow exceptions can be caught individually."""
        with pytest.raises(FlowValidationError):
            raise FlowValidationError("validation error")

        with pytest.raises(FlowExecutionError):
            raise FlowExecutionError("execution error")

        with pytest.raises(FlowTimeoutError):
            raise FlowTimeoutError("timeout error")

        with pytest.raises(FlowConfigurationError):
            raise FlowConfigurationError("config error")

    def test_can_catch_all_flow_exceptions_with_base_class(self) -> None:
        """All flow exceptions can be caught using FlowError."""
        exceptions_to_test = [
            FlowValidationError("validation error"),
            FlowExecutionError("execution error"),
            FlowTimeoutError("timeout error"),
            FlowConfigurationError("config error"),
        ]

        for exception in exceptions_to_test:
            with pytest.raises(FlowError):
                raise exception


class TestExceptionChaining:
    """Test exception chaining and context preservation."""

    def test_flow_error_supports_exception_chaining(self) -> None:
        """FlowError supports exception chaining with 'from' clause."""
        original_error = ValueError("original error")

        with pytest.raises(FlowError) as exc_info:
            try:
                raise original_error
            except ValueError as e:
                raise FlowError("wrapped error") from e

        assert exc_info.value.__cause__ is original_error

    def test_specialized_exceptions_support_chaining(self) -> None:
        """Specialized flow exceptions support exception chaining."""
        original_error = ConnectionError("network error")

        with pytest.raises(FlowExecutionError) as exc_info:
            try:
                raise original_error
            except ConnectionError as e:
                raise FlowExecutionError("execution failed due to network") from e

        assert exc_info.value.__cause__ is original_error
