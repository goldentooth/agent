"""Tests for Context._apply_transformations private method."""

from typing import Any

from context.main import Context


class TestContextApplyTransformations:
    """Test suite for Context._apply_transformations private method."""

    def test_apply_transformations_no_transformations(self) -> None:
        """Test applying transformations when none exist for key."""
        context = Context()

        # Should return original value when no transformations exist
        result = context._apply_transformations("test_key", "original_value")

        assert result == "original_value"

    def test_apply_transformations_single_transformation(self) -> None:
        """Test applying a single transformation."""
        context = Context()

        # Add a transformation that uppercases strings
        def uppercase_transform(value: str) -> str:
            return value.upper()

        context.add_transformation("test_key", uppercase_transform)

        # Apply transformations
        result = context._apply_transformations("test_key", "hello")

        assert result == "HELLO"

    def test_apply_transformations_multiple_transformations(self) -> None:
        """Test applying multiple transformations in sequence."""
        context = Context()

        # Add multiple transformations
        def uppercase_transform(value: str) -> str:
            return value.upper()

        def add_prefix_transform(value: str) -> str:
            return f"PREFIX_{value}"

        def add_suffix_transform(value: str) -> str:
            return f"{value}_SUFFIX"

        context.add_transformation("test_key", uppercase_transform)
        context.add_transformation("test_key", add_prefix_transform)
        context.add_transformation("test_key", add_suffix_transform)

        # Apply transformations (should be applied in order)
        result = context._apply_transformations("test_key", "hello")

        assert result == "PREFIX_HELLO_SUFFIX"

    def test_apply_transformations_with_numeric_values(self) -> None:
        """Test applying transformations to numeric values."""
        context = Context()

        # Add transformations for numeric operations
        def double_transform(value: int) -> int:
            return value * 2

        def add_ten_transform(value: int) -> int:
            return value + 10

        context.add_transformation("numeric_key", double_transform)
        context.add_transformation("numeric_key", add_ten_transform)

        # Apply transformations
        result = context._apply_transformations("numeric_key", 5)

        assert result == 20  # (5 * 2) + 10

    def test_apply_transformations_exception_handling(self) -> None:
        """Test that exceptions in transformations are handled gracefully."""
        context = Context()

        # Add a transformation that will raise an exception
        def failing_transform(value: str) -> str:
            raise ValueError("Transformation failed")

        def working_transform(value: str) -> str:
            return value.upper()

        context.add_transformation("test_key", failing_transform)
        context.add_transformation("test_key", working_transform)

        # Should continue with remaining transformations after failure
        result = context._apply_transformations("test_key", "hello")

        # Should continue with next transformation after one fails
        assert result == "HELLO"

    def test_apply_transformations_all_fail(self) -> None:
        """Test that original value is returned when all transformations fail."""
        context = Context()

        # Add transformations that will all raise exceptions
        def failing_transform1(value: str) -> str:
            raise ValueError("First transformation failed")

        def failing_transform2(value: str) -> str:
            raise RuntimeError("Second transformation failed")

        context.add_transformation("test_key", failing_transform1)
        context.add_transformation("test_key", failing_transform2)

        # Should return original value when all transformations fail
        result = context._apply_transformations("test_key", "original")

        assert result == "original"

    def test_apply_transformations_with_complex_data(self) -> None:
        """Test applying transformations to complex data structures."""
        context = Context()

        # Add transformation for dictionaries
        def add_timestamp_transform(value: dict[str, Any]) -> dict[str, Any]:
            import time

            new_value = value.copy()
            new_value["timestamp"] = time.time()
            return new_value

        def add_version_transform(value: dict[str, Any]) -> dict[str, Any]:
            new_value = value.copy()
            new_value["version"] = "1.0"
            return new_value

        context.add_transformation("data_key", add_timestamp_transform)
        context.add_transformation("data_key", add_version_transform)

        original_data = {"name": "test", "value": 42}
        result = context._apply_transformations("data_key", original_data)

        assert result["name"] == "test"
        assert result["value"] == 42
        assert "timestamp" in result
        assert result["version"] == "1.0"

    def test_apply_transformations_key_specific(self) -> None:
        """Test that transformations are key-specific."""
        context = Context()

        # Add different transformations for different keys
        def uppercase_transform(value: str) -> str:
            return value.upper()

        def lowercase_transform(value: str) -> str:
            return value.lower()

        context.add_transformation("key1", uppercase_transform)
        context.add_transformation("key2", lowercase_transform)

        # Apply transformations to different keys
        result1 = context._apply_transformations("key1", "Hello")
        result2 = context._apply_transformations("key2", "WORLD")
        result3 = context._apply_transformations("key3", "Unchanged")

        assert result1 == "HELLO"
        assert result2 == "world"
        assert result3 == "Unchanged"

    def test_apply_transformations_method_signature(self) -> None:
        """Test that _apply_transformations method has correct signature."""
        context = Context()

        # Verify method exists and is callable
        assert hasattr(context, "_apply_transformations")
        assert callable(context._apply_transformations)

        # Test with required parameters
        result = context._apply_transformations("key", "value")
        assert result == "value"

    def test_apply_transformations_return_type_preservation(self) -> None:
        """Test that original type is preserved when no transformations apply."""
        context = Context()

        # Test various data types
        string_result = context._apply_transformations("key", "string")
        int_result = context._apply_transformations("key", 42)
        list_result = context._apply_transformations("key", [1, 2, 3])
        dict_result = context._apply_transformations("key", {"a": 1})
        bool_result = context._apply_transformations("key", True)
        none_result = context._apply_transformations("key", None)

        assert string_result == "string"
        assert int_result == 42
        assert list_result == [1, 2, 3]
        assert dict_result == {"a": 1}
        assert bool_result is True
        assert none_result is None

    def test_apply_transformations_with_none_values(self) -> None:
        """Test applying transformations to None values."""
        context = Context()

        # Add transformation that handles None
        def none_to_default_transform(value: Any) -> str:
            return "default" if value is None else value

        context.add_transformation("test_key", none_to_default_transform)

        result = context._apply_transformations("test_key", None)

        assert result == "default"

    def test_apply_transformations_chaining_effect(self) -> None:
        """Test that transformations properly chain their effects."""
        context = Context()

        # Add transformations that build on each other
        def to_list_transform(value: str) -> list[str]:
            return [value]

        def append_item_transform(value: list[str]) -> list[str]:
            return value + ["appended"]

        def count_items_transform(value: list[str]) -> int:
            return len(value)

        context.add_transformation("chain_key", to_list_transform)
        context.add_transformation("chain_key", append_item_transform)
        context.add_transformation("chain_key", count_items_transform)

        result = context._apply_transformations("chain_key", "initial")

        assert result == 2  # ["initial", "appended"] has length 2

    def test_apply_transformations_empty_key(self) -> None:
        """Test applying transformations with empty string key."""
        context = Context()

        def transform_func(value: str) -> str:
            return f"transformed_{value}"

        context.add_transformation("", transform_func)

        result = context._apply_transformations("", "test")

        assert result == "transformed_test"

    def test_apply_transformations_special_characters_in_key(self) -> None:
        """Test applying transformations with special characters in key."""
        context = Context()

        special_key = "key.with-special@chars[0]"

        def transform_func(value: str) -> str:
            return value.upper()

        context.add_transformation(special_key, transform_func)

        result = context._apply_transformations(special_key, "hello")

        assert result == "HELLO"

    def test_apply_transformations_no_side_effects(self) -> None:
        """Test that applying transformations has no side effects on context."""
        context = Context()

        # Set up initial state
        context.set("test_key", "original")
        original_value = context.get("test_key")

        # Add transformation
        def transform_func(value: str) -> str:
            return value.upper()

        context.add_transformation("test_key", transform_func)

        # Apply transformation directly
        result = context._apply_transformations("test_key", "direct_call")

        # Context state should be unchanged
        assert context.get("test_key") == original_value
        assert result == "DIRECT_CALL"

    def test_apply_transformations_order_matters(self) -> None:
        """Test that transformation order matters for the result."""
        context = Context()

        # Add transformations in specific order
        def multiply_by_two(value: int) -> int:
            return value * 2

        def add_five(value: int) -> int:
            return value + 5

        context.add_transformation("math_key", multiply_by_two)
        context.add_transformation("math_key", add_five)

        # (10 * 2) + 5 = 25
        result = context._apply_transformations("math_key", 10)
        assert result == 25
