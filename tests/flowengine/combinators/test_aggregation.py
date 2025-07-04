"""Tests for aggregation combinators."""

from __future__ import annotations

import pytest

from flowengine.combinators.aggregation import (
    batch_stream,
    buffer_stream,
    chunk_stream,
    distinct_stream,
    expand_stream,
    group_by_stream,
    memoize_stream,
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


@pytest.mark.asyncio
async def test_memoize_stream():
    """Test memoize_stream function with repeated keys."""
    # Create a flow that caches items by their modulo 3 value
    flow: Flow[int, int] = memoize_stream(lambda x: x % 3)

    # Create test input stream
    async def test_stream():
        for i in [1, 4, 7, 2, 5, 8]:  # 1%3=1, 4%3=1, 7%3=1, 2%3=2, 5%3=2, 8%3=2
            yield i

    # Execute the flow
    result: list[int] = await flow.to_list()(test_stream())

    # Should cache: 1 (key 1), 4 (key 1 cached -> yield 1), 7 (key 1 cached -> yield 1),
    #               2 (key 2), 5 (key 2 cached -> yield 2), 8 (key 2 cached -> yield 2)
    assert result == [1, 1, 1, 2, 2, 2]


@pytest.mark.asyncio
async def test_memoize_stream_string_keys():
    """Test memoize_stream function with string key extraction."""
    # Create a flow that caches items by their first letter
    flow: Flow[str, str] = memoize_stream(lambda x: x[0])

    # Create test input stream
    async def test_stream():
        for word in ["apple", "apricot", "banana", "berry", "avocado"]:
            yield word

    # Execute the flow
    result: list[str] = await flow.to_list()(test_stream())

    # Should cache: apple (key 'a'), apricot (key 'a' cached -> yield apple),
    #               banana (key 'b'), berry (key 'b' cached -> yield banana),
    #               avocado (key 'a' cached -> yield apple)
    assert result == ["apple", "apple", "banana", "banana", "apple"]


@pytest.mark.asyncio
async def test_memoize_stream_no_duplicates():
    """Test memoize_stream with all unique keys."""
    flow: Flow[int, int] = memoize_stream(lambda x: x)

    async def test_stream():
        for i in range(5):
            yield i

    result: list[int] = await flow.to_list()(test_stream())
    # All unique keys, so all items pass through unchanged
    assert result == [0, 1, 2, 3, 4]


@pytest.mark.asyncio
async def test_memoize_stream_empty():
    """Test memoize_stream with empty stream."""
    flow: Flow[int, int] = memoize_stream(lambda x: x)

    async def empty_stream():
        return
        yield  # pragma: no cover

    result: list[int] = await flow.to_list()(empty_stream())
    assert result == []


@pytest.mark.asyncio
async def test_memoize_stream_single_item():
    """Test memoize_stream with single item."""
    flow: Flow[str, str] = memoize_stream(lambda x: len(x))

    async def test_stream():
        yield "hello"

    result: list[str] = await flow.to_list()(test_stream())
    assert result == ["hello"]


@pytest.mark.asyncio
async def test_buffer_stream_basic():
    """Test buffer_stream with basic trigger functionality."""
    import asyncio

    # Create trigger stream that fires twice
    async def trigger_stream():
        await asyncio.sleep(0.01)  # Let some items accumulate
        yield "trigger1"
        await asyncio.sleep(0.01)  # Let more items accumulate
        yield "trigger2"

    flow: Flow[int, list[int]] = buffer_stream(trigger_stream())

    # Create test input stream
    async def test_stream():
        for i in range(6):
            yield i
            await asyncio.sleep(0.005)  # Small delay between items

    # Execute the flow
    result: list[list[int]] = await flow.to_list()(test_stream())

    # Should have 2-3 buffers depending on timing
    assert len(result) >= 2
    assert len(result) <= 3

    # All items should be present across all buffers
    all_items = [item for buffer in result for item in buffer]
    assert set(all_items) == set(range(6))


@pytest.mark.asyncio
async def test_buffer_stream_immediate_trigger():
    """Test buffer_stream with immediate trigger."""

    # Create trigger that fires immediately
    async def trigger_stream():
        yield "trigger"

    flow: Flow[str, list[str]] = buffer_stream(trigger_stream())

    # Create test input stream
    async def test_stream():
        yield "a"
        yield "b"

    # Execute the flow
    result: list[list[str]] = await flow.to_list()(test_stream())

    # Should have at least one buffer with remaining items
    assert len(result) >= 1
    all_items = [item for buffer in result for item in buffer]
    assert set(all_items) == {"a", "b"}


@pytest.mark.asyncio
async def test_buffer_stream_no_trigger():
    """Test buffer_stream with no triggers."""

    # Create empty trigger stream
    async def trigger_stream():
        return
        yield  # unreachable

    flow: Flow[int, list[int]] = buffer_stream(trigger_stream())

    # Create test input stream
    async def test_stream():
        for i in range(3):
            yield i

    # Execute the flow
    result: list[list[int]] = await flow.to_list()(test_stream())

    # Should have one buffer with all remaining items
    assert len(result) == 1
    assert result[0] == [0, 1, 2]


@pytest.mark.asyncio
async def test_buffer_stream_empty_input():
    """Test buffer_stream with empty input stream."""

    # Create trigger stream
    async def trigger_stream():
        yield "trigger"

    flow: Flow[int, list[int]] = buffer_stream(trigger_stream())

    # Create empty input stream
    async def test_stream():
        return
        yield  # unreachable

    # Execute the flow
    result: list[list[int]] = await flow.to_list()(test_stream())

    # Should have no buffers for empty input
    assert result == []


@pytest.mark.asyncio
async def test_expand_stream_basic():
    """Test expand_stream with basic recursive expansion."""

    # Create expander that generates children for each item
    async def expander(x: int):
        if x < 10:  # Only expand small numbers
            yield x * 2
            yield x * 2 + 1

    flow: Flow[int, int] = expand_stream(expander, max_depth=2)

    # Create test input stream
    async def test_stream():
        yield 1

    # Execute the flow
    result: list[int] = await flow.to_list()(test_stream())

    # Should expand: 1 -> [2, 3] -> [4, 5, 6, 7]
    # Total: [1, 2, 3, 4, 5, 6, 7]
    expected = {1, 2, 3, 4, 5, 6, 7}
    assert set(result) == expected


@pytest.mark.asyncio
async def test_expand_stream_max_depth():
    """Test expand_stream respects max_depth limit."""

    # Create expander that always generates two children
    async def expander(x: str):
        yield f"{x}a"
        yield f"{x}b"

    flow: Flow[str, str] = expand_stream(expander, max_depth=1)

    # Create test input stream
    async def test_stream():
        yield "x"

    # Execute the flow
    result: list[str] = await flow.to_list()(test_stream())

    # Should expand only 1 level: "x" -> ["xa", "xb"]
    # Total: ["x", "xa", "xb"]
    expected = {"x", "xa", "xb"}
    assert set(result) == expected


@pytest.mark.asyncio
async def test_expand_stream_no_expansion():
    """Test expand_stream when expander returns no items."""

    # Create expander that never expands
    async def expander(x: int):
        # No yields - empty expansion
        return
        yield  # unreachable

    flow: Flow[int, int] = expand_stream(expander)

    # Create test input stream
    async def test_stream():
        for i in range(3):
            yield i

    # Execute the flow
    result: list[int] = await flow.to_list()(test_stream())

    # Should just return original items
    assert result == [0, 1, 2]


@pytest.mark.asyncio
async def test_expand_stream_empty_input():
    """Test expand_stream with empty input stream."""

    # Create simple expander
    async def expander(x: int):
        yield x + 1

    flow: Flow[int, int] = expand_stream(expander)

    # Create empty input stream
    async def test_stream():
        return
        yield  # unreachable

    # Execute the flow
    result: list[int] = await flow.to_list()(test_stream())

    # Should return empty result
    assert result == []


@pytest.mark.asyncio
async def test_expand_stream_zero_depth():
    """Test expand_stream with max_depth=0."""

    # Create expander that would generate children
    async def expander(x: int):
        yield x * 10

    flow: Flow[int, int] = expand_stream(expander, max_depth=0)

    # Create test input stream
    async def test_stream():
        yield 1
        yield 2

    # Execute the flow
    result: list[int] = await flow.to_list()(test_stream())

    # Should not expand at all, just return original items
    assert result == [1, 2]


@pytest.mark.asyncio
async def test_expand_stream_multiple_inputs():
    """Test expand_stream with multiple input items."""

    # Create expander that generates one child per item
    async def expander(x: str):
        yield f"{x}_child"

    flow: Flow[str, str] = expand_stream(expander, max_depth=1)

    # Create test input stream
    async def test_stream():
        yield "a"
        yield "b"

    # Execute the flow
    result: list[str] = await flow.to_list()(test_stream())

    # Should expand: "a" -> "a_child", "b" -> "b_child"
    # Total: ["a", "b", "a_child", "b_child"]
    expected = {"a", "b", "a_child", "b_child"}
    assert set(result) == expected


@pytest.mark.asyncio
async def test_expand_stream_complex_expansion():
    """Test expand_stream with complex expansion logic."""

    # Create expander that generates factorial-like expansion
    async def expander(x: int):
        if x > 1:
            for i in range(2, x):
                yield i

    flow: Flow[int, int] = expand_stream(expander, max_depth=3)

    # Create test input stream
    async def test_stream():
        yield 5

    # Execute the flow
    result: list[int] = await flow.to_list()(test_stream())

    # Should include 5 and all its recursive expansions
    assert 5 in result
    assert 2 in result
    assert 3 in result
    assert 4 in result
