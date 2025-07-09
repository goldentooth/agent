"""Tests for TransformationsManager class."""

from typing import Any

from context.computed import Transformation
from context.transformations_manager import TransformationsManager


class TestTransformationsManager:
    """Test suite for TransformationsManager class."""

    def test_init_creates_empty_manager(self) -> None:
        """Test that manager initializes with empty state."""
        manager = TransformationsManager()

        assert len(manager._transformations) == 0
        assert len(manager) == 0
        assert manager.get_keys() == []

    def test_add_transformation_basic(self) -> None:
        """Test adding a basic transformation."""
        manager = TransformationsManager()

        def transform_func(value: str) -> str:
            return value.upper()

        manager.add_transformation("test_key", transform_func)

        assert manager.has_transformations("test_key")
        assert "test_key" in manager.get_keys()
        assert len(manager.get_transformations("test_key")) == 1

    def test_add_multiple_transformations_same_key(self) -> None:
        """Test adding multiple transformations to same key."""
        manager = TransformationsManager()

        def transform_func1(value: str) -> str:
            return value.upper()

        def transform_func2(value: str) -> str:
            return f"prefix_{value}"

        manager.add_transformation("test_key", transform_func1)
        manager.add_transformation("test_key", transform_func2)

        transformations = manager.get_transformations("test_key")
        assert len(transformations) == 2
        assert all(isinstance(t, Transformation) for t in transformations)

    def test_add_transformations_different_keys(self) -> None:
        """Test adding transformations to different keys."""
        manager = TransformationsManager()

        def transform_func1(value: str) -> str:
            return value.upper()

        def transform_func2(value: str) -> str:
            return value.lower()

        manager.add_transformation("key1", transform_func1)
        manager.add_transformation("key2", transform_func2)

        assert manager.has_transformations("key1")
        assert manager.has_transformations("key2")
        assert len(manager.get_keys()) == 2

    def test_remove_transformations_existing_key(self) -> None:
        """Test removing transformations for existing key."""
        manager = TransformationsManager()

        def transform_func(value: str) -> str:
            return value.upper()

        manager.add_transformation("test_key", transform_func)
        assert manager.has_transformations("test_key")

        manager.remove_transformations("test_key")
        assert not manager.has_transformations("test_key")
        assert "test_key" not in manager.get_keys()

    def test_remove_transformations_nonexistent_key(self) -> None:
        """Test removing transformations for non-existent key."""
        manager = TransformationsManager()

        # Should not raise an exception
        manager.remove_transformations("nonexistent")

    def test_apply_transformations_no_transformations(self) -> None:
        """Test applying transformations when none exist."""
        manager = TransformationsManager()

        result = manager.apply_transformations("test_key", "original_value")
        assert result == "original_value"

    def test_apply_transformations_single_transformation(self) -> None:
        """Test applying single transformation."""
        manager = TransformationsManager()

        def transform_func(value: str) -> str:
            return value.upper()

        manager.add_transformation("test_key", transform_func)

        result = manager.apply_transformations("test_key", "hello")
        assert result == "HELLO"

    def test_apply_transformations_multiple_transformations(self) -> None:
        """Test applying multiple transformations in sequence."""
        manager = TransformationsManager()

        def transform_func1(value: str) -> str:
            return value.upper()

        def transform_func2(value: str) -> str:
            return f"prefix_{value}"

        def transform_func3(value: str) -> str:
            return f"{value}_suffix"

        manager.add_transformation("test_key", transform_func1)
        manager.add_transformation("test_key", transform_func2)
        manager.add_transformation("test_key", transform_func3)

        result = manager.apply_transformations("test_key", "hello")
        assert result == "prefix_HELLO_suffix"

    def test_apply_transformations_with_exception(self) -> None:
        """Test applying transformations with exception handling."""
        manager = TransformationsManager()

        def failing_transform(value: str) -> str:
            raise ValueError("Transformation failed")

        def working_transform(value: str) -> str:
            return value.upper()

        manager.add_transformation("test_key", failing_transform)
        manager.add_transformation("test_key", working_transform)

        result = manager.apply_transformations("test_key", "hello")
        # Should continue with next transformation after failure
        assert result == "HELLO"

    def test_apply_transformations_all_fail(self) -> None:
        """Test applying transformations when all fail."""
        manager = TransformationsManager()

        def failing_transform1(value: str) -> str:
            raise ValueError("First transformation failed")

        def failing_transform2(value: str) -> str:
            raise RuntimeError("Second transformation failed")

        manager.add_transformation("test_key", failing_transform1)
        manager.add_transformation("test_key", failing_transform2)

        result = manager.apply_transformations("test_key", "original")
        # Should return original value when all transformations fail
        assert result == "original"

    def test_apply_transformations_numeric_values(self) -> None:
        """Test applying transformations to numeric values."""
        manager = TransformationsManager()

        def double_transform(value: int) -> int:
            return value * 2

        def add_ten_transform(value: int) -> int:
            return value + 10

        manager.add_transformation("numeric_key", double_transform)
        manager.add_transformation("numeric_key", add_ten_transform)

        result = manager.apply_transformations("numeric_key", 5)
        assert result == 20  # (5 * 2) + 10

    def test_get_transformations_existing_key(self) -> None:
        """Test getting transformations for existing key."""
        manager = TransformationsManager()

        def transform_func(value: str) -> str:
            return value.upper()

        manager.add_transformation("test_key", transform_func)

        transformations = manager.get_transformations("test_key")
        assert len(transformations) == 1
        assert isinstance(transformations[0], Transformation)

        # Should be a copy
        assert transformations is not manager._transformations["test_key"]

    def test_get_transformations_nonexistent_key(self) -> None:
        """Test getting transformations for non-existent key."""
        manager = TransformationsManager()

        transformations = manager.get_transformations("nonexistent")
        assert transformations == []

    def test_get_all_transformations(self) -> None:
        """Test getting all transformations."""
        manager = TransformationsManager()

        def transform_func1(value: str) -> str:
            return value.upper()

        def transform_func2(value: str) -> str:
            return value.lower()

        manager.add_transformation("key1", transform_func1)
        manager.add_transformation("key2", transform_func2)

        all_transformations = manager.get_all_transformations()
        assert len(all_transformations) == 2
        assert "key1" in all_transformations
        assert "key2" in all_transformations
        assert len(all_transformations["key1"]) == 1
        assert len(all_transformations["key2"]) == 1

        # Should be a copy
        assert all_transformations is not manager._transformations

    def test_has_transformations_true(self) -> None:
        """Test has_transformations returns True for existing key."""
        manager = TransformationsManager()

        def transform_func(value: str) -> str:
            return value.upper()

        manager.add_transformation("test_key", transform_func)
        assert manager.has_transformations("test_key")

    def test_has_transformations_false(self) -> None:
        """Test has_transformations returns False for non-existent key."""
        manager = TransformationsManager()
        assert not manager.has_transformations("nonexistent")

    def test_get_keys(self) -> None:
        """Test getting all keys."""
        manager = TransformationsManager()

        def transform_func(value: str) -> str:
            return value.upper()

        manager.add_transformation("key1", transform_func)
        manager.add_transformation("key2", transform_func)

        keys = manager.get_keys()
        assert len(keys) == 2
        assert "key1" in keys
        assert "key2" in keys

    def test_copy_to_manager(self) -> None:
        """Test copying to another manager."""
        manager1 = TransformationsManager()
        manager2 = TransformationsManager()

        def transform_func1(value: str) -> str:
            return value.upper()

        def transform_func2(value: str) -> str:
            return value.lower()

        manager1.add_transformation("key1", transform_func1)
        manager1.add_transformation("key2", transform_func2)

        manager1.copy_to_manager(manager2)

        # Verify transformations were copied
        assert manager2.has_transformations("key1")
        assert manager2.has_transformations("key2")
        assert len(manager2.get_transformations("key1")) == 1
        assert len(manager2.get_transformations("key2")) == 1

        # Verify they are separate instances
        assert manager2._transformations is not manager1._transformations

    def test_clear(self) -> None:
        """Test clearing all transformations."""
        manager = TransformationsManager()

        def transform_func(value: str) -> str:
            return value.upper()

        manager.add_transformation("key1", transform_func)
        manager.add_transformation("key2", transform_func)

        assert len(manager.get_keys()) == 2

        manager.clear()
        assert len(manager.get_keys()) == 0
        assert len(manager) == 0

    def test_len(self) -> None:
        """Test __len__ method."""
        manager = TransformationsManager()

        def transform_func(value: str) -> str:
            return value.upper()

        assert len(manager) == 0

        manager.add_transformation("key1", transform_func)
        assert len(manager) == 1

        manager.add_transformation("key2", transform_func)
        assert len(manager) == 2

        manager.add_transformation("key1", transform_func)  # Same key
        assert len(manager) == 2  # Should still be 2 unique keys

    def test_contains(self) -> None:
        """Test __contains__ method."""
        manager = TransformationsManager()

        def transform_func(value: str) -> str:
            return value.upper()

        assert "key1" not in manager

        manager.add_transformation("key1", transform_func)
        assert "key1" in manager
        assert "key2" not in manager

    def test_transformation_isolation(self) -> None:
        """Test that transformations are isolated between keys."""
        manager = TransformationsManager()

        def uppercase_transform(value: str) -> str:
            return value.upper()

        def lowercase_transform(value: str) -> str:
            return value.lower()

        manager.add_transformation("key1", uppercase_transform)
        manager.add_transformation("key2", lowercase_transform)

        result1 = manager.apply_transformations("key1", "Hello")
        result2 = manager.apply_transformations("key2", "WORLD")
        result3 = manager.apply_transformations("key3", "Unchanged")

        assert result1 == "HELLO"
        assert result2 == "world"
        assert result3 == "Unchanged"

    def test_complex_data_transformations(self) -> None:
        """Test transformations with complex data types."""
        manager = TransformationsManager()

        def add_timestamp_transform(value: dict[str, Any]) -> dict[str, Any]:
            import time

            new_value = value.copy()
            new_value["timestamp"] = time.time()
            return new_value

        def add_version_transform(value: dict[str, Any]) -> dict[str, Any]:
            new_value = value.copy()
            new_value["version"] = "1.0"
            return new_value

        manager.add_transformation("data_key", add_timestamp_transform)
        manager.add_transformation("data_key", add_version_transform)

        original_data = {"name": "test", "value": 42}
        result = manager.apply_transformations("data_key", original_data)

        assert result["name"] == "test"
        assert result["value"] == 42
        assert "timestamp" in result
        assert result["version"] == "1.0"

    def test_transformation_chaining_effect(self) -> None:
        """Test that transformations properly chain their effects."""
        manager = TransformationsManager()

        def to_list_transform(value: str) -> list[str]:
            return [value]

        def append_item_transform(value: list[str]) -> list[str]:
            return value + ["appended"]

        def count_items_transform(value: list[str]) -> int:
            return len(value)

        manager.add_transformation("chain_key", to_list_transform)
        manager.add_transformation("chain_key", append_item_transform)
        manager.add_transformation("chain_key", count_items_transform)

        result = manager.apply_transformations("chain_key", "initial")
        assert result == 2  # ["initial", "appended"] has length 2

    def test_transformation_with_none_values(self) -> None:
        """Test transformations with None values."""
        manager = TransformationsManager()

        def none_to_default_transform(value: Any) -> str:
            return "default" if value is None else value

        manager.add_transformation("test_key", none_to_default_transform)

        result = manager.apply_transformations("test_key", None)
        assert result == "default"

    def test_transformation_with_special_characters_in_key(self) -> None:
        """Test transformations with special characters in key."""
        manager = TransformationsManager()

        special_key = "key.with-special@chars[0]"

        def transform_func(value: str) -> str:
            return value.upper()

        manager.add_transformation(special_key, transform_func)

        result = manager.apply_transformations(special_key, "hello")
        assert result == "HELLO"

    def test_transformation_order_matters(self) -> None:
        """Test that transformation order matters for the result."""
        manager = TransformationsManager()

        def multiply_by_two(value: int) -> int:
            return value * 2

        def add_five(value: int) -> int:
            return value + 5

        manager.add_transformation("math_key", multiply_by_two)
        manager.add_transformation("math_key", add_five)

        # (10 * 2) + 5 = 25
        result = manager.apply_transformations("math_key", 10)
        assert result == 25
