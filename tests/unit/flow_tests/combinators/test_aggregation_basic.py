"""Tests for basic aggregation combinators."""

from typing import AsyncGenerator

import pytest

from flow.combinators.aggregation import (
    batch_stream,
    chunk_stream,
    distinct_stream,
    group_by_stream,
    memoize_stream,
    pairwise_stream,
    scan_stream,
    window_stream,
)
from flow.flow import Flow


@pytest.mark.asyncio
async def test_batch_stream() -> None:
    """Test batch_stream function."""
    flow: Flow[int, list[int]] = batch_stream(3)

    # Create test input stream
    async def test_stream() -> AsyncGenerator[int, None]:
        for i in range(7):
            yield i

    # Execute the flow
    result: list[list[int]] = await flow.to_list()(test_stream())

    # Should batch into groups of 3: [0,1,2], [3,4,5], [6]
    expected = [[0, 1, 2], [3, 4, 5], [6]]
    assert result == expected


@pytest.mark.asyncio
async def test_batch_stream_empty() -> None:
    """Test batch_stream with empty input."""
    flow: Flow[int, list[int]] = batch_stream(3)

    async def empty_stream() -> AsyncGenerator[int, None]:
        return
        yield  # unreachable

    result: list[list[int]] = await flow.to_list()(empty_stream())
    assert result == []


@pytest.mark.asyncio
async def test_batch_stream_exact_size() -> None:
    """Test batch_stream with input that exactly fits batch size."""
    flow: Flow[str, list[str]] = batch_stream(2)

    async def test_stream() -> AsyncGenerator[str, None]:
        yield "a"
        yield "b"
        yield "c"
        yield "d"

    result: list[list[str]] = await flow.to_list()(test_stream())
    expected = [["a", "b"], ["c", "d"]]
    assert result == expected


@pytest.mark.asyncio
async def test_batch_stream_single_item() -> None:
    """Test batch_stream with single item."""
    flow: Flow[int, list[int]] = batch_stream(5)

    async def test_stream() -> AsyncGenerator[int, None]:
        yield 42

    result: list[list[int]] = await flow.to_list()(test_stream())
    assert result == [[42]]


@pytest.mark.asyncio
async def test_chunk_stream() -> None:
    """Test chunk_stream function."""
    flow: Flow[str, list[str]] = chunk_stream(2)

    async def test_stream() -> AsyncGenerator[str, None]:
        for char in "hello":
            yield char

    result: list[list[str]] = await flow.to_list()(test_stream())
    expected = [["h", "e"], ["l", "l"], ["o"]]
    assert result == expected


@pytest.mark.asyncio
async def test_chunk_stream_empty() -> None:
    """Test chunk_stream with empty input."""
    flow: Flow[int, list[int]] = chunk_stream(3)

    async def empty_stream() -> AsyncGenerator[int, None]:
        return
        yield  # unreachable

    result: list[list[int]] = await flow.to_list()(empty_stream())
    assert result == []


@pytest.mark.asyncio
async def test_chunk_stream_exact_size() -> None:
    """Test chunk_stream with input that exactly fits chunk size."""
    flow: Flow[int, list[int]] = chunk_stream(3)

    async def test_stream() -> AsyncGenerator[int, None]:
        for i in range(6):
            yield i

    result: list[list[int]] = await flow.to_list()(test_stream())
    expected = [[0, 1, 2], [3, 4, 5]]
    assert result == expected


@pytest.mark.asyncio
async def test_chunk_stream_single_item() -> None:
    """Test chunk_stream with single item."""
    flow: Flow[str, list[str]] = chunk_stream(10)

    async def test_stream() -> AsyncGenerator[str, None]:
        yield "test"

    result: list[list[str]] = await flow.to_list()(test_stream())
    assert result == [["test"]]


@pytest.mark.asyncio
async def test_window_stream() -> None:
    """Test window_stream function."""
    flow: Flow[int, list[int]] = window_stream(3)

    async def test_stream() -> AsyncGenerator[int, None]:
        for i in range(5):
            yield i

    result: list[list[int]] = await flow.to_list()(test_stream())
    # Sliding window of size 3 with step 1: [0,1,2], [1,2,3], [2,3,4]
    expected = [[0, 1, 2], [1, 2, 3], [2, 3, 4]]
    assert result == expected


