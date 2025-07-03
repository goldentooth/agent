"""Tests for aggregation combinators."""

from __future__ import annotations

import pytest

from flowengine.combinators.aggregation import batch_stream, chunk_stream, window_stream
from flowengine.flow import Flow


@pytest.mark.asyncio
async def test_batch_stream():
    """Test batch_stream function."""
    # Create a flow that batches items into groups of 3
    flow: Flow[int, list[int]] = batch_stream(3)

    # Create test input stream
    async def test_stream():
        for i in range(7):
            yield i

    # Execute the flow
    result: list[list[int]] = await flow.to_list()(test_stream())

    # Should produce batches of 3, plus remaining items
    assert result == [[0, 1, 2], [3, 4, 5], [6]]


@pytest.mark.asyncio
async def test_batch_stream_empty():
    """Test batch_stream with empty stream."""
    flow: Flow[int, list[int]] = batch_stream(3)

    async def empty_stream():
        return
        yield  # pragma: no cover

    result: list[list[int]] = await flow.to_list()(empty_stream())
    assert result == []


@pytest.mark.asyncio
async def test_batch_stream_exact_size():
    """Test batch_stream with exact multiple of batch size."""
    flow: Flow[int, list[int]] = batch_stream(2)

    async def test_stream():
        for i in range(4):
            yield i

    result: list[list[int]] = await flow.to_list()(test_stream())
    assert result == [[0, 1], [2, 3]]


@pytest.mark.asyncio
async def test_batch_stream_single_item():
    """Test batch_stream with single item."""
    flow: Flow[int, list[int]] = batch_stream(5)

    async def test_stream():
        yield 42

    result: list[list[int]] = await flow.to_list()(test_stream())
    assert result == [[42]]


@pytest.mark.asyncio
async def test_chunk_stream():
    """Test chunk_stream function."""
    # Create a flow that chunks items into groups of 3
    flow: Flow[int, list[int]] = chunk_stream(3)

    # Create test input stream
    async def test_stream():
        for i in range(7):
            yield i

    # Execute the flow
    result: list[list[int]] = await flow.to_list()(test_stream())

    # Should produce chunks of 3, plus remaining items
    assert result == [[0, 1, 2], [3, 4, 5], [6]]


@pytest.mark.asyncio
async def test_chunk_stream_empty():
    """Test chunk_stream with empty stream."""
    flow: Flow[int, list[int]] = chunk_stream(3)

    async def empty_stream():
        return
        yield  # pragma: no cover

    result: list[list[int]] = await flow.to_list()(empty_stream())
    assert result == []


@pytest.mark.asyncio
async def test_chunk_stream_exact_size():
    """Test chunk_stream with exact multiple of chunk size."""
    flow: Flow[int, list[int]] = chunk_stream(2)

    async def test_stream():
        for i in range(4):
            yield i

    result: list[list[int]] = await flow.to_list()(test_stream())
    assert result == [[0, 1], [2, 3]]


@pytest.mark.asyncio
async def test_chunk_stream_single_item():
    """Test chunk_stream with single item."""
    flow: Flow[int, list[int]] = chunk_stream(5)

    async def test_stream():
        yield 42

    result: list[list[int]] = await flow.to_list()(test_stream())
    assert result == [[42]]


@pytest.mark.asyncio
async def test_window_stream():
    """Test window_stream function with default step."""
    # Create a flow that creates sliding windows of size 3
    flow: Flow[int, list[int]] = window_stream(3)

    # Create test input stream
    async def test_stream():
        for i in range(6):
            yield i

    # Execute the flow
    result: list[list[int]] = await flow.to_list()(test_stream())

    # Should produce overlapping windows of size 3
    assert result == [[0, 1, 2], [1, 2, 3], [2, 3, 4], [3, 4, 5]]


@pytest.mark.asyncio
async def test_window_stream_with_step():
    """Test window_stream function with custom step."""
    # Create a flow that creates windows of size 3 with step 2
    flow: Flow[int, list[int]] = window_stream(3, step=2)

    # Create test input stream
    async def test_stream():
        for i in range(8):
            yield i

    # Execute the flow
    result: list[list[int]] = await flow.to_list()(test_stream())

    # Should produce windows with step 2
    assert result == [[0, 1, 2], [2, 3, 4], [4, 5, 6]]


@pytest.mark.asyncio
async def test_window_stream_insufficient_items():
    """Test window_stream with fewer items than window size."""
    flow: Flow[int, list[int]] = window_stream(5)

    async def test_stream():
        for i in range(3):
            yield i

    result: list[list[int]] = await flow.to_list()(test_stream())
    # Should produce no windows since we don't have enough items
    assert result == []


@pytest.mark.asyncio
async def test_window_stream_empty():
    """Test window_stream with empty stream."""
    flow: Flow[int, list[int]] = window_stream(3)

    async def empty_stream():
        return
        yield  # pragma: no cover

    result: list[list[int]] = await flow.to_list()(empty_stream())
    assert result == []


@pytest.mark.asyncio
async def test_window_stream_exact_size():
    """Test window_stream with exactly window size items."""
    flow: Flow[int, list[int]] = window_stream(3)

    async def test_stream():
        for i in range(3):
            yield i

    result: list[list[int]] = await flow.to_list()(test_stream())
    # Should produce one window
    assert result == [[0, 1, 2]]
