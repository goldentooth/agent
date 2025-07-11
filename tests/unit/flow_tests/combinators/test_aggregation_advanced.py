"""Tests for advanced aggregation combinators."""

from typing import AsyncGenerator

import pytest

from flow.combinators.aggregation import buffer_stream, expand_stream, finalize_stream
from flow.flow import Flow


@pytest.mark.asyncio
async def test_buffer_stream_basic() -> None:
    """Test buffer_stream with basic trigger functionality."""
    import asyncio

    # Create trigger stream that fires twice
    async def trigger_stream() -> AsyncGenerator[str, None]:
        await asyncio.sleep(0.01)  # Let some items accumulate
        yield "trigger1"
        await asyncio.sleep(0.01)  # Let more items accumulate
        yield "trigger2"

    flow: Flow[int, list[int]] = buffer_stream(trigger_stream())

    # Create test input stream
    async def test_stream() -> AsyncGenerator[int, None]:
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
async def test_buffer_stream_immediate_trigger() -> None:
    """Test buffer_stream with immediate trigger."""

    # Create trigger that fires immediately
    async def trigger_stream() -> AsyncGenerator[str, None]:
        yield "trigger"

    flow: Flow[str, list[str]] = buffer_stream(trigger_stream())

    # Create test input stream
    async def test_stream() -> AsyncGenerator[str, None]:
        yield "a"
        yield "b"

    # Execute the flow
    result: list[list[str]] = await flow.to_list()(test_stream())

    # Should have at least one buffer with remaining items
    assert len(result) >= 1
    all_items = [item for buffer in result for item in buffer]
    assert set(all_items) == {"a", "b"}


@pytest.mark.asyncio
async def test_buffer_stream_no_trigger() -> None:
    """Test buffer_stream with no triggers."""

    # Create empty trigger stream
    async def trigger_stream() -> AsyncGenerator[int, None]:
        return
        yield  # unreachable

    flow: Flow[int, list[int]] = buffer_stream(trigger_stream())

    # Create test input stream
    async def test_stream() -> AsyncGenerator[int, None]:
        for i in range(3):
            yield i

    # Execute the flow
    result: list[list[int]] = await flow.to_list()(test_stream())

    # Should have one buffer with all remaining items
    assert len(result) == 1
    assert result[0] == [0, 1, 2]


@pytest.mark.asyncio
async def test_buffer_stream_empty_input() -> None:
    """Test buffer_stream with empty input stream."""

    # Create trigger stream
    async def trigger_stream() -> AsyncGenerator[str, None]:
        yield "trigger"

    flow: Flow[int, list[int]] = buffer_stream(trigger_stream())

    # Create empty input stream
    async def test_stream() -> AsyncGenerator[int, None]:
        return
        yield  # unreachable

    # Execute the flow
    result: list[list[int]] = await flow.to_list()(test_stream())

    # Should have no buffers for empty input
    assert result == []


@pytest.mark.asyncio
async def test_expand_stream_basic() -> None:
    """Test expand_stream with basic recursive expansion."""

    # Create expander that generates children for each item
    async def expander(x: int) -> AsyncGenerator[int, None]:
        if x < 10:  # Only expand small numbers
            yield x * 2
            yield x * 2 + 1

    flow: Flow[int, int] = expand_stream(expander, max_depth=2)

    # Create test input stream
    async def test_stream() -> AsyncGenerator[int, None]:
        yield 1

    # Execute the flow
    result: list[int] = await flow.to_list()(test_stream())

    # Should expand: 1 -> [2, 3] -> [4, 5, 6, 7]
    # Total: [1, 2, 3, 4, 5, 6, 7]
    expected = {1, 2, 3, 4, 5, 6, 7}
    assert set(result) == expected


@pytest.mark.asyncio
async def test_expand_stream_max_depth() -> None:
    """Test expand_stream respects max_depth limit."""

    # Create expander that always generates two children
    async def expander(x: str) -> AsyncGenerator[str, None]:
        yield f"{x}a"
        yield f"{x}b"

    flow: Flow[str, str] = expand_stream(expander, max_depth=1)

    # Create test input stream
    async def test_stream() -> AsyncGenerator[str, None]:
        yield "x"

    # Execute the flow
    result: list[str] = await flow.to_list()(test_stream())

    # Should expand only 1 level: "x" -> ["xa", "xb"]
    # Total: ["x", "xa", "xb"]
    expected = {"x", "xa", "xb"}
    assert set(result) == expected


