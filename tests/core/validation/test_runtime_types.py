"""Tests for runtime type validation utilities."""

from typing import Any
from unittest.mock import patch

import pytest

from goldentooth_agent.core.validation.runtime_types import (
    validate_dict_response,
    validate_return_type,
)


class TestValidateReturnType:
    """Test the validate_return_type decorator."""

    def test_sync_function_valid_return_type(self):
        """Test sync function with correct return type."""

        @validate_return_type
        def get_string() -> str:
            return "hello"

        result = get_string()
        assert result == "hello"

    def test_sync_function_invalid_return_type(self):
        """Test sync function with incorrect return type."""

        @validate_return_type
        def get_string() -> str:
            return 123  # Wrong type

        with pytest.raises(
            TypeError, match="get_string returned int, expected <class 'str'>"
        ):
            get_string()

    @pytest.mark.asyncio
    async def test_async_function_valid_return_type(self):
        """Test async function with correct return type."""

        @validate_return_type
        async def get_string() -> str:
            return "hello"

        result = await get_string()
        assert result == "hello"

    @pytest.mark.asyncio
    async def test_async_function_invalid_return_type(self):
        """Test async function with incorrect return type."""

        @validate_return_type
        async def get_string() -> str:
            return 123  # Wrong type

        with pytest.raises(
            TypeError, match="get_string returned int, expected <class 'str'>"
        ):
            await get_string()

    def test_function_with_any_return_type(self):
        """Test function with Any return type (should skip validation)."""

        @validate_return_type
        def get_anything() -> Any:
            return 123

        result = get_anything()
        assert result == 123

    def test_function_without_return_annotation(self):
        """Test function without return annotation (should skip validation)."""

        @validate_return_type
        def no_annotation():
            return "hello"

        result = no_annotation()
        assert result == "hello"

    def test_function_with_get_type_hints_exception(self):
        """Test function where get_type_hints raises exception."""

        @validate_return_type
        def problematic_function() -> str:
            return "hello"

        # Mock get_type_hints to raise exception
        with patch(
            "goldentooth_agent.core.validation.runtime_types.get_type_hints"
        ) as mock_hints:
            mock_hints.side_effect = NameError("Undefined type")

            # Should not raise and return the value
            result = problematic_function()
            assert result == "hello"

    @pytest.mark.asyncio
    async def test_async_function_with_get_type_hints_exception(self):
        """Test async function where get_type_hints raises exception."""

        @validate_return_type
        async def problematic_async_function() -> str:
            return "hello"

        # Mock get_type_hints to raise exception
        with patch(
            "goldentooth_agent.core.validation.runtime_types.get_type_hints"
        ) as mock_hints:
            mock_hints.side_effect = NameError("Undefined type")

            # Should not raise and return the value
            result = await problematic_async_function()
            assert result == "hello"

    def test_complex_return_type_validation(self):
        """Test with complex return types like list."""

        @validate_return_type
        def get_list() -> list:
            return ["a", "b", "c"]

        result = get_list()
        assert result == ["a", "b", "c"]

    def test_complex_return_type_validation_failure(self):
        """Test with complex return types that fail validation."""

        @validate_return_type
        def get_list() -> list:
            return {"a": 1}  # Wrong type

        with pytest.raises(TypeError, match="get_list returned dict, expected"):
            get_list()


class TestValidateDictResponse:
    """Test the validate_dict_response function."""

    def test_valid_dict_no_keys_specified(self):
        """Test valid dict with no key requirements."""
        response = {"key1": "value1", "key2": "value2"}
        result = validate_dict_response(response)
        assert result == response

    def test_valid_dict_with_required_keys(self):
        """Test valid dict with all required keys present."""
        response = {"required1": "value1", "required2": "value2", "extra": "value3"}
        result = validate_dict_response(
            response, required_keys=["required1", "required2"]
        )
        assert result == response

    def test_valid_dict_with_optional_keys(self):
        """Test valid dict with optional keys."""
        response = {"required": "value", "optional": "value2"}
        result = validate_dict_response(
            response,
            required_keys=["required"],
            optional_keys=["optional", "other_optional"],
        )
        assert result == response

    def test_non_dict_response_raises_type_error(self):
        """Test that non-dict response raises TypeError."""
        with pytest.raises(TypeError, match="Expected dict response, got str"):
            validate_dict_response("not a dict")

        with pytest.raises(TypeError, match="Expected dict response, got list"):
            validate_dict_response(["a", "b", "c"])

        with pytest.raises(TypeError, match="Expected dict response, got NoneType"):
            validate_dict_response(None)

    def test_missing_required_keys_raises_key_error(self):
        """Test that missing required keys raises KeyError."""
        response = {"key1": "value1"}

        with pytest.raises(
            KeyError, match="Response missing required keys: \\['key2', 'key3'\\]"
        ):
            validate_dict_response(response, required_keys=["key1", "key2", "key3"])

    def test_partial_missing_required_keys(self):
        """Test with some required keys missing."""
        response = {"key1": "value1", "key3": "value3"}

        with pytest.raises(
            KeyError, match="Response missing required keys: \\['key2'\\]"
        ):
            validate_dict_response(response, required_keys=["key1", "key2", "key3"])

    def test_unexpected_keys_logged_as_warning(self, caplog):
        """Test that unexpected keys are logged as warnings."""
        response = {"required": "value", "unexpected": "value2"}

        with caplog.at_level("WARNING"):
            result = validate_dict_response(response, required_keys=["required"])

        assert result == response
        assert "Response contains unexpected keys: {'unexpected'}" in caplog.text

    def test_unexpected_keys_with_optional_keys(self, caplog):
        """Test unexpected keys when optional keys are specified."""
        response = {
            "required": "value",
            "optional": "value2",
            "unexpected1": "value3",
            "unexpected2": "value4",
        }

        with caplog.at_level("WARNING"):
            result = validate_dict_response(
                response, required_keys=["required"], optional_keys=["optional"]
            )

        assert result == response
        assert "unexpected1" in caplog.text
        assert "unexpected2" in caplog.text

    def test_no_warning_when_all_keys_expected(self, caplog):
        """Test no warning when all keys are in required or optional."""
        response = {"required": "value", "optional": "value2"}

        with caplog.at_level("WARNING"):
            result = validate_dict_response(
                response, required_keys=["required"], optional_keys=["optional"]
            )

        assert result == response
        assert "unexpected" not in caplog.text

    def test_empty_dict_with_no_required_keys(self):
        """Test empty dict when no keys are required."""
        result = validate_dict_response({})
        assert result == {}

    def test_empty_dict_with_required_keys_fails(self):
        """Test empty dict when keys are required."""
        with pytest.raises(
            KeyError, match="Response missing required keys: \\['required'\\]"
        ):
            validate_dict_response({}, required_keys=["required"])

    def test_none_values_in_required_keys_are_valid(self):
        """Test that None values in required keys are still valid."""
        response = {"required": None, "other": "value"}
        result = validate_dict_response(response, required_keys=["required"])
        assert result == response

    def test_edge_case_empty_key_names(self):
        """Test edge case with empty string as key name."""
        response = {"": "value", "normal_key": "value2"}
        result = validate_dict_response(response, required_keys=["", "normal_key"])
        assert result == response

    def test_large_response_dict(self):
        """Test with large response dictionary."""
        response = {f"key_{i}": f"value_{i}" for i in range(1000)}
        required_keys = [f"key_{i}" for i in range(0, 100, 10)]  # Every 10th key

        result = validate_dict_response(response, required_keys=required_keys)
        assert result == response
        assert len(result) == 1000
