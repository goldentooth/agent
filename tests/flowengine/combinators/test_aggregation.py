"""Tests for aggregation combinators."""

from __future__ import annotations

import pytest

from flowengine.combinators.aggregation import (
    batch_stream,
    chunk_stream,
    distinct_stream,
    group_by_stream,
    pairwise_stream,
    scan_stream,
    window_stream,
)
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


@pytest.mark.asyncio
async def test_scan_stream():
    """Test scan_stream function with sum accumulation."""
    # Create a flow that performs running sum
    flow: Flow[int, int] = scan_stream(lambda acc, x: acc + x, 0)

    # Create test input stream
    async def test_stream():
        for i in range(1, 5):  # 1, 2, 3, 4
            yield i

    # Execute the flow
    result: list[int] = await flow.to_list()(test_stream())

    # Should produce running sums: [0, 1, 3, 6, 10]
    assert result == [0, 1, 3, 6, 10]


@pytest.mark.asyncio
async def test_scan_stream_product():
    """Test scan_stream function with product accumulation."""
    # Create a flow that performs running product
    flow: Flow[int, int] = scan_stream(lambda acc, x: acc * x, 1)

    # Create test input stream
    async def test_stream():
        for i in range(1, 5):  # 1, 2, 3, 4
            yield i

    # Execute the flow
    result: list[int] = await flow.to_list()(test_stream())

    # Should produce running products: [1, 1, 2, 6, 24]
    assert result == [1, 1, 2, 6, 24]


@pytest.mark.asyncio
async def test_scan_stream_string_concat():
    """Test scan_stream function with string concatenation."""
    # Create a flow that performs running string concatenation
    flow: Flow[str, str] = scan_stream(lambda acc, x: acc + x, "")

    # Create test input stream
    async def test_stream():
        for letter in ["a", "b", "c"]:
            yield letter

    # Execute the flow
    result: list[str] = await flow.to_list()(test_stream())

    # Should produce running concatenations: ["", "a", "ab", "abc"]
    assert result == ["", "a", "ab", "abc"]


@pytest.mark.asyncio
async def test_scan_stream_empty():
    """Test scan_stream with empty stream."""
    flow: Flow[int, int] = scan_stream(lambda acc, x: acc + x, 42)

    async def empty_stream():
        return
        yield  # pragma: no cover

    result: list[int] = await flow.to_list()(empty_stream())
    # Should only contain initial value
    assert result == [42]


@pytest.mark.asyncio
async def test_group_by_stream():
    """Test group_by_stream function with modulo grouping."""
    # Create a flow that groups numbers by their remainder when divided by 3
    flow: Flow[int, tuple[int, list[int]]] = group_by_stream(lambda x: x % 3)

    # Create test input stream
    async def test_stream():
        for i in range(9):  # 0, 1, 2, 3, 4, 5, 6, 7, 8
            yield i

    # Execute the flow
    result: list[tuple[int, list[int]]] = await flow.to_list()(test_stream())

    # Convert to dict for easier testing (order may vary)
    result_dict = dict(result)
    assert result_dict == {0: [0, 3, 6], 1: [1, 4, 7], 2: [2, 5, 8]}


@pytest.mark.asyncio
async def test_group_by_stream_strings():
    """Test group_by_stream function with string length grouping."""
    # Create a flow that groups strings by their length
    flow: Flow[str, tuple[int, list[str]]] = group_by_stream(len)

    # Create test input stream
    async def test_stream():
        for word in ["a", "bb", "ccc", "dd", "e", "fff"]:
            yield word

    # Execute the flow
    result: list[tuple[int, list[str]]] = await flow.to_list()(test_stream())

    # Convert to dict for easier testing
    result_dict = dict(result)
    assert result_dict == {1: ["a", "e"], 2: ["bb", "dd"], 3: ["ccc", "fff"]}


@pytest.mark.asyncio
async def test_group_by_stream_empty():
    """Test group_by_stream with empty stream."""
    flow: Flow[int, tuple[int, list[int]]] = group_by_stream(lambda x: x % 2)

    async def empty_stream():
        return
        yield  # pragma: no cover

    result: list[tuple[int, list[int]]] = await flow.to_list()(empty_stream())
    assert result == []


@pytest.mark.asyncio
async def test_group_by_stream_single_group():
    """Test group_by_stream where all items belong to same group."""
    flow: Flow[int, tuple[str, list[int]]] = group_by_stream(lambda x: "same")

    async def test_stream():
        for i in range(3):
            yield i

    result: list[tuple[str, list[int]]] = await flow.to_list()(test_stream())
    assert result == [("same", [0, 1, 2])]


