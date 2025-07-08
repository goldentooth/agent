"""Tests for Transformation.__init__ method."""

from typing import Any, Callable

import pytest

from context.main import Transformation


def simple_transform(value: Any) -> str:
    """Simple transformation function for testing."""
    return f"transformed_{value}"


def uppercase_transform(value: Any) -> str:
    """Uppercase transformation function."""
    return str(value).upper()


def double_transform(value: Any) -> Any:
    """Double numeric values."""
    if isinstance(value, (int, float)):
        return value * 2
    return value


class TestTransformationInit:
    """Test suite for Transformation.__init__ method."""

    def test_init_basic(self) -> None:
        """Test basic Transformation initialization."""

        def test_func(value: Any) -> str:
            return f"result_{value}"

        transformation = Transformation(test_func, "test_key")

        # Check that attributes are set correctly
        assert transformation.func is test_func
        assert transformation.key == "test_key"

    def test_init_with_string_key(self) -> None:
        """Test initialization with string key."""

        def test_func(value: Any) -> str:
            return str(value)

        transformation = Transformation(test_func, "my_key")

        assert transformation.func is test_func
        assert transformation.key == "my_key"

    def test_init_with_empty_string_key(self) -> None:
        """Test initialization with empty string key."""

        def test_func(value: Any) -> str:
            return "empty"

        transformation = Transformation(test_func, "")

        assert transformation.func is test_func
        assert transformation.key == ""

    def test_init_with_lambda_function(self) -> None:
        """Test initialization with lambda function."""

        transform_func: Callable[[Any], Any] = lambda x: x * 2  # noqa: E731
        transformation = Transformation(transform_func, "lambda_key")

        assert transformation.func is transform_func
        assert transformation.key == "lambda_key"

    def test_init_with_builtin_function(self) -> None:
        """Test initialization with builtin function."""

        transformation = Transformation(str, "builtin_key")

        assert transformation.func is str
        assert transformation.key == "builtin_key"

    def test_init_with_callable_object(self) -> None:
        """Test initialization with callable object."""

        class CallableTransform:
            def __call__(self, value: Any) -> str:
                return f"callable_{value}"

        callable_obj = CallableTransform()
        transformation = Transformation(callable_obj, "callable_key")

        assert transformation.func is callable_obj
        assert transformation.key == "callable_key"

    def test_init_preserves_function_reference(self) -> None:
        """Test that initialization preserves exact function reference."""

        def original_func(value: Any) -> str:
            return f"original_{value}"

        transformation = Transformation(original_func, "reference_key")

        # Should be the exact same function object
        assert transformation.func is original_func
        assert id(transformation.func) == id(original_func)

    def test_init_with_complex_key_name(self) -> None:
        """Test initialization with complex key names."""

        def test_func(value: Any) -> str:
            return str(value)

        complex_keys = [
            "user.profile.name",
            "config_setting_123",
            "nested[0].value",
            "special-chars!@#$%",
            "unicode_ключ_🔑",
        ]

        for key in complex_keys:
            transformation = Transformation(test_func, key)
            assert transformation.key == key
            assert transformation.func is test_func

    def test_init_function_with_different_signatures(self) -> None:
        """Test initialization with functions having different signatures."""

        def no_args() -> str:
            return "no_args"

        def one_arg(x: Any) -> str:
            return f"one_{x}"

        def two_args(x: Any, y: Any) -> str:
            return f"two_{x}_{y}"

        def varargs(*args: Any) -> str:
            return f"varargs_{len(args)}"

        def kwargs(**kwargs: Any) -> str:
            return f"kwargs_{len(kwargs)}"

        functions = [no_args, one_arg, two_args, varargs, kwargs]

        for i, func in enumerate(functions):
            transformation = Transformation(func, f"key_{i}")
            assert transformation.func is func
            assert transformation.key == f"key_{i}"

    def test_init_with_predefined_functions(self) -> None:
        """Test initialization with predefined transformation functions."""

        transformation1 = Transformation(simple_transform, "simple_key")
        assert transformation1.func is simple_transform
        assert transformation1.key == "simple_key"

        transformation2 = Transformation(uppercase_transform, "upper_key")
        assert transformation2.func is uppercase_transform
        assert transformation2.key == "upper_key"

        transformation3 = Transformation(double_transform, "double_key")
        assert transformation3.func is double_transform
        assert transformation3.key == "double_key"

    def test_init_multiple_transformations_same_function(self) -> None:
        """Test creating multiple transformations with same function."""

        def shared_func(value: Any) -> str:
            return f"shared_{value}"

        transformation1 = Transformation(shared_func, "key1")
        transformation2 = Transformation(shared_func, "key2")
        transformation3 = Transformation(shared_func, "key3")

        # All should reference the same function
        assert transformation1.func is shared_func
        assert transformation2.func is shared_func
        assert transformation3.func is shared_func

        # But have different keys
        assert transformation1.key == "key1"
        assert transformation2.key == "key2"
        assert transformation3.key == "key3"

    def test_init_function_attribute_preservation(self) -> None:
        """Test that function attributes are preserved after initialization."""

        def documented_func(value: Any) -> str:
            """This function has documentation."""
            return str(value)

        documented_func.custom_attr = "custom_value"  # type: ignore[attr-defined]

        transformation = Transformation(documented_func, "doc_key")

        # Function attributes should be preserved
        assert transformation.func.__doc__ == "This function has documentation."
        assert transformation.func.custom_attr == "custom_value"
        assert transformation.func.__name__ == "documented_func"
