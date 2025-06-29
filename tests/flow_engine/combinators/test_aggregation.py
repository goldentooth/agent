"""Tests for aggregation flow combinators."""

import asyncio

import pytest

from goldentooth_agent.flow_engine.combinators.aggregation import (
    batch_stream,
    buffer_stream,
    chunk_stream,
    distinct_stream,
    expand_stream,
    finalize_stream,
    group_by_stream,
    memoize_stream,
    pairwise_stream,
    scan_stream,
    window_stream,
)


async def async_range(n: int, delay: float = 0):
    """Generate an async range with optional delay."""
    for i in range(n):
        if delay > 0:
            await asyncio.sleep(delay)
        yield i


def get_type(x) -> str:
    """Get type name as string."""
    return type(x).__name__


class TestBatchStream:
    """Tests for batch_stream function."""

    @pytest.mark.asyncio
    async def test_batch_basic(self):
        """Test basic batching functionality."""
        batch_flow = batch_stream(3)
        assert "batch(3)" in batch_flow.name

        input_stream = async_range(7)
        result_stream = batch_flow(input_stream)
        values = [item async for item in result_stream]

        assert values == [[0, 1, 2], [3, 4, 5], [6]]

    @pytest.mark.asyncio
    async def test_batch_exact_multiple(self):
        """Test batching when stream size is exact multiple."""
        batch_flow = batch_stream(2)

        input_stream = async_range(6)
        result_stream = batch_flow(input_stream)
        values = [item async for item in result_stream]

        assert values == [[0, 1], [2, 3], [4, 5]]

    @pytest.mark.asyncio
    async def test_batch_empty_stream(self):
        """Test batching empty stream."""
        batch_flow = batch_stream(5)

        async def empty_stream():
            if False:
                yield 0

        result_stream = batch_flow(empty_stream())
        values = [item async for item in result_stream]
        assert values == []

    @pytest.mark.asyncio
    async def test_batch_size_one(self):
        """Test batching with size 1."""
        batch_flow = batch_stream(1)

        input_stream = async_range(3)
        result_stream = batch_flow(input_stream)
        values = [item async for item in result_stream]

        assert values == [[0], [1], [2]]


class TestChunkStream:
    """Tests for chunk_stream function."""

    @pytest.mark.asyncio
    async def test_chunk_basic(self):
        """Test basic chunking functionality."""
        chunk_flow = chunk_stream(4)
        assert "chunk(4)" in chunk_flow.name

        input_stream = async_range(10)
        result_stream = chunk_flow(input_stream)
        values = [item async for item in result_stream]

        assert values == [[0, 1, 2, 3], [4, 5, 6, 7], [8, 9]]

    @pytest.mark.asyncio
    async def test_chunk_single_item(self):
        """Test chunking with single item."""
        chunk_flow = chunk_stream(5)

        async def single_item():
            yield "only"

        result_stream = chunk_flow(single_item())
        values = [item async for item in result_stream]

        assert values == [["only"]]


class TestWindowStream:
    """Tests for window_stream function."""

    @pytest.mark.asyncio
    async def test_window_basic(self):
        """Test basic windowing functionality."""
        window_flow = window_stream(3)
        assert "window(3, step=1)" in window_flow.name

        input_stream = async_range(5)
        result_stream = window_flow(input_stream)
        values = [item async for item in result_stream]

        assert values == [[0, 1, 2], [1, 2, 3], [2, 3, 4]]

    @pytest.mark.asyncio
    async def test_window_with_step(self):
        """Test windowing with custom step."""
        window_flow = window_stream(3, step=2)
        assert "window(3, step=2)" in window_flow.name

        input_stream = async_range(7)
        result_stream = window_flow(input_stream)
        values = [item async for item in result_stream]

        # Windows at positions 0, 2, 4
        assert values == [[0, 1, 2], [2, 3, 4], [4, 5, 6]]

    @pytest.mark.asyncio
    async def test_window_insufficient_items(self):
        """Test windowing with insufficient items."""
        window_flow = window_stream(5)

        input_stream = async_range(3)
        result_stream = window_flow(input_stream)
        values = [item async for item in result_stream]

        assert values == []  # No complete window

    @pytest.mark.asyncio
    async def test_window_step_larger_than_size(self):
        """Test windowing with step larger than window size."""
        window_flow = window_stream(2, step=3)

        input_stream = async_range(8)
        result_stream = window_flow(input_stream)
        values = [item async for item in result_stream]

        # Windows at positions 0, 3, 6
        assert values == [[0, 1], [3, 4], [6, 7]]


