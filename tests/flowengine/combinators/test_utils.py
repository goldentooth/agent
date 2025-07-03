"""Tests for flowengine.combinators.utils module."""

from flowengine.combinators.utils import STREAM_END, get_function_name


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


def test_stream_end_is_singleton():
    # STREAM_END should be a unique sentinel object
    assert STREAM_END is STREAM_END
    assert STREAM_END == STREAM_END
    assert STREAM_END != object()
    assert STREAM_END is not None
