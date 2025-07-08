"""Tests for flowengine.combinators.utils module."""

import pytest

from flowengine.combinators.utils import (
    STREAM_END,
    Input,
    create_single_item_stream,
    get_function_name,
)


def test_get_function_name_returns_function_name() -> None:
    def test_function() -> None:
        pass

    result = get_function_name(test_function)

    assert result == "test_function"


def test_get_function_name_returns_default_for_no_name() -> None:
    class CallableWithoutName:
        def __call__(self) -> None:
            pass

    obj = CallableWithoutName()
    # Callable objects without __name__ attribute

    result = get_function_name(obj)

    assert result == "function"


def test_stream_end_is_singleton() -> None:
    # STREAM_END should be a unique sentinel object
    assert STREAM_END is STREAM_END
    assert STREAM_END == STREAM_END
    assert STREAM_END != object()
    assert STREAM_END is not None


@pytest.mark.asyncio
async def test_create_single_item_stream_yields_one_item() -> None:
    test_item = "test value"

    stream = create_single_item_stream(test_item)

    # Collect all items from the stream
    items: list[str] = []
    async for item in stream:
        items.append(item)

    assert len(items) == 1
    assert items[0] == "test value"


@pytest.mark.asyncio
async def test_create_single_item_stream_works_with_different_types() -> None:
    # Test with integer
    int_stream = create_single_item_stream(42)
    int_items = [item async for item in int_stream]
    assert int_items == [42]

    # Test with None
    none_stream = create_single_item_stream(None)
    none_items = [item async for item in none_stream]
    assert none_items == [None]

    # Test with object
    obj = {"key": "value"}
    obj_stream = create_single_item_stream(obj)
    obj_items = [item async for item in obj_stream]
    assert obj_items == [{"key": "value"}]
    assert obj_items[0] is obj  # Same object reference


def test_input_typevar_is_available() -> None:
    # Input TypeVar should be available for type annotations
    assert Input is not None
    assert hasattr(Input, "__name__")
    assert Input.__name__ == "Input"