@pytest.mark.asyncio
async def test_expand_stream_no_expansion() -> None:
    """Test expand_stream when expander returns no items."""

    # Create expander that never expands
    async def expander(x: int) -> AsyncGenerator[int, None]:
        # No yields - empty expansion
        return
        yield  # unreachable

    flow: Flow[int, int] = expand_stream(expander)

    # Create test input stream
    async def test_stream() -> AsyncGenerator[int, None]:
        for i in range(3):
            yield i

    # Execute the flow
    result: list[int] = await flow.to_list()(test_stream())

    # Should just return original items
    assert result == [0, 1, 2]


@pytest.mark.asyncio
async def test_expand_stream_empty_input() -> None:
    """Test expand_stream with empty input stream."""

    # Create simple expander
    async def expander(x: int) -> AsyncGenerator[int, None]:
        yield x + 1

    flow: Flow[int, int] = expand_stream(expander)

    # Create empty input stream
    async def test_stream() -> AsyncGenerator[int, None]:
        return
        yield  # unreachable

    # Execute the flow
    result: list[int] = await flow.to_list()(test_stream())

    # Should return empty result
    assert result == []


@pytest.mark.asyncio
async def test_expand_stream_zero_depth() -> None:
    """Test expand_stream with max_depth=0."""

    # Create expander that would generate children
    async def expander(x: int) -> AsyncGenerator[int, None]:
        yield x * 10

    flow: Flow[int, int] = expand_stream(expander, max_depth=0)

    # Create test input stream
    async def test_stream() -> AsyncGenerator[int, None]:
        yield 1
        yield 2

    # Execute the flow
    result: list[int] = await flow.to_list()(test_stream())

    # Should not expand at all, just return original items
    assert result == [1, 2]


@pytest.mark.asyncio
async def test_expand_stream_multiple_inputs() -> None:
    """Test expand_stream with multiple input items."""

    # Create expander that generates one child per item
    async def expander(x: str) -> AsyncGenerator[str, None]:
        yield f"{x}_child"

    flow: Flow[str, str] = expand_stream(expander, max_depth=1)

    # Create test input stream
    async def test_stream() -> AsyncGenerator[str, None]:
        yield "a"
        yield "b"

    # Execute the flow
    result: list[str] = await flow.to_list()(test_stream())

    # Should expand: "a" -> "a_child", "b" -> "b_child"
    # Total: ["a", "b", "a_child", "b_child"]
    expected = {"a", "b", "a_child", "b_child"}
    assert set(result) == expected


@pytest.mark.asyncio
async def test_expand_stream_complex_expansion() -> None:
    """Test expand_stream with complex expansion logic."""

    # Create expander that generates factorial-like expansion
    async def expander(x: int) -> AsyncGenerator[int, None]:
        if x > 1:
            for i in range(2, x):
                yield i

    flow: Flow[int, int] = expand_stream(expander, max_depth=3)

    # Create test input stream
    async def test_stream() -> AsyncGenerator[int, None]:
        yield 5

    # Execute the flow
    result: list[int] = await flow.to_list()(test_stream())

    # Should include 5 and all its recursive expansions
    assert 5 in result
    assert 2 in result
    assert 3 in result
    assert 4 in result


@pytest.mark.asyncio
async def test_finalize_stream_sync_finalizer() -> None:
    """Test finalize_stream with synchronous finalizer function."""
    call_count = 0

    def finalizer() -> None:
        nonlocal call_count
        call_count += 1

    flow: Flow[int, int] = finalize_stream(finalizer)

    # Create test input stream
    async def test_stream() -> AsyncGenerator[int, None]:
        for i in range(3):
            yield i

    # Execute the flow
    result: list[int] = await flow.to_list()(test_stream())

    # Should pass through all items
    assert result == [0, 1, 2]
    # Finalizer should be called once
    assert call_count == 1


