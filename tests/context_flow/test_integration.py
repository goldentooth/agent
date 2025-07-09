"""Tests for context_flow.integration module."""

import pytest

from context_flow.integration import (
    ContextFlowError,
    ContextTypeMismatchError,
    MissingRequiredKeyError,
    _single_item_stream,
)


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


class TestContextTypeMismatchError:
    """Test cases for ContextTypeMismatchError exception class."""

    def test_context_type_mismatch_error_inherits_from_context_flow_error(self) -> None:
        """Test that ContextTypeMismatchError inherits from ContextFlowError."""
        assert issubclass(ContextTypeMismatchError, ContextFlowError)

    def test_context_type_mismatch_error_inherits_from_exception(self) -> None:
        """Test that ContextTypeMismatchError inherits from Exception."""
        assert issubclass(ContextTypeMismatchError, Exception)

    def test_context_type_mismatch_error_instantiation(self) -> None:
        """Test that ContextTypeMismatchError can be instantiated."""
        error = ContextTypeMismatchError()
        assert isinstance(error, ContextTypeMismatchError)
        assert isinstance(error, ContextFlowError)
        assert isinstance(error, Exception)

    def test_context_type_mismatch_error_with_message(self) -> None:
        """Test that ContextTypeMismatchError can be instantiated with a message."""
        message = "Key 'user_id' expected str, got int"
        error = ContextTypeMismatchError(message)
        assert str(error) == message

    def test_context_type_mismatch_error_with_formatted_message(self) -> None:
        """Test that ContextTypeMismatchError works with formatted type messages."""
        key_path = "user.profile.age"
        expected_type = "int"
        actual_type = "str"
        message = f"Key '{key_path}' expected {expected_type}, got {actual_type}"
        error = ContextTypeMismatchError(message)
        assert str(error) == message

    def test_context_type_mismatch_error_can_be_raised(self) -> None:
        """Test that ContextTypeMismatchError can be raised and caught."""
        with pytest.raises(ContextTypeMismatchError) as exc_info:
            raise ContextTypeMismatchError("Type mismatch error")

        assert str(exc_info.value) == "Type mismatch error"

    def test_context_type_mismatch_error_can_be_caught_as_context_flow_error(
        self,
    ) -> None:
        """Test that ContextTypeMismatchError can be caught as ContextFlowError."""
        with pytest.raises(ContextFlowError) as exc_info:
            raise ContextTypeMismatchError("Type mismatch error")

        assert isinstance(exc_info.value, ContextTypeMismatchError)

    def test_context_type_mismatch_error_can_be_caught_as_exception(self) -> None:
        """Test that ContextTypeMismatchError can be caught as base Exception."""
        with pytest.raises(Exception) as exc_info:
            raise ContextTypeMismatchError("Type mismatch error")

        assert isinstance(exc_info.value, ContextTypeMismatchError)
        assert isinstance(exc_info.value, ContextFlowError)

    def test_context_type_mismatch_error_empty_instantiation(self) -> None:
        """Test that ContextTypeMismatchError can be instantiated without arguments."""
        error = ContextTypeMismatchError()
        assert str(error) == ""

    def test_context_type_mismatch_error_multiple_args(self) -> None:
        """Test that ContextTypeMismatchError can be instantiated with multiple arguments."""
        error = ContextTypeMismatchError("Type mismatch", "Expected int", "Got str")
        assert error.args == ("Type mismatch", "Expected int", "Got str")

    def test_context_type_mismatch_error_with_exception_chaining(self) -> None:
        """Test that ContextTypeMismatchError works with exception chaining."""
        original_error = TypeError("Invalid type conversion")

        try:
            raise original_error
        except TypeError as e:
            with pytest.raises(ContextTypeMismatchError) as exc_info:
                raise ContextTypeMismatchError("Context type mismatch") from e

        assert exc_info.value.__cause__ == original_error
        assert str(exc_info.value) == "Context type mismatch"

    def test_context_type_mismatch_error_with_type_names(self) -> None:
        """Test that ContextTypeMismatchError works with actual type names."""
        expected_type = int
        actual_type = str
        message = f"Expected {expected_type.__name__}, got {actual_type.__name__}"

        error = ContextTypeMismatchError(message)
        assert str(error) == "Expected int, got str"