class TestScanStream:
    """Tests for scan_stream function."""

    @pytest.mark.asyncio
    async def test_scan_sum(self):
        """Test scan with sum accumulator."""

        def add(acc: int, x: int) -> int:
            return acc + x

        scan_flow = scan_stream(add, 0)
        assert "scan(add, 0)" in scan_flow.name

        input_stream = async_range(5)
        result_stream = scan_flow(input_stream)
        values = [item async for item in result_stream]

        # Running sum: 0, 0+0=0, 0+1=1, 1+2=3, 3+3=6, 6+4=10
        assert values == [0, 0, 1, 3, 6, 10]

    @pytest.mark.asyncio
    async def test_scan_list_accumulator(self):
        """Test scan with list accumulator."""

        def append_to_list(acc: list, x: int) -> list:
            return acc + [x]

        scan_flow = scan_stream(append_to_list, [])

        input_stream = async_range(3)
        result_stream = scan_flow(input_stream)
        values = [item async for item in result_stream]

        assert values == [[], [0], [0, 1], [0, 1, 2]]

    @pytest.mark.asyncio
    async def test_scan_empty_stream(self):
        """Test scan on empty stream."""
        scan_flow = scan_stream(lambda acc, x: acc + x, 10)

        async def empty_stream():
            if False:
                yield 0

        result_stream = scan_flow(empty_stream())
        values = [item async for item in result_stream]

        # Only initial value is emitted
        assert values == [10]


class TestGroupByStream:
    """Tests for group_by_stream function."""

    @pytest.mark.asyncio
    async def test_group_by_basic(self):
        """Test basic grouping functionality."""

        def parity(x: int) -> str:
            return "even" if x % 2 == 0 else "odd"

        group_flow = group_by_stream(parity)
        assert "group_by(parity)" in group_flow.name

        input_stream = async_range(6)
        result_stream = group_flow(input_stream)
        groups = [item async for item in result_stream]

        # Convert to dict for easier testing
        group_dict = dict(groups)
        assert set(group_dict.keys()) == {"even", "odd"}
        assert group_dict["even"] == [0, 2, 4]
        assert group_dict["odd"] == [1, 3, 5]

    @pytest.mark.asyncio
    async def test_group_by_single_group(self):
        """Test grouping when all items belong to one group."""
        group_flow = group_by_stream(lambda x: "all")

        input_stream = async_range(3)
        result_stream = group_flow(input_stream)
        groups = [item async for item in result_stream]

        assert groups == [("all", [0, 1, 2])]

    @pytest.mark.asyncio
    async def test_group_by_empty_stream(self):
        """Test grouping empty stream."""
        group_flow = group_by_stream(str)

        async def empty_stream():
            if False:
                yield 0

        result_stream = group_flow(empty_stream())
        groups = [item async for item in result_stream]
        assert groups == []


class TestDistinctStream:
    """Tests for distinct_stream function."""

    @pytest.mark.asyncio
    async def test_distinct_basic(self):
        """Test basic distinct functionality."""
        distinct_flow = distinct_stream()
        assert distinct_flow.name == "distinct"

        async def duplicates_stream():
            for x in [1, 2, 1, 3, 2, 4, 1]:
                yield x

        result_stream = distinct_flow(duplicates_stream())
        values = [item async for item in result_stream]

        assert values == [1, 2, 3, 4]

    @pytest.mark.asyncio
    async def test_distinct_with_key_function(self):
        """Test distinct with custom key function."""
        # Use absolute value as key
        distinct_flow = distinct_stream(abs)
        assert "distinct(abs)" in distinct_flow.name

        async def signed_stream():
            for x in [1, -1, 2, -2, 3, -3]:
                yield x

        result_stream = distinct_flow(signed_stream())
        values = [item async for item in result_stream]

        # Only first occurrence of each absolute value
        assert values == [1, 2, 3]

    @pytest.mark.asyncio
    async def test_distinct_complex_objects(self):
        """Test distinct with complex objects."""
        distinct_flow = distinct_stream(lambda d: d["id"])

        async def object_stream():
            yield {"id": 1, "name": "A"}
            yield {"id": 2, "name": "B"}
            yield {"id": 1, "name": "C"}  # Duplicate id
            yield {"id": 3, "name": "D"}

        result_stream = distinct_flow(object_stream())
        values = [item async for item in result_stream]

        assert len(values) == 3
        assert values[0]["name"] == "A"
        assert values[1]["name"] == "B"
        assert values[2]["name"] == "D"