@pytest.mark.asyncio
async def test_distinct_stream():
    """Test distinct_stream function without key function."""
    # Create a flow that filters out duplicate items
    flow: Flow[int, int] = distinct_stream()

    # Create test input stream with duplicates
    async def test_stream():
        for i in [1, 2, 3, 2, 4, 1, 5, 3]:
            yield i

    # Execute the flow
    result: list[int] = await flow.to_list()(test_stream())

    # Should produce only distinct items in order of first appearance
    assert result == [1, 2, 3, 4, 5]


@pytest.mark.asyncio
async def test_distinct_stream_with_key():
    """Test distinct_stream function with key function."""
    # Create a flow that filters duplicates by absolute value
    flow: Flow[int, int] = distinct_stream(key_fn=abs)

    # Create test input stream
    async def test_stream():
        for i in [1, -1, 2, -2, 3, 1, -3]:
            yield i

    # Execute the flow
    result: list[int] = await flow.to_list()(test_stream())

    # Should keep first occurrence by absolute value
    assert result == [1, 2, 3]


@pytest.mark.asyncio
async def test_distinct_stream_strings():
    """Test distinct_stream function with strings by length."""
    # Create a flow that filters duplicates by string length
    flow: Flow[str, str] = distinct_stream(key_fn=len)

    # Create test input stream
    async def test_stream():
        for word in ["a", "bb", "c", "dd", "eee", "f"]:
            yield word

    # Execute the flow
    result: list[str] = await flow.to_list()(test_stream())

    # Should keep first occurrence of each length
    assert result == ["a", "bb", "eee"]


@pytest.mark.asyncio
async def test_distinct_stream_empty():
    """Test distinct_stream with empty stream."""
    flow: Flow[int, int] = distinct_stream()

    async def empty_stream():
        return
        yield  # pragma: no cover

    result: list[int] = await flow.to_list()(empty_stream())
    assert result == []


@pytest.mark.asyncio
async def test_distinct_stream_no_duplicates():
    """Test distinct_stream with no duplicates."""
    flow: Flow[int, int] = distinct_stream()

    async def test_stream():
        for i in range(5):
            yield i

    result: list[int] = await flow.to_list()(test_stream())
    # Should return all items since no duplicates
    assert result == [0, 1, 2, 3, 4]


@pytest.mark.asyncio
async def test_pairwise_stream():
    """Test pairwise_stream function."""
    # Create a flow that emits consecutive pairs
    flow: Flow[int, tuple[int, int]] = pairwise_stream()

    # Create test input stream
    async def test_stream():
        for i in range(5):  # 0, 1, 2, 3, 4
            yield i

    # Execute the flow
    result: list[tuple[int, int]] = await flow.to_list()(test_stream())

    # Should produce consecutive pairs
    assert result == [(0, 1), (1, 2), (2, 3), (3, 4)]


@pytest.mark.asyncio
async def test_pairwise_stream_strings():
    """Test pairwise_stream function with strings."""
    flow: Flow[str, tuple[str, str]] = pairwise_stream()

    # Create test input stream
    async def test_stream():
        for letter in ["a", "b", "c", "d"]:
            yield letter

    # Execute the flow
    result: list[tuple[str, str]] = await flow.to_list()(test_stream())

    # Should produce consecutive string pairs
    assert result == [("a", "b"), ("b", "c"), ("c", "d")]


@pytest.mark.asyncio
async def test_pairwise_stream_single_item():
    """Test pairwise_stream with single item."""
    flow: Flow[int, tuple[int, int]] = pairwise_stream()

    async def test_stream():
        yield 42

    result: list[tuple[int, int]] = await flow.to_list()(test_stream())
    # Should produce no pairs since only one item
    assert result == []


@pytest.mark.asyncio
async def test_pairwise_stream_two_items():
    """Test pairwise_stream with exactly two items."""
    flow: Flow[int, tuple[int, int]] = pairwise_stream()

    async def test_stream():
        yield 1
        yield 2

    result: list[tuple[int, int]] = await flow.to_list()(test_stream())
    # Should produce one pair
    assert result == [(1, 2)]


@pytest.mark.asyncio
async def test_pairwise_stream_empty():
    """Test pairwise_stream with empty stream."""
    flow: Flow[int, tuple[int, int]] = pairwise_stream()

    async def empty_stream():
        return
        yield  # pragma: no cover

    result: list[tuple[int, int]] = await flow.to_list()(empty_stream())
    assert result == []
