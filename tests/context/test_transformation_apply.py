"""Tests for Transformation.apply method."""

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
    """Double numeric values, pass through others."""
    if isinstance(value, (int, float)):
        return value * 2
    return value


def failing_transform(value: Any) -> str:
    """Transformation that raises an exception."""
    raise ValueError("Transformation failed")


class TestTransformationApply:
    """Test suite for Transformation.apply method."""

    def test_apply_basic(self) -> None:
        """Test basic apply functionality."""

        def test_func(value: Any) -> str:
            return f"result_{value}"

        transformation = Transformation(test_func, "test_key")
        result = transformation.apply("input")

        assert result == "result_input"

    def test_apply_with_different_types(self) -> None:
        """Test apply with different input value types."""

        def str_transform(value: Any) -> str:
            return f"str_{value}"

        transformation = Transformation(str_transform, "test_key")

        # Test with different types
        assert transformation.apply("string") == "str_string"
        assert transformation.apply(42) == "str_42"
        assert transformation.apply(3.14) == "str_3.14"
        assert transformation.apply(True) == "str_True"
        assert transformation.apply(None) == "str_None"
        assert transformation.apply([1, 2, 3]) == "str_[1, 2, 3]"
        assert transformation.apply({"key": "value"}) == "str_{'key': 'value'}"

    def test_apply_with_predefined_functions(self) -> None:
        """Test apply with predefined transformation functions."""

        transformation1 = Transformation(simple_transform, "simple_key")
        assert transformation1.apply("test") == "transformed_test"
        assert transformation1.apply(123) == "transformed_123"

        transformation2 = Transformation(uppercase_transform, "upper_key")
        assert transformation2.apply("hello") == "HELLO"
        assert transformation2.apply("World") == "WORLD"

        transformation3 = Transformation(double_transform, "double_key")
        assert transformation3.apply(5) == 10
        assert transformation3.apply(2.5) == 5.0
        assert transformation3.apply("text") == "text"

    def test_apply_with_builtin_functions(self) -> None:
        """Test apply with builtin transformation functions."""

        str_transformation = Transformation(str, "str_key")
        assert str_transformation.apply(42) == "42"
        assert str_transformation.apply(3.14) == "3.14"
        assert str_transformation.apply(True) == "True"

        len_transformation = Transformation(len, "len_key")
        assert len_transformation.apply("hello") == 5
        assert len_transformation.apply([1, 2, 3, 4]) == 4
        assert len_transformation.apply({"a": 1, "b": 2}) == 2

    def test_apply_with_lambda_function(self) -> None:
        """Test apply with lambda transformation function."""

        lambda_func: Callable[[Any], Any] = lambda x: x * 3
        transformation = Transformation(lambda_func, "lambda_key")

        assert transformation.apply(2) == 6
        assert transformation.apply(4) == 12
        assert transformation.apply("a") == "aaa"

    def test_apply_with_callable_object(self) -> None:
        """Test apply with callable object."""

        class CallableTransform:
            def __init__(self, multiplier: int) -> None:
                super().__init__()
                self.multiplier = multiplier

            def __call__(self, value: Any) -> Any:
                if isinstance(value, (int, float)):
                    return value * self.multiplier
                return f"{value}_multiplied"

        callable_obj = CallableTransform(5)
        transformation = Transformation(callable_obj, "callable_key")

        assert transformation.apply(3) == 15
        assert transformation.apply(2.0) == 10.0
        assert transformation.apply("test") == "test_multiplied"

    def test_apply_preserves_exception_from_function(self) -> None:
        """Test that apply preserves exceptions from transformation function."""

        transformation = Transformation(failing_transform, "fail_key")

        with pytest.raises(ValueError, match="Transformation failed"):
            transformation.apply("any_value")

    def test_apply_with_none_value(self) -> None:
        """Test apply with None input value."""

        def none_handler(value: Any) -> str:
            if value is None:
                return "none_handled"
            return f"not_none_{value}"

        transformation = Transformation(none_handler, "none_key")

        assert transformation.apply(None) == "none_handled"
        assert transformation.apply("not_none") == "not_none_not_none"

    def test_apply_with_complex_data_structures(self) -> None:
        """Test apply with complex data structures."""

        def data_transform(value: Any) -> dict[str, Any]:
            return {
                "original": value,
                "type": type(value).__name__,
                "length": len(value) if hasattr(value, "__len__") else 0,
            }

        transformation = Transformation(data_transform, "data_key")

        # Test with list
        result = transformation.apply([1, 2, 3])
        assert result["original"] == [1, 2, 3]
        assert result["type"] == "list"
        assert result["length"] == 3

        # Test with dict
        result = transformation.apply({"a": 1, "b": 2})
        assert result["original"] == {"a": 1, "b": 2}
        assert result["type"] == "dict"
        assert result["length"] == 2

    def test_apply_return_value_preservation(self) -> None:
        """Test that apply preserves exact return value from function."""

        def identity_transform(value: Any) -> Any:
            return value

        transformation = Transformation(identity_transform, "identity_key")

        # Test various types are preserved exactly
        test_values = [
            "string",
            42,
            3.14,
            True,
            False,
            None,
            [1, 2, 3],
            {"key": "value"},
            (1, 2, 3),
            {1, 2, 3},
        ]

        for value in test_values:
            result = transformation.apply(value)
            assert result is value  # Should be the exact same object

    def test_apply_function_state_preservation(self) -> None:
        """Test that apply doesn't affect function state."""

        def stateful_func(value: Any) -> str:
            if not hasattr(stateful_func, "call_count"):
                stateful_func.call_count = 0  # type: ignore[attr-defined]
            stateful_func.call_count += 1  # type: ignore[attr-defined]
            return f"call_{stateful_func.call_count}_{value}"  # type: ignore[attr-defined]

        transformation = Transformation(stateful_func, "stateful_key")

        # Multiple calls should maintain function state
        assert transformation.apply("first") == "call_1_first"
        assert transformation.apply("second") == "call_2_second"
        assert transformation.apply("third") == "call_3_third"

    def test_apply_performance_multiple_calls(self) -> None:
        """Test apply performance with multiple calls."""

        def fast_transform(value: Any) -> str:
            return f"fast_{value}"

        transformation = Transformation(fast_transform, "perf_key")

        # Multiple rapid calls should work efficiently
        results: list[str] = []
        for i in range(1000):
            result = transformation.apply(f"value_{i}")
            results.append(result)

        # Verify all results are correct
        for i, result in enumerate(results):
            assert result == f"fast_value_{i}"