class TestPairwiseStream:
    """Tests for pairwise_stream function."""

    @pytest.mark.asyncio
    async def test_pairwise_basic(self):
        """Test basic pairwise functionality."""
        pairwise_flow = pairwise_stream()
        assert pairwise_flow.name == "pairwise"

        input_stream = async_range(4)
        result_stream = pairwise_flow(input_stream)
        values = [item async for item in result_stream]

        assert values == [(0, 1), (1, 2), (2, 3)]

    @pytest.mark.asyncio
    async def test_pairwise_single_item(self):
        """Test pairwise with single item."""
        pairwise_flow = pairwise_stream()

        async def single_stream():
            yield "only"

        result_stream = pairwise_flow(single_stream())
        values = [item async for item in result_stream]

        assert values == []  # No pairs possible

    @pytest.mark.asyncio
    async def test_pairwise_empty_stream(self):
        """Test pairwise on empty stream."""
        pairwise_flow = pairwise_stream()

        async def empty_stream():
            if False:
                yield 0

        result_stream = pairwise_flow(empty_stream())
        values = [item async for item in result_stream]
        assert values == []

    @pytest.mark.asyncio
    async def test_pairwise_with_strings(self):
        """Test pairwise with string values."""
        pairwise_flow = pairwise_stream()

        async def string_stream():
            for s in ["a", "b", "c"]:
                yield s

        input_stream = string_stream()
        result_stream = pairwise_flow(input_stream)
        values = [item async for item in result_stream]

        assert values == [("a", "b"), ("b", "c")]


class TestMemoizeStream:
    """Tests for memoize_stream function."""

    @pytest.mark.asyncio
    async def test_memoize_basic(self):
        """Test basic memoization functionality."""
        call_count = {}

        def expensive_operation(x: int) -> int:
            if x not in call_count:
                call_count[x] = 0
            call_count[x] += 1
            return x * x

        # Use the value itself as the key
        memoize_flow = memoize_stream(lambda x: x)
        assert "memoize(<lambda>)" in memoize_flow.name

        async def repeating_stream():
            for x in [1, 2, 1, 3, 2, 1]:
                yield expensive_operation(x)

        result_stream = memoize_flow(repeating_stream())
        values = [item async for item in result_stream]

        # Values are correct
        assert values == [1, 4, 1, 9, 4, 1]
        # But expensive_operation was only called once per unique input
        assert call_count == {1: 3, 2: 2, 3: 1}

    @pytest.mark.asyncio
    async def test_memoize_custom_key(self):
        """Test memoization with custom key function."""
        # Memoize based on string length
        memoize_flow = memoize_stream(len)

        async def string_stream():
            # Different strings with same length
            for s in ["a", "bb", "cc", "ddd", "ee", "f"]:
                yield s

        result_stream = memoize_flow(string_stream())
        values = [item async for item in result_stream]

        # Only first string of each length is kept
        assert values == ["a", "bb", "bb", "ddd", "bb", "a"]