class TestSingleItemStream:
    """Test cases for _single_item_stream function."""

    @pytest.mark.asyncio
    async def test_single_item_stream_basic_functionality(self) -> None:
        """Test that _single_item_stream yields exactly one item."""
        item = "test_item"

        stream = _single_item_stream(item)

        # Collect all items from the stream
        items = []
        async for result in stream:
            items.append(result)

        assert len(items) == 1
        assert items[0] == "test_item"

    @pytest.mark.asyncio
    async def test_single_item_stream_with_string(self) -> None:
        """Test _single_item_stream with string input."""
        item = "hello world"

        stream = _single_item_stream(item)

        async for result in stream:
            assert result == "hello world"
            assert isinstance(result, str)
            break

    @pytest.mark.asyncio
    async def test_single_item_stream_with_integer(self) -> None:
        """Test _single_item_stream with integer input."""
        item = 42

        stream = _single_item_stream(item)

        async for result in stream:
            assert result == 42
            assert isinstance(result, int)
            break

    @pytest.mark.asyncio
    async def test_single_item_stream_with_none(self) -> None:
        """Test _single_item_stream with None input."""
        item = None

        stream = _single_item_stream(item)

        async for result in stream:
            assert result is None
            break

    @pytest.mark.asyncio
    async def test_single_item_stream_with_list(self) -> None:
        """Test _single_item_stream with list input."""
        item = [1, 2, 3, "test"]

        stream = _single_item_stream(item)

        async for result in stream:
            assert result == [1, 2, 3, "test"]
            assert isinstance(result, list)
            break

    @pytest.mark.asyncio
    async def test_single_item_stream_with_dict(self) -> None:
        """Test _single_item_stream with dictionary input."""
        item = {"key": "value", "number": 42}

        stream = _single_item_stream(item)

        async for result in stream:
            assert result == {"key": "value", "number": 42}
            assert isinstance(result, dict)
            break

    @pytest.mark.asyncio
    async def test_single_item_stream_with_custom_object(self) -> None:
        """Test _single_item_stream with custom object input."""

        class CustomObject:
            def __init__(self, value: str):
                super().__init__()
                self.value = value

            def __eq__(self, other: object) -> bool:
                return isinstance(other, CustomObject) and self.value == other.value

        item = CustomObject("test_value")

        stream = _single_item_stream(item)

        async for result in stream:
            assert result == item
            assert isinstance(result, CustomObject)
            assert result.value == "test_value"
            break

    @pytest.mark.asyncio
    async def test_single_item_stream_exhaustible(self) -> None:
        """Test that _single_item_stream is properly exhaustible."""
        item = "test"

        stream = _single_item_stream(item)

        # First iteration should yield the item
        first_result = await stream.__anext__()
        assert first_result == "test"

        # Second iteration should raise StopAsyncIteration
        with pytest.raises(StopAsyncIteration):
            await stream.__anext__()

    @pytest.mark.asyncio
    async def test_single_item_stream_multiple_iterations(self) -> None:
        """Test that _single_item_stream can be iterated multiple times."""
        item = "test"

        # First iteration
        stream1 = _single_item_stream(item)
        async for result in stream1:
            assert result == "test"
            break

        # Second iteration with new stream
        stream2 = _single_item_stream(item)
        async for result in stream2:
            assert result == "test"
            break

    @pytest.mark.asyncio
    async def test_single_item_stream_type_preservation(self) -> None:
        """Test that _single_item_stream preserves the type of the input."""
        # Test with different types
        test_cases = [
            ("string", str),
            (123, int),
            (45.67, float),
            (True, bool),
            ([1, 2, 3], list),
            ({"key": "value"}, dict),
            ((1, 2, 3), tuple),
        ]

        for item, expected_type in test_cases:
            stream = _single_item_stream(item)
            async for result in stream:
                assert isinstance(result, expected_type)
                assert result == item
                break

    @pytest.mark.asyncio
    async def test_single_item_stream_with_empty_string(self) -> None:
        """Test _single_item_stream with empty string."""
        item = ""

        stream = _single_item_stream(item)

        async for result in stream:
            assert result == ""
            assert isinstance(result, str)
            break

    @pytest.mark.asyncio
    async def test_single_item_stream_with_zero(self) -> None:
        """Test _single_item_stream with zero value."""
        item = 0

        stream = _single_item_stream(item)

        async for result in stream:
            assert result == 0
            assert isinstance(result, int)
            break

    @pytest.mark.asyncio
    async def test_single_item_stream_with_false(self) -> None:
        """Test _single_item_stream with False boolean."""
        item = False

        stream = _single_item_stream(item)

        async for result in stream:
            assert result is False
            assert isinstance(result, bool)
            break

    @pytest.mark.asyncio
    async def test_single_item_stream_with_empty_list(self) -> None:
        """Test _single_item_stream with empty list."""
        item: list[int] = []

        stream = _single_item_stream(item)

        async for result in stream:
            assert result == []
            assert isinstance(result, list)
            break

    @pytest.mark.asyncio
    async def test_single_item_stream_reference_preservation(self) -> None:
        """Test that _single_item_stream preserves object references."""
        item = {"mutable": "object"}

        stream = _single_item_stream(item)

        async for result in stream:
            assert result is item  # Same object reference
            assert result == item  # Same content
            break
