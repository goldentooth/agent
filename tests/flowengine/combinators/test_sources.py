"""Tests for source flow combinators."""

import pytest

from flowengine.combinators.sources import (
    empty_flow,
    range_flow,
    repeat_flow,
    start_with_stream,
)


@pytest.mark.asyncio
async def test_range_flow_basic():
    """Test basic range generation."""
    flow = range_flow(0, 5)
    assert "range(0, 5, 1)" in flow.name

    # Range flows don't need input
    result_stream = flow(None)  # type: ignore
    values = [item async for item in result_stream]
    assert values == [0, 1, 2, 3, 4]


@pytest.mark.asyncio
async def test_range_flow_with_step():
    """Test range with custom step."""
    flow = range_flow(0, 10, 2)
    assert "range(0, 10, 2)" in flow.name

    result_stream = flow(None)  # type: ignore
    values = [item async for item in result_stream]
    assert values == [0, 2, 4, 6, 8]


@pytest.mark.asyncio
async def test_range_flow_negative_step():
    """Test range with negative step."""
    flow = range_flow(5, 0, -1)
    result_stream = flow(None)  # type: ignore
    values = [item async for item in result_stream]
    assert values == [5, 4, 3, 2, 1]


@pytest.mark.asyncio
async def test_range_flow_empty():
    """Test range that produces no values."""
    flow = range_flow(5, 5)
    result_stream = flow(None)  # type: ignore
    values = [item async for item in result_stream]
    assert values == []


@pytest.mark.asyncio
async def test_repeat_flow_finite():
    """Test repeating a value finite times."""
    flow = repeat_flow("hello", 3)
    assert "repeat(hello, 3)" in flow.name

    result_stream = flow(None)  # type: ignore
    values = [item async for item in result_stream]
    assert values == ["hello", "hello", "hello"]


@pytest.mark.asyncio
async def test_repeat_flow_zero_times():
    """Test repeating zero times."""
    flow = repeat_flow("test", 0)
    result_stream = flow(None)  # type: ignore
    values = [item async for item in result_stream]
    assert values == []


@pytest.mark.asyncio
async def test_repeat_flow_infinite():
    """Test infinite repeat (limited by take)."""
    flow = repeat_flow(42, None)
    assert "repeat(42, ∞)" in flow.name

    result_stream = flow(None)  # type: ignore

    # Take only first 5 items to avoid infinite loop
    values: list[int] = []
    count = 0
    async for item in result_stream:
        values.append(item)
        count += 1
        if count >= 5:
            break

    assert values == [42, 42, 42, 42, 42]


@pytest.mark.asyncio
async def test_repeat_flow_complex_object():
    """Test repeating complex objects."""
    obj = {"key": "value", "number": 123}
    flow = repeat_flow(obj, 2)

    result_stream = flow(None)  # type: ignore
    values = [item async for item in result_stream]
    assert values == [obj, obj]
    # Verify they're the same object
    assert values[0] is values[1]


@pytest.mark.asyncio
async def test_empty_flow_basic():
    """Test empty flow produces no items."""
    flow = empty_flow()
    assert flow.name == "empty"

    result_stream = flow(None)  # type: ignore
    values = [item async for item in result_stream]
    assert values == []


@pytest.mark.asyncio
async def test_empty_flow_is_valid_generator():
    """Test empty flow is a valid async generator."""
    flow = empty_flow()
    result_stream = flow(None)  # type: ignore

    # Should be able to iterate without errors
    count = 0
    async for _ in result_stream:
        count += 1
    assert count == 0


@pytest.mark.asyncio
async def test_start_with_stream_single_item():
    """Test prepending a single item."""
    flow = start_with_stream("START")
    assert "start_with(1 items)" in flow.name

    async def input_stream():
        yield "A"
        yield "B"
        yield "C"

    result_stream = flow(input_stream())
    values = [item async for item in result_stream]
    assert values == ["START", "A", "B", "C"]


@pytest.mark.asyncio
async def test_start_with_stream_multiple_items():
    """Test prepending multiple items."""
    flow = start_with_stream(1, 2, 3)
    assert "start_with(3 items)" in flow.name

    async def input_stream():
        yield 4
        yield 5

    result_stream = flow(input_stream())
    values = [item async for item in result_stream]
    assert values == [1, 2, 3, 4, 5]


@pytest.mark.asyncio
async def test_start_with_stream_no_items():
    """Test start_with with no items (identity)."""
    # When called with no args, we need to provide type context somehow
    # Since we can't use generics syntax on function calls in Python,
    # we'll just accept the type checker warning here
    flow = start_with_stream()  # type: ignore[var-annotated]
    assert "start_with(0 items)" in flow.name

    async def input_stream():
        yield "A"
        yield "B"

    result_stream = flow(input_stream())  # type: ignore[arg-type]
    values: list[str] = []
    async for item in result_stream:  # type: ignore[misc]
        values.append(item)  # type: ignore[arg-type]
    assert values == ["A", "B"]


@pytest.mark.asyncio
async def test_start_with_stream_empty_stream():
    """Test start_with on empty input stream."""
    flow = start_with_stream("ONLY")

    async def empty_stream():
        if False:
            yield "never"

    result_stream = flow(empty_stream())
    values = [item async for item in result_stream]
    assert values == ["ONLY"]


@pytest.mark.asyncio
async def test_start_with_stream_mixed_types():
    """Test start_with with mixed types."""
    flow = start_with_stream("header", 0, None, {"meta": "data"})

    async def input_stream():
        yield "body"

    result_stream = flow(input_stream())
    values = [item async for item in result_stream]
    assert values == ["header", 0, None, {"meta": "data"}, "body"]