@pytest.mark.asyncio
async def test_window_stream_with_step() -> None:
    """Test window_stream with custom step size."""
    flow: Flow[int, list[int]] = window_stream(2, step=2)

    async def test_stream() -> AsyncGenerator[int, None]:
        for i in range(6):
            yield i

    result: list[list[int]] = await flow.to_list()(test_stream())
    # Window of size 2 with step 2: [0,1], [2,3], [4,5]
    expected = [[0, 1], [2, 3], [4, 5]]
    assert result == expected


@pytest.mark.asyncio
async def test_window_stream_insufficient_items() -> None:
    """Test window_stream with fewer items than window size."""
    flow: Flow[str, list[str]] = window_stream(5)

    async def test_stream() -> AsyncGenerator[str, None]:
        yield "a"
        yield "b"

    result: list[list[str]] = await flow.to_list()(test_stream())
    # Not enough items to fill a window
    assert result == []


@pytest.mark.asyncio
async def test_window_stream_empty() -> None:
    """Test window_stream with empty input."""
    flow: Flow[int, list[int]] = window_stream(3)

    async def empty_stream() -> AsyncGenerator[int, None]:
        return
        yield  # unreachable

    result: list[list[int]] = await flow.to_list()(empty_stream())
    assert result == []


@pytest.mark.asyncio
async def test_window_stream_exact_size() -> None:
    """Test window_stream with input exactly matching window size."""
    flow: Flow[int, list[int]] = window_stream(3)

    async def test_stream() -> AsyncGenerator[int, None]:
        for i in range(3):
            yield i

    result: list[list[int]] = await flow.to_list()(test_stream())
    expected = [[0, 1, 2]]
    assert result == expected


@pytest.mark.asyncio
async def test_scan_stream() -> None:
    """Test scan_stream function."""
    flow: Flow[int, int] = scan_stream(lambda acc, x: acc + x, 0)

    async def test_stream() -> AsyncGenerator[int, None]:
        for i in [1, 2, 3, 4]:
            yield i

    result: list[int] = await flow.to_list()(test_stream())
    # Running sum starting with 0: 0, 1, 3, 6, 10
    expected = [0, 1, 3, 6, 10]
    assert result == expected


@pytest.mark.asyncio
async def test_scan_stream_product() -> None:
    """Test scan_stream with multiplication."""
    flow: Flow[int, int] = scan_stream(lambda acc, x: acc * x, 1)

    async def test_stream() -> AsyncGenerator[int, None]:
        for i in [2, 3, 4]:
            yield i

    result: list[int] = await flow.to_list()(test_stream())
    # Running product starting with 1: 1, 2, 6, 24
    expected = [1, 2, 6, 24]
    assert result == expected


@pytest.mark.asyncio
async def test_scan_stream_string_concat() -> None:
    """Test scan_stream with string concatenation."""
    flow: Flow[str, str] = scan_stream(lambda acc, x: acc + x, "")

    async def test_stream() -> AsyncGenerator[str, None]:
        for char in ["a", "b", "c"]:
            yield char

    result: list[str] = await flow.to_list()(test_stream())
    # Running concatenation: "", "a", "ab", "abc"
    expected = ["", "a", "ab", "abc"]
    assert result == expected


@pytest.mark.asyncio
async def test_scan_stream_empty() -> None:
    """Test scan_stream with empty input."""
    flow: Flow[int, int] = scan_stream(lambda acc, x: acc + x, 42)

    async def empty_stream() -> AsyncGenerator[int, None]:
        return
        yield  # unreachable

    result: list[int] = await flow.to_list()(empty_stream())
    # Should still emit initial value
    expected = [42]
    assert result == expected


@pytest.mark.asyncio
async def test_group_by_stream() -> None:
    """Test group_by_stream function."""
    flow: Flow[int, tuple[int, list[int]]] = group_by_stream(lambda x: x % 2)

    async def test_stream() -> AsyncGenerator[int, None]:
        for i in [1, 2, 3, 4, 5, 6]:
            yield i

    result: list[tuple[int, list[int]]] = await flow.to_list()(test_stream())

    # Convert to dict for easier testing
    groups = dict(result)
    assert groups[0] == [2, 4, 6]  # Even numbers
    assert groups[1] == [1, 3, 5]  # Odd numbers