class TestBufferStream:
    """Tests for buffer_stream function."""

    @pytest.mark.asyncio
    async def test_buffer_basic(self):
        """Test basic buffering functionality."""

        async def trigger_stream():
            # Trigger every 50ms
            for _ in range(3):
                await asyncio.sleep(0.05)
                yield "trigger"

        buffer_flow = buffer_stream(trigger_stream())
        assert buffer_flow.name == "buffer"

        # Items arrive faster than triggers
        result_stream = buffer_flow(async_range(10, delay=0.01))
        buffers = []

        start_time = asyncio.get_event_loop().time()
        async for buffer in result_stream:
            buffers.append(buffer)
            # Stop after reasonable time
            if asyncio.get_event_loop().time() - start_time > 0.2:
                break

        # Should have collected items in buffers
        assert len(buffers) >= 2
        # First buffer should have items
        assert len(buffers[0]) > 0
        # All items should be in order
        all_items = [item for buffer in buffers for item in buffer]
        assert all_items == list(range(len(all_items)))

    @pytest.mark.asyncio
    async def test_buffer_no_trigger(self):
        """Test buffering when trigger never fires."""

        async def never_trigger():
            await asyncio.sleep(1)  # Wait forever
            yield "never"

        buffer_flow = buffer_stream(never_trigger())

        # Send some items
        async def quick_stream():
            for i in range(3):
                yield i

        result_stream = buffer_flow(quick_stream())
        buffers = []

        # Collect with timeout
        start_time = asyncio.get_event_loop().time()
        async for buffer in result_stream:
            buffers.append(buffer)
            if asyncio.get_event_loop().time() - start_time > 0.1:
                break

        # Should eventually emit remaining buffer
        assert len(buffers) == 1
        assert buffers[0] == [0, 1, 2]

    @pytest.mark.asyncio
    async def test_buffer_cleanup_on_completion(self):
        """Test buffer stream cleanup when stream completes with remaining items."""

        async def quick_trigger():
            await asyncio.sleep(0.1)  # Wait long enough for items to accumulate
            yield "trigger"

        buffer_flow = buffer_stream(quick_trigger())

        # Send items that will accumulate before trigger
        async def items_stream():
            for i in range(3):
                yield i
                await asyncio.sleep(0.01)

        result_stream = buffer_flow(items_stream())
        buffers = []

        async for buffer in result_stream:
            buffers.append(buffer)

        # Should have emitted the final buffer with remaining items
        assert len(buffers) >= 1
        # All items should be present
        all_items = [item for buffer in buffers for item in buffer]
        assert all_items == [0, 1, 2]


class TestExpandStream:
    """Tests for expand_stream function."""

    @pytest.mark.asyncio
    async def test_expand_basic(self):
        """Test basic expansion functionality."""

        async def expand_fn(x: int):
            """Expand by yielding x/2 if even."""
            if x % 2 == 0 and x > 0:
                yield x // 2

        expand_flow = expand_stream(expand_fn, max_depth=3)
        assert "expand(expand_fn, depth=3)" in expand_flow.name

        async def start_stream():
            yield 8

        result_stream = expand_flow(start_stream())
        values = [item async for item in result_stream]

        # 8 -> 4 -> 2 -> 1 (stops, odd)
        assert values == [8, 4, 2, 1]

    @pytest.mark.asyncio
    async def test_expand_max_depth(self):
        """Test expansion with max depth limit."""

        async def always_expand(x: int):
            """Always yield x+1."""
            yield x + 1

        expand_flow = expand_stream(always_expand, max_depth=2)

        async def start_stream():
            yield 0

        result_stream = expand_flow(start_stream())
        values = [item async for item in result_stream]

        # 0 -> 1 -> 2 (max depth reached)
        assert values == [0, 1, 2]

    @pytest.mark.asyncio
    async def test_expand_no_expansion(self):
        """Test expansion when nothing expands."""

        async def never_expand(x):
            """Never yield anything."""
            if False:
                yield x

        expand_flow = expand_stream(never_expand, max_depth=5)

        input_stream = async_range(3)
        result_stream = expand_flow(input_stream)
        values = [item async for item in result_stream]

        # Only original items
        assert values == [0, 1, 2]


class TestFinalizeStream:
    """Tests for finalize_stream function."""

    @pytest.mark.asyncio
    async def test_finalize_normal_completion(self):
        """Test finalization on normal completion."""
        finalized = False

        def cleanup():
            nonlocal finalized
            finalized = True

        finalize_flow = finalize_stream(cleanup)
        assert "finalize(cleanup)" in finalize_flow.name

        input_stream = async_range(3)
        result_stream = finalize_flow(input_stream)
        values = [item async for item in result_stream]

        assert values == [0, 1, 2]
        assert finalized

    @pytest.mark.asyncio
    async def test_finalize_with_error(self):
        """Test finalization when error occurs."""
        finalized = False

        def cleanup():
            nonlocal finalized
            finalized = True

        finalize_flow = finalize_stream(cleanup)

        async def failing_stream():
            yield 1
            raise ValueError("Test error")

        with pytest.raises(ValueError):
            result_stream = finalize_flow(failing_stream())
            _ = [item async for item in result_stream]

        # Finalizer should still run
        assert finalized

    @pytest.mark.asyncio
    async def test_finalize_async_function(self):
        """Test finalization with async cleanup function."""
        finalized = False

        async def async_cleanup():
            nonlocal finalized
            await asyncio.sleep(0.001)
            finalized = True

        finalize_flow = finalize_stream(async_cleanup)

        input_stream = async_range(2)
        result_stream = finalize_flow(input_stream)
        values = [item async for item in result_stream]

        assert values == [0, 1]
        assert finalized
