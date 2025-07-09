"""Tests for context_flow.integration module."""

import pytest

from context_flow.integration import ContextFlowError, MissingRequiredKeyError


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


class TestMissingRequiredKeyError:
    """Test cases for MissingRequiredKeyError exception class."""

    def test_missing_required_key_error_inherits_from_context_flow_error(self) -> None:
        """Test that MissingRequiredKeyError inherits from ContextFlowError."""
        assert issubclass(MissingRequiredKeyError, ContextFlowError)

    def test_missing_required_key_error_inherits_from_exception(self) -> None:
        """Test that MissingRequiredKeyError inherits from Exception."""
        assert issubclass(MissingRequiredKeyError, Exception)

    def test_missing_required_key_error_instantiation(self) -> None:
        """Test that MissingRequiredKeyError can be instantiated."""
        error = MissingRequiredKeyError()
        assert isinstance(error, MissingRequiredKeyError)
        assert isinstance(error, ContextFlowError)
        assert isinstance(error, Exception)

    def test_missing_required_key_error_with_message(self) -> None:
        """Test that MissingRequiredKeyError can be instantiated with a message."""
        message = "Key 'user_id' is required but missing from context"
        error = MissingRequiredKeyError(message)
        assert str(error) == message

    def test_missing_required_key_error_can_be_raised(self) -> None:
        """Test that MissingRequiredKeyError can be raised and caught."""
        with pytest.raises(MissingRequiredKeyError) as exc_info:
            raise MissingRequiredKeyError("Missing key error")

        assert str(exc_info.value) == "Missing key error"

    def test_missing_required_key_error_can_be_caught_as_context_flow_error(
        self,
    ) -> None:
        """Test that MissingRequiredKeyError can be caught as ContextFlowError."""
        with pytest.raises(ContextFlowError) as exc_info:
            raise MissingRequiredKeyError("Missing key error")

        assert isinstance(exc_info.value, MissingRequiredKeyError)

    def test_missing_required_key_error_can_be_caught_as_exception(self) -> None:
        """Test that MissingRequiredKeyError can be caught as base Exception."""
        with pytest.raises(Exception) as exc_info:
            raise MissingRequiredKeyError("Missing key error")

        assert isinstance(exc_info.value, MissingRequiredKeyError)
        assert isinstance(exc_info.value, ContextFlowError)

    def test_missing_required_key_error_empty_instantiation(self) -> None:
        """Test that MissingRequiredKeyError can be instantiated without arguments."""
        error = MissingRequiredKeyError()
        assert str(error) == ""

    def test_missing_required_key_error_multiple_args(self) -> None:
        """Test that MissingRequiredKeyError can be instantiated with multiple arguments."""
        error = MissingRequiredKeyError(
            "Key missing", "Additional info", "More details"
        )
        assert error.args == ("Key missing", "Additional info", "More details")

    def test_missing_required_key_error_with_exception_chaining(self) -> None:
        """Test that MissingRequiredKeyError works with exception chaining."""
        original_error = KeyError("key_name")

        try:
            raise original_error
        except KeyError as e:
            with pytest.raises(MissingRequiredKeyError) as exc_info:
                raise MissingRequiredKeyError("Required key missing") from e

        assert exc_info.value.__cause__ == original_error
        assert str(exc_info.value) == "Required key missing"