@pytest.mark.asyncio
async def test_group_by_stream_strings() -> None:
    """Test group_by_stream with string length grouping."""
    flow: Flow[str, tuple[int, list[str]]] = group_by_stream(len)

    async def test_stream() -> AsyncGenerator[str, None]:
        for word in ["a", "bb", "ccc", "dd", "e"]:
            yield word

    result: list[tuple[int, list[str]]] = await flow.to_list()(test_stream())

    groups = dict(result)
    assert groups[1] == ["a", "e"]
    assert groups[2] == ["bb", "dd"]
    assert groups[3] == ["ccc"]


@pytest.mark.asyncio
async def test_group_by_stream_empty() -> None:
    """Test group_by_stream with empty input."""
    flow: Flow[int, tuple[str, list[int]]] = group_by_stream(str)

    async def empty_stream() -> AsyncGenerator[int, None]:
        return
        yield  # unreachable

    result: list[tuple[str, list[int]]] = await flow.to_list()(empty_stream())
    assert result == []


@pytest.mark.asyncio
async def test_group_by_stream_single_group() -> None:
    """Test group_by_stream where all items have same key."""
    flow: Flow[int, tuple[str, list[int]]] = group_by_stream(lambda x: "same")

    async def test_stream() -> AsyncGenerator[int, None]:
        for i in [1, 2, 3]:
            yield i

    result: list[tuple[str, list[int]]] = await flow.to_list()(test_stream())
    expected = [("same", [1, 2, 3])]
    assert result == expected


@pytest.mark.asyncio
async def test_distinct_stream() -> None:
    """Test distinct_stream function."""
    flow: Flow[int, int] = distinct_stream()

    async def test_stream() -> AsyncGenerator[int, None]:
        for i in [1, 2, 2, 3, 1, 4, 3]:
            yield i

    result: list[int] = await flow.to_list()(test_stream())
    # Should see each item only once, in order of first appearance
    expected = [1, 2, 3, 4]
    assert result == expected


@pytest.mark.asyncio
async def test_distinct_stream_with_key() -> None:
    """Test distinct_stream with key function."""
    flow: Flow[str, str] = distinct_stream(len)

    async def test_stream() -> AsyncGenerator[str, None]:
        for word in ["a", "bb", "c", "dd", "eee"]:
            yield word

    result: list[str] = await flow.to_list()(test_stream())
    # Should see first occurrence of each length: "a" (len=1), "bb" (len=2), "eee" (len=3)
    expected = ["a", "bb", "eee"]
    assert result == expected


@pytest.mark.asyncio
async def test_distinct_stream_strings() -> None:
    """Test distinct_stream with string values."""
    flow: Flow[str, str] = distinct_stream()

    async def test_stream() -> AsyncGenerator[str, None]:
        for word in ["hello", "world", "hello", "python", "world"]:
            yield word

    result: list[str] = await flow.to_list()(test_stream())
    expected = ["hello", "world", "python"]
    assert result == expected


@pytest.mark.asyncio
async def test_distinct_stream_empty() -> None:
    """Test distinct_stream with empty input."""
    flow: Flow[int, int] = distinct_stream()

    async def empty_stream() -> AsyncGenerator[int, None]:
        return
        yield  # unreachable

    result: list[int] = await flow.to_list()(empty_stream())
    assert result == []


@pytest.mark.asyncio
async def test_distinct_stream_no_duplicates() -> None:
    """Test distinct_stream with no duplicates."""
    flow: Flow[int, int] = distinct_stream()

    async def test_stream() -> AsyncGenerator[int, None]:
        for i in [1, 2, 3, 4]:
            yield i

    result: list[int] = await flow.to_list()(test_stream())
    expected = [1, 2, 3, 4]
    assert result == expected


@pytest.mark.asyncio
async def test_pairwise_stream() -> None:
    """Test pairwise_stream function."""
    flow: Flow[int, tuple[int, int]] = pairwise_stream()

    async def test_stream() -> AsyncGenerator[int, None]:
        for i in [1, 2, 3, 4, 5]:
            yield i

    result: list[tuple[int, int]] = await flow.to_list()(test_stream())
    expected = [(1, 2), (2, 3), (3, 4), (4, 5)]
    assert result == expected


