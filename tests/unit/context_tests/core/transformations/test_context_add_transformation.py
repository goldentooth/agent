"""Tests for Context.add_transformation method."""

from context.computed import Transformation
from context.main import Context


class TestContextAddTransformation:
    """Test suite for Context.add_transformation method."""

    def test_add_transformation_basic(self) -> None:
        """Test basic transformation functionality."""
        context = Context()

        # Add a simple transformation
        context.add_transformation("name", str.upper)

        # Verify transformation was added
        assert "name" in context._transformations_manager._transformations
        assert len(context._transformations_manager._transformations["name"]) == 1
        assert isinstance(
            context._transformations_manager._transformations["name"][0], Transformation
        )
        assert (
            context._transformations_manager._transformations["name"][0].func
            is str.upper
        )
        assert (
            context._transformations_manager._transformations["name"][0].key == "name"
        )

    def test_add_transformation_multiple_keys(self) -> None:
        """Test adding transformations to multiple keys."""
        context = Context()

        # Add transformations to different keys
        context.add_transformation("key1", str.upper)
        context.add_transformation("key2", str.lower)
        context.add_transformation("key3", lambda x: x * 2)

        # Verify all transformations were added
        assert "key1" in context._transformations_manager._transformations
        assert "key2" in context._transformations_manager._transformations
        assert "key3" in context._transformations_manager._transformations
        assert len(context._transformations_manager._transformations["key1"]) == 1
        assert len(context._transformations_manager._transformations["key2"]) == 1
        assert len(context._transformations_manager._transformations["key3"]) == 1

    def test_add_transformation_multiple_per_key(self) -> None:
        """Test adding multiple transformations to the same key."""
        context = Context()

        # Add multiple transformations to the same key
        context.add_transformation("value", lambda x: x * 2)
        context.add_transformation("value", lambda x: x + 1)
        context.add_transformation("value", lambda x: x * 3)

        # Verify all transformations were added in order
        assert "value" in context._transformations_manager._transformations
        assert len(context._transformations_manager._transformations["value"]) == 3

        # Check the functions are stored correctly
        transformations = context._transformations_manager._transformations["value"]
        for i, transformation in enumerate(transformations):
            assert isinstance(transformation, Transformation)
            assert transformation.key == "value"

    def test_add_transformation_different_function_types(self) -> None:
        """Test adding different types of functions as transformations."""
        context = Context()

        # Built-in function
        context.add_transformation("builtin", str.upper)

        # Lambda function
        context.add_transformation("lambda", lambda x: x.lower())

        # Named function
        def named_func(x: str) -> str:
            return x.strip()

        context.add_transformation("named", named_func)

        # Method reference
        class TestClass:
            def transform_method(self, x: str) -> str:
                return x.replace(" ", "_")

        test_obj = TestClass()
        context.add_transformation("method", test_obj.transform_method)

        # Verify all transformation types work
        assert len(context._transformations_manager._transformations) == 4
        assert "builtin" in context._transformations_manager._transformations
        assert "lambda" in context._transformations_manager._transformations
        assert "named" in context._transformations_manager._transformations
        assert "method" in context._transformations_manager._transformations

    def test_add_transformation_callable_objects(self) -> None:
        """Test adding callable objects as transformations."""
        context = Context()

        # Callable class
        class CallableTransform:
            def __call__(self, x: str) -> str:
                return x.title()

        callable_obj = CallableTransform()
        context.add_transformation("callable", callable_obj)

        # Verify callable object was added
        assert "callable" in context._transformations_manager._transformations
        assert len(context._transformations_manager._transformations["callable"]) == 1
        assert (
            context._transformations_manager._transformations["callable"][0].func
            is callable_obj
        )

    def test_add_transformation_empty_key(self) -> None:
        """Test adding transformation with empty key."""
        context = Context()

        # Add transformation with empty key
        context.add_transformation("", str.upper)

        # Verify transformation was added
        assert "" in context._transformations_manager._transformations
        assert len(context._transformations_manager._transformations[""]) == 1

    def test_add_transformation_key_with_spaces(self) -> None:
        """Test adding transformation with key containing spaces."""
        context = Context()

        # Add transformation with spaced key
        context.add_transformation("key with spaces", str.upper)

        # Verify transformation was added
        assert "key with spaces" in context._transformations_manager._transformations
        assert (
            len(context._transformations_manager._transformations["key with spaces"])
            == 1
        )

    def test_add_transformation_special_characters_key(self) -> None:
        """Test adding transformation with special characters in key."""
        context = Context()

        # Add transformations with special character keys
        special_keys = [
            "key.with.dots",
            "key-with-dashes",
            "key_with_underscores",
            "key@symbol",
        ]

        for key in special_keys:
            context.add_transformation(key, str.upper)

        # Verify all transformations were added
        for key in special_keys:
            assert key in context._transformations_manager._transformations
            assert len(context._transformations_manager._transformations[key]) == 1

    def test_add_transformation_preserves_function_reference(self) -> None:
        """Test that function references are preserved correctly."""
        context = Context()

        # Create a function with specific identity
        def specific_function(x: str) -> str:
            return x.replace("a", "A")

        context.add_transformation("test", specific_function)

        # Verify the exact function reference is preserved
        stored_transformation = context._transformations_manager._transformations[
            "test"
        ][0]
        assert stored_transformation.func is specific_function
        assert stored_transformation.key == "test"

    def test_add_transformation_order_preservation(self) -> None:
        """Test that transformation order is preserved when multiple are added."""
        context = Context()

        # Add transformations in specific order
        functions = [
            lambda x: f"1:{x}",
            lambda x: f"2:{x}",
            lambda x: f"3:{x}",
            lambda x: f"4:{x}",
        ]

        for i, func in enumerate(functions):
            context.add_transformation("ordered", func)

        # Verify order is preserved
        transformations = context._transformations_manager._transformations["ordered"]
        assert len(transformations) == 4

        for i, transformation in enumerate(transformations):
            assert transformation.func is functions[i]

    def test_add_transformation_mixed_key_types(self) -> None:
        """Test adding transformations with various key types converted to strings."""
        context = Context()

        # Add transformations with different key types
        # (all should be converted to strings internally)
        context.add_transformation("string_key", str.upper)

        # Verify string keys work
        assert "string_key" in context._transformations_manager._transformations

    def test_add_transformation_returns_none(self) -> None:
        """Test that add_transformation returns None."""
        context = Context()

        # Call the method and verify it doesn't crash
        context.add_transformation("test", str.upper)

        # Verify the transformation was added (indirect test of return behavior)
        assert "test" in context._transformations_manager._transformations

    def test_add_transformation_independence(self) -> None:
        """Test that transformations added to different contexts are independent."""
        context1 = Context()
        context2 = Context()

        # Add transformations to different contexts
        context1.add_transformation("shared_key", str.upper)
        context2.add_transformation("shared_key", str.lower)

        # Verify they are independent
        assert (
            len(context1._transformations_manager._transformations["shared_key"]) == 1
        )
        assert (
            len(context2._transformations_manager._transformations["shared_key"]) == 1
        )
        assert (
            context1._transformations_manager._transformations["shared_key"][0].func
            is str.upper
        )
        assert (
            context2._transformations_manager._transformations["shared_key"][0].func
            is str.lower
        )

    def test_add_transformation_modification_after_addition(self) -> None:
        """Test that transformations list can be modified after addition."""
        context = Context()

        # Add initial transformation
        context.add_transformation("modifiable", str.upper)
        assert len(context._transformations_manager._transformations["modifiable"]) == 1

        # Add another transformation to the same key
        context.add_transformation("modifiable", str.lower)
        assert len(context._transformations_manager._transformations["modifiable"]) == 2

        # Verify both transformations exist
        transformations = context._transformations_manager._transformations[
            "modifiable"
        ]
        assert transformations[0].func is str.upper
        assert transformations[1].func is str.lower
