"""Tests for flowengine.combinators.utils module."""

from flowengine.combinators.utils import get_function_name


def test_get_function_name_returns_function_name():
    def test_function():
        pass

    result = get_function_name(test_function)

    assert result == "test_function"


def test_get_function_name_returns_default_for_no_name():
    class CallableWithoutName:
        def __call__(self):
            pass

    obj = CallableWithoutName()
    # Callable objects without __name__ attribute

    result = get_function_name(obj)

    assert result == "function"