@pytest.mark.asyncio
async def test_pairwise_stream_strings() -> None:
    """Test pairwise_stream with strings."""
    flow: Flow[str, tuple[str, str]] = pairwise_stream()

    async def test_stream() -> AsyncGenerator[str, None]:
        for char in "abc":
            yield char

    result: list[tuple[str, str]] = await flow.to_list()(test_stream())
    expected = [("a", "b"), ("b", "c")]
    assert result == expected


@pytest.mark.asyncio
async def test_pairwise_stream_single_item() -> None:
    """Test pairwise_stream with single item."""
    flow: Flow[int, tuple[int, int]] = pairwise_stream()

    async def test_stream() -> AsyncGenerator[int, None]:
        yield 42

    result: list[tuple[int, int]] = await flow.to_list()(test_stream())
    # No pairs can be formed
    assert result == []


@pytest.mark.asyncio
async def test_pairwise_stream_two_items() -> None:
    """Test pairwise_stream with exactly two items."""
    flow: Flow[str, tuple[str, str]] = pairwise_stream()

    async def test_stream() -> AsyncGenerator[str, None]:
        yield "first"
        yield "second"

    result: list[tuple[str, str]] = await flow.to_list()(test_stream())
    expected = [("first", "second")]
    assert result == expected


@pytest.mark.asyncio
async def test_pairwise_stream_empty() -> None:
    """Test pairwise_stream with empty input."""
    flow: Flow[int, tuple[int, int]] = pairwise_stream()

    async def empty_stream() -> AsyncGenerator[int, None]:
        return
        yield  # unreachable

    result: list[tuple[int, int]] = await flow.to_list()(empty_stream())
    assert result == []


@pytest.mark.asyncio
async def test_memoize_stream() -> None:
    """Test memoize_stream function."""
    # Create a flow that caches items by their modulo 3 value
    flow: Flow[int, int] = memoize_stream(lambda x: x % 3)

    # Create test input stream
    async def test_stream() -> AsyncGenerator[int, None]:
        for i in [1, 4, 7, 2, 5, 8]:  # 1%3=1, 4%3=1, 7%3=1, 2%3=2, 5%3=2, 8%3=2
            yield i

    # Execute the flow
    result: list[int] = await flow.to_list()(test_stream())

    # Should cache: 1%3=1 caches 1, 4%3=1 returns 1, 7%3=1 returns 1,
    #               2%3=2 caches 2, 5%3=2 returns 2, 8%3=2 returns 2
    expected = [1, 1, 1, 2, 2, 2]
    assert result == expected


@pytest.mark.asyncio
async def test_memoize_stream_string_keys() -> None:
    """Test memoize_stream with string keys."""
    flow: Flow[str, str] = memoize_stream(lambda s: s[0])  # Cache by first character

    async def test_stream() -> AsyncGenerator[str, None]:
        for word in ["apple", "banana", "apricot", "berry"]:
            yield word

    result: list[str] = await flow.to_list()(test_stream())
    # "apple" caches with key "a", "banana" caches with key "b",
    # "apricot" returns "apple" (key "a"), "berry" returns "banana" (key "b")
    expected = ["apple", "banana", "apple", "banana"]
    assert result == expected


@pytest.mark.asyncio
async def test_memoize_stream_no_duplicates() -> None:
    """Test memoize_stream with no duplicate keys."""
    flow: Flow[int, int] = memoize_stream(lambda x: x)

    async def test_stream() -> AsyncGenerator[int, None]:
        for i in [1, 2, 3, 4]:
            yield i

    result: list[int] = await flow.to_list()(test_stream())
    # No caching occurs since all keys are unique
    expected = [1, 2, 3, 4]
    assert result == expected


@pytest.mark.asyncio
async def test_memoize_stream_empty() -> None:
    """Test memoize_stream with empty input."""
    flow: Flow[int, int] = memoize_stream(lambda x: x % 2)

    async def empty_stream() -> AsyncGenerator[int, None]:
        return
        yield  # unreachable

    result: list[int] = await flow.to_list()(empty_stream())
    assert result == []


@pytest.mark.asyncio
async def test_memoize_stream_single_item() -> None:
    """Test memoize_stream with single item."""
    flow: Flow[str, str] = memoize_stream(lambda x: len(x))

    async def test_stream() -> AsyncGenerator[str, None]:
        yield "hello"

    result: list[str] = await flow.to_list()(test_stream())
    assert result == ["hello"]
