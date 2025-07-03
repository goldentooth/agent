"""Tests for source flow combinators."""

import pytest

from flowengine.combinators.sources import range_flow


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
