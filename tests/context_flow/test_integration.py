"""Tests for context_flow.integration module."""

import pytest

from context_flow.integration import ContextFlowError


class TestContextFlowError:
    """Test cases for ContextFlowError exception class."""

    def test_context_flow_error_is_exception(self) -> None:
        """Test that ContextFlowError inherits from Exception."""
        assert issubclass(ContextFlowError, Exception)

    def test_context_flow_error_instantiation(self) -> None:
        """Test that ContextFlowError can be instantiated."""
        error = ContextFlowError()
        assert isinstance(error, ContextFlowError)
        assert isinstance(error, Exception)

    def test_context_flow_error_with_message(self) -> None:
        """Test that ContextFlowError can be instantiated with a message."""
        message = "Test error message"
        error = ContextFlowError(message)
        assert str(error) == message

    def test_context_flow_error_can_be_raised(self) -> None:
        """Test that ContextFlowError can be raised and caught."""
        with pytest.raises(ContextFlowError) as exc_info:
            raise ContextFlowError("Test error")

        assert str(exc_info.value) == "Test error"

    def test_context_flow_error_can_be_caught_as_exception(self) -> None:
        """Test that ContextFlowError can be caught as base Exception."""
        with pytest.raises(Exception) as exc_info:
            raise ContextFlowError("Test error")

        assert isinstance(exc_info.value, ContextFlowError)

    def test_context_flow_error_empty_instantiation(self) -> None:
        """Test that ContextFlowError can be instantiated without arguments."""
        error = ContextFlowError()
        assert str(error) == ""

    def test_context_flow_error_multiple_args(self) -> None:
        """Test that ContextFlowError can be instantiated with multiple arguments."""
        error = ContextFlowError("First", "Second", "Third")
        assert error.args == ("First", "Second", "Third")