@pytest.mark.asyncio
async def test_finalize_stream_async_finalizer() -> None:
    """Test finalize_stream with asynchronous finalizer function."""
    call_count = 0

    async def finalizer() -> None:
        nonlocal call_count
        call_count += 1

    flow: Flow[str, str] = finalize_stream(finalizer)

    # Create test input stream
    async def test_stream() -> AsyncGenerator[str, None]:
        yield "a"
        yield "b"

    # Execute the flow
    result: list[str] = await flow.to_list()(test_stream())

    # Should pass through all items
    assert result == ["a", "b"]
    # Finalizer should be called once
    assert call_count == 1


@pytest.mark.asyncio
async def test_finalize_stream_empty_input() -> None:
    """Test finalize_stream with empty input stream."""
    call_count = 0

    def finalizer() -> None:
        nonlocal call_count
        call_count += 1

    flow: Flow[int, int] = finalize_stream(finalizer)

    # Create empty input stream
    async def test_stream() -> AsyncGenerator[int, None]:
        return
        yield  # unreachable

    # Execute the flow
    result: list[int] = await flow.to_list()(test_stream())

    # Should return empty result
    assert result == []
    # Finalizer should still be called
    assert call_count == 1


@pytest.mark.asyncio
async def test_finalize_stream_with_exception() -> None:
    """Test finalize_stream still calls finalizer when stream raises exception."""
    call_count = 0

    def finalizer() -> None:
        nonlocal call_count
        call_count += 1

    flow: Flow[int, int] = finalize_stream(finalizer)

    # Create stream that raises exception
    async def test_stream() -> AsyncGenerator[int, None]:
        yield 1
        yield 2
        raise ValueError("Test exception")

    # Execute the flow and expect exception
    with pytest.raises(ValueError, match="Test exception"):
        await flow.to_list()(test_stream())

    # Finalizer should still be called even with exception
    assert call_count == 1


@pytest.mark.asyncio
async def test_finalize_stream_multiple_calls() -> None:
    """Test finalize_stream finalizer is called for each flow execution."""
    call_count = 0

    def finalizer() -> None:
        nonlocal call_count
        call_count += 1

    flow: Flow[int, int] = finalize_stream(finalizer)

    # Create test input stream
    async def test_stream() -> AsyncGenerator[int, None]:
        yield 1

    # Execute the flow multiple times
    for _ in range(3):
        result: list[int] = await flow.to_list()(test_stream())
        assert result == [1]

    # Finalizer should be called once per execution
    assert call_count == 3


@pytest.mark.asyncio
async def test_finalize_stream_finalizer_with_side_effects() -> None:
    """Test finalize_stream finalizer can perform side effects."""
    cleanup_items: list[str] = []

    def finalizer() -> None:
        cleanup_items.append("cleaned_up")

    flow: Flow[str, str] = finalize_stream(finalizer)

    # Create test input stream
    async def test_stream() -> AsyncGenerator[str, None]:
        yield "item1"
        yield "item2"

    # Execute the flow
    result: list[str] = await flow.to_list()(test_stream())

    # Should pass through all items
    assert result == ["item1", "item2"]
    # Side effects should have occurred
    assert cleanup_items == ["cleaned_up"]


@pytest.mark.asyncio
async def test_finalize_stream_async_finalizer_with_delay() -> None:
    """Test finalize_stream with async finalizer that has delay."""
    import asyncio

    call_times: list[str] = []

    async def finalizer() -> None:
        await asyncio.sleep(0.01)  # Small delay
        call_times.append("finalized")

    flow: Flow[int, int] = finalize_stream(finalizer)

    # Create test input stream
    async def test_stream() -> AsyncGenerator[int, None]:
        yield 1
        yield 2

    # Execute the flow
    start_time = asyncio.get_event_loop().time()
    result: list[int] = await flow.to_list()(test_stream())
    end_time = asyncio.get_event_loop().time()

    # Should pass through all items
    assert result == [1, 2]
    # Finalizer should be called
    assert call_times == ["finalized"]
    # Should have taken at least the delay time
    assert end_time - start_time >= 0.01
