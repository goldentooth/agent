"""Tests for source flow combinators."""

import pytest

from flowengine.combinators.sources import range_flow, repeat_flow


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
    values = []
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
