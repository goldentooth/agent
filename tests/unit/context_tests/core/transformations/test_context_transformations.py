"""Tests for Context.transformations property."""

from context.computed import Transformation
from context.main import Context


class TestContextTransformations:
    """Test suite for Context.transformations property."""

    def test_transformations_empty_context(self) -> None:
        """Test transformations property on empty context."""
        context = Context()

        result = context.transformations()

        assert isinstance(result, dict)
        assert len(result) == 0

    def test_transformations_single_key_single_transformation(self) -> None:
        """Test transformations property with single transformation."""
        context = Context()

        # Add transformation
        context.add_transformation("name", str.upper)

        # Get transformations
        result = context.transformations()

        # Verify structure
        assert isinstance(result, dict)
        assert len(result) == 1
        assert "name" in result
        assert isinstance(result["name"], list)
        assert len(result["name"]) == 1
        assert isinstance(result["name"][0], Transformation)
        assert result["name"][0].func is str.upper
        assert result["name"][0].key == "name"

    def test_transformations_single_key_multiple_transformations(self) -> None:
        """Test transformations property with multiple transformations on same key."""
        context = Context()

        # Add multiple transformations
        func1 = lambda x: x * 2
        func2 = str.upper
        func3 = lambda x: x + "!"

        context.add_transformation("value", func1)
        context.add_transformation("value", func2)
        context.add_transformation("value", func3)

        # Get transformations and verify structure
        result = context.transformations()
        assert len(result) == 1
        assert "value" in result
        assert len(result["value"]) == 3

        # Verify order and keys
        assert result["value"][0].func is func1
        assert result["value"][1].func is func2
        assert result["value"][2].func is func3

    def test_transformations_multiple_keys(self) -> None:
        """Test transformations property with multiple keys."""
        context = Context()

        # Add transformations to different keys
        context.add_transformation("key1", str.upper)
        context.add_transformation("key2", str.lower)
        context.add_transformation("key3", lambda x: x * 2)

        # Get transformations
        result = context.transformations()

        # Verify structure
        assert len(result) == 3
        assert "key1" in result
        assert "key2" in result
        assert "key3" in result

        # Verify each key has expected transformations
        assert len(result["key1"]) == 1
        assert len(result["key2"]) == 1
        assert len(result["key3"]) == 1

        assert result["key1"][0].func is str.upper
        assert result["key2"][0].func is str.lower

    def test_transformations_mixed_multiple_keys_and_transformations(self) -> None:
        """Test transformations property with complex setup."""
        context = Context()

        # Add varied transformations
        context.add_transformation("single", str.upper)
        context.add_transformation("multiple", lambda x: x * 2)
        context.add_transformation("multiple", str.lower)
        context.add_transformation("multiple", lambda x: x + "!")
        context.add_transformation("another", str.strip)

        # Get transformations
        result = context.transformations()

        # Verify structure
        assert len(result) == 3
        assert len(result["single"]) == 1
        assert len(result["multiple"]) == 3
        assert len(result["another"]) == 1

    def test_transformations_returns_copy(self) -> None:
        """Test that transformations property returns defensive copy."""
        context = Context()

        # Add transformation
        context.add_transformation("test", str.upper)

        # Get transformations twice
        result1 = context.transformations()
        result2 = context.transformations()

        # Verify different objects but same content
        assert result1 is not result2
        assert result1["test"] is not result2["test"]
        assert len(result1["test"]) == len(result2["test"])
        assert result1["test"][0].func is result2["test"][0].func

    def test_transformations_copy_prevents_external_modification(self) -> None:
        """Test that modifying returned transformations doesn't affect context."""
        context = Context()

        # Add transformations
        context.add_transformation("key", str.upper)
        context.add_transformation("key", str.lower)

        # Get transformations and modify
        result = context.transformations()
        original_length = len(result["key"])

        # Modify the returned list
        result["key"].clear()
        result["other"] = [Transformation(str.strip, "other")]

        # Verify context is unchanged
        new_result = context.transformations()
        assert len(new_result["key"]) == original_length
        assert "other" not in new_result

    def test_transformations_after_removal(self) -> None:
        """Test transformations property after removing transformations."""
        context = Context()

        # Add transformations
        context.add_transformation("keep", str.upper)
        context.add_transformation("remove", str.lower)

        # Verify initial state
        result = context.transformations()
        assert len(result) == 2

        # Remove transformations
        context.remove_transformations("remove")

        # Verify updated state
        result = context.transformations()
        assert len(result) == 1
        assert "keep" in result
        assert "remove" not in result

    def test_transformations_function_references_preserved(self) -> None:
        """Test that function references are preserved in transformations."""
        context = Context()

        # Create specific functions
        def func1(x: str) -> str:
            return x.upper()

        def func2(x: str) -> str:
            return x.lower()

        # Add transformations
        context.add_transformation("test", func1)
        context.add_transformation("test", func2)

        # Get transformations
        result = context.transformations()

        # Verify exact function references
        assert result["test"][0].func is func1
        assert result["test"][1].func is func2

    def test_transformations_empty_after_all_removed(self) -> None:
        """Test transformations property after removing all transformations."""
        context = Context()

        # Add transformations
        context.add_transformation("key1", str.upper)
        context.add_transformation("key2", str.lower)

        # Remove all transformations
        context.remove_transformations("key1")
        context.remove_transformations("key2")

        # Verify empty result
        result = context.transformations()
        assert len(result) == 0

    def test_transformations_independence_between_contexts(self) -> None:
        """Test that transformations from different contexts are independent."""
        context1 = Context()
        context2 = Context()

        # Add different transformations to each context
        context1.add_transformation("shared", str.upper)
        context2.add_transformation("shared", str.lower)
        context2.add_transformation("unique", lambda x: x * 2)

        # Get transformations from each
        result1 = context1.transformations()
        result2 = context2.transformations()

        # Verify independence
        assert len(result1) == 1
        assert len(result2) == 2
        assert result1["shared"][0].func is str.upper
        assert result2["shared"][0].func is str.lower
        assert "unique" not in result1
        assert "unique" in result2

    def test_transformations_special_characters_keys(self) -> None:
        """Test transformations property with special character keys."""
        context = Context()

        # Add transformations with special keys
        special_keys = ["key.with.dots", "key-with-dashes", "key_with_underscores"]

        for key in special_keys:
            context.add_transformation(key, str.upper)

        # Get transformations
        result = context.transformations()

        # Verify all special keys present
        assert len(result) == 3
        for key in special_keys:
            assert key in result
            assert len(result[key]) == 1

    def test_transformations_empty_string_key(self) -> None:
        """Test transformations property with empty string key."""
        context = Context()

        # Add transformation with empty key
        context.add_transformation("", str.upper)

        # Get transformations
        result = context.transformations()

        # Verify empty key handling
        assert len(result) == 1
        assert "" in result
        assert len(result[""]) == 1

    def test_transformations_type_annotation(self) -> None:
        """Test that transformations property has correct type annotation."""
        context = Context()

        # Add transformations
        context.add_transformation("test", str.upper)

        # Get transformations
        result = context.transformations()

        # Verify types
        assert isinstance(result, dict)
        for key, transformations_list in result.items():
            assert isinstance(key, str)
            assert isinstance(transformations_list, list)
            for transformation in transformations_list:
                assert isinstance(transformation, Transformation)
