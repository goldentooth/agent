"""Tests for temporal flow combinators."""

from __future__ import annotations

import asyncio
import time
from typing import AsyncGenerator

import pytest

from flowengine.combinators.temporal import (
    DebounceMode,
    debounce_stream,
    debounce_stream_leading_edge,
    debounce_stream_trailing_edge,
    delay_stream,
    sample_stream,
    throttle_stream,
    timeout_stream,
)
from flowengine.exceptions import FlowTimeoutError
from flowengine.flow import Flow


async def async_range(n: int, delay: float = 0) -> AsyncGenerator[int, None]:
    """Generate an async range with optional delay."""
    for i in range(n):
        if delay > 0:
            await asyncio.sleep(delay)
        yield i


class TestDelayStream:
    """Tests for delay_stream function."""

    @pytest.mark.asyncio
    async def test_delay_basic(self) -> None:
        """Test basic delay functionality."""
        delay_flow: Flow[int, int] = delay_stream(0.01)  # 10ms delay
        assert "delay(0.01)" in delay_flow.name

        start_time = time.time()
        input_stream = async_range(3)
        result_stream = delay_flow(input_stream)
        values: list[int] = []

        async for item in result_stream:
            values.append(item)

        elapsed = time.time() - start_time
        assert values == [0, 1, 2]
        # Should take at least 30ms (3 items * 10ms)
        assert elapsed >= 0.03

    @pytest.mark.asyncio
    async def test_delay_zero(self) -> None:
        """Test delay with zero seconds (no delay)."""
        delay_flow: Flow[int, int] = delay_stream(0)

        start_time = time.time()
        input_stream = async_range(3)
        result_stream = delay_flow(input_stream)
        values: list[int] = [item async for item in result_stream]
        elapsed = time.time() - start_time

        assert values == [0, 1, 2]
        # Should complete almost instantly
        assert elapsed < 0.1

    @pytest.mark.asyncio
    async def test_delay_empty_stream(self) -> None:
        """Test delay on empty stream."""
        delay_flow: Flow[int, int] = delay_stream(0.01)

        async def empty_stream() -> AsyncGenerator[int, None]:
            if False:
                yield 0

        result_stream = delay_flow(empty_stream())
        values: list[int] = [item async for item in result_stream]
        assert values == []


class TestDebounceStream:
    """Tests for debounce_stream function."""

    @pytest.mark.asyncio
    async def test_debounce_basic(self) -> None:
        """Test basic debounce functionality."""
        debounce_flow: Flow[int, int] = debounce_stream(0.05)  # 50ms debounce
        assert "debounce" in debounce_flow.name and "0.05" in debounce_flow.name

        # Stream items quickly - first should be emitted, rest suppressed
        async def fast_stream() -> AsyncGenerator[int, None]:
            for i in range(3):
                yield i
                await asyncio.sleep(
                    0.01
                )  # 10ms between items (faster than 50ms debounce)

        result_stream = debounce_flow(fast_stream())
        values: list[int] = [item async for item in result_stream]

        # Only the first item should be emitted, rest suppressed due to debouncing
        assert values == [0]

    @pytest.mark.asyncio
    async def test_debounce_spaced_items(self) -> None:
        """Test debounce with well-spaced items."""
        debounce_flow: Flow[int, int] = debounce_stream(0.02)  # 20ms debounce

        # Stream items with spacing larger than debounce period
        async def slow_stream() -> AsyncGenerator[int, None]:
            for i in range(3):
                yield i
                await asyncio.sleep(0.05)  # 50ms between items > 20ms debounce

        result_stream = debounce_flow(slow_stream())
        values: list[int] = [item async for item in result_stream]

        # With proper debouncing, all items should be emitted since they are spaced apart
        # Each item is 50ms apart which is > 20ms debounce interval
        assert values == [0, 1, 2]  # All items emitted since properly spaced

    @pytest.mark.asyncio
    async def test_debounce_single_item(self) -> None:
        """Test debounce with single item."""
        debounce_flow: Flow[str, str] = debounce_stream(0.02)

        async def single_item_stream() -> AsyncGenerator[str, None]:
            yield "only"

        result_stream = debounce_flow(single_item_stream())
        values: list[str] = [item async for item in result_stream]
        assert values == ["only"]

    @pytest.mark.asyncio
    async def test_debounce_true_behavior(self) -> None:
        """Test true debouncing behavior - emit first, suppress until interval expires."""
        debounce_flow: Flow[int, int] = debounce_stream(0.03)  # 30ms debounce

        # Stream with bursts separated by quiet periods
        async def burst_stream() -> AsyncGenerator[int, None]:
            # First burst: items arriving quickly
            for i in range(3):
                yield i
                await asyncio.sleep(
                    0.005
                )  # 5ms between items (faster than 30ms debounce)

            # Quiet period (> 30ms)
            await asyncio.sleep(0.05)

            # Second burst
            for i in range(10, 12):
                yield i
                await asyncio.sleep(0.005)  # 5ms between items

        result_stream = debounce_flow(burst_stream())
        values: list[int] = [item async for item in result_stream]

        # Should emit first item from each burst, suppress others
        # First burst: emit 0 (first), suppress 1,2
        # After quiet period: emit 10 (first of second burst), suppress 11
        assert values == [0, 10]  # First item from each burst

    @pytest.mark.asyncio
    async def test_debounce_mode_leading_edge(self) -> None:
        """Test debounce_stream with explicit leading edge mode."""
        debounce_flow: Flow[int, int] = debounce_stream(0.05, DebounceMode.LEADING_EDGE)

        async def fast_stream() -> AsyncGenerator[int, None]:
            for i in range(3):
                yield i
                await asyncio.sleep(0.01)

        values: list[int] = [item async for item in debounce_flow(fast_stream())]
        assert values == [0]  # Leading edge: emit first, suppress rest

    @pytest.mark.asyncio
    async def test_debounce_mode_trailing_edge(self) -> None:
        """Test debounce_stream with trailing edge mode."""
        debounce_flow: Flow[int, int] = debounce_stream(
            0.05, DebounceMode.TRAILING_EDGE
        )

        async def fast_stream() -> AsyncGenerator[int, None]:
            for i in range(3):
                yield i
                await asyncio.sleep(0.01)

        values: list[int] = [item async for item in debounce_flow(fast_stream())]
        assert values == [2]  # Trailing edge: emit last after quiet period

    @pytest.mark.asyncio
    async def test_debounce_specific_functions(self) -> None:
        """Test specific debounce function variants."""
        # Leading edge function
        leading_flow: Flow[int, int] = debounce_stream_leading_edge(0.05)

        async def test_stream() -> AsyncGenerator[int, None]:
            for i in range(3):
                yield i
                await asyncio.sleep(0.01)

        leading_values: list[int] = [item async for item in leading_flow(test_stream())]

        # Trailing edge function
        trailing_flow: Flow[int, int] = debounce_stream_trailing_edge(0.05)
        trailing_values: list[int] = [
            item async for item in trailing_flow(test_stream())
        ]

        assert leading_values == [0]  # First item
        assert trailing_values == [2]  # Last item after quiet period

        # Check function names
        assert "debounce_leading" in leading_flow.name
        assert "debounce_trailing" in trailing_flow.name


class TestThrottleStream:
    """Tests for throttle_stream function."""

    @pytest.mark.asyncio
    async def test_throttle_basic(self) -> None:
        """Test basic throttle functionality."""
        throttle_flow: Flow[int, int] = throttle_stream(20.0)  # 20 items per second max
        assert "throttle(20.0/s)" in throttle_flow.name

        start_time = time.time()
        # Try to send 5 items instantly
        input_stream = async_range(5)
        result_stream = throttle_flow(input_stream)
        values: list[int] = []

        async for item in result_stream:
            values.append(item)

        elapsed = time.time() - start_time
        assert values == [0, 1, 2, 3, 4]
        # Should take at least 200ms (5 items at 20/sec = 0.25 sec)
        assert elapsed >= 0.2

    @pytest.mark.asyncio
    async def test_throttle_slow_input(self) -> None:
        """Test throttle with naturally slow input."""
        throttle_flow: Flow[int, int] = throttle_stream(
            100.0
        )  # 100 items per second max

        # Input is already slow (10 items/sec), so throttle shouldn't affect it
        start_time = time.time()
        input_stream = async_range(3, delay=0.1)
        result_stream = throttle_flow(input_stream)
        values: list[int] = [item async for item in result_stream]
        elapsed = time.time() - start_time

        assert values == [0, 1, 2]
        # Should take about 300ms (natural speed)
        assert 0.25 <= elapsed <= 0.4

    @pytest.mark.asyncio
    async def test_throttle_empty_stream(self) -> None:
        """Test throttle on empty stream."""
        throttle_flow: Flow[int, int] = throttle_stream(10.0)

        async def empty_stream() -> AsyncGenerator[int, None]:
            if False:
                yield 0

        result_stream = throttle_flow(empty_stream())
        values: list[int] = [item async for item in result_stream]
        assert values == []

    @pytest.mark.asyncio
    async def test_throttle_persistence_across_streams(self) -> None:
        """Test that throttle state persists across multiple stream uses."""
        throttle_flow: Flow[int, int] = throttle_stream(10.0)  # 10 items per second

        # First stream
        async def stream1() -> AsyncGenerator[int, None]:
            for i in range(2):
                yield i

        start_time = time.time()
        values1: list[int] = [item async for item in throttle_flow(stream1())]
        time1 = time.time() - start_time

        # Second stream immediately after
        async def stream2() -> AsyncGenerator[int, None]:
            for i in range(2, 4):
                yield i

        start_time = time.time()
        values2: list[int] = [item async for item in throttle_flow(stream2())]
        time2 = time.time() - start_time

        # Verify results
        assert values1 == [0, 1]
        assert values2 == [2, 3]

        # Total time should be ~300ms for 4 items at 10/sec
        total_time = time1 + time2
        assert 0.25 <= total_time <= 0.45  # Allow some timing variance


class TestTimeoutStream:
    """Tests for timeout_stream function."""

    @pytest.mark.asyncio
    async def test_timeout_basic(self) -> None:
        """Test basic timeout functionality."""
        timeout_flow: Flow[int, int] = timeout_stream(0.1)  # 100ms timeout
        assert "timeout(0.1)" in timeout_flow.name

        # Normal processing should work
        input_stream = async_range(3)
        result_stream = timeout_flow(input_stream)
        values: list[int] = [item async for item in result_stream]
        assert values == [0, 1, 2]

    @pytest.mark.asyncio
    async def test_timeout_exceeded(self) -> None:
        """Test timeout when processing takes too long."""
        timeout_flow: Flow[int, int] = timeout_stream(0.01)  # 10ms timeout

        async def slow_stream() -> AsyncGenerator[int, None]:
            yield 1
            await asyncio.sleep(0.02)  # This will trigger timeout
            yield 2

        # The timeout should be triggered when waiting for the second item
        result_stream = timeout_flow(slow_stream())
        values: list[int] = []

        with pytest.raises(FlowTimeoutError):
            async for item in result_stream:
                values.append(item)

        # Should have gotten the first item before timing out
        assert values == [1]

    @pytest.mark.asyncio
    async def test_timeout_empty_stream(self) -> None:
        """Test timeout on empty stream."""
        timeout_flow: Flow[int, int] = timeout_stream(0.1)

        async def empty_stream() -> AsyncGenerator[int, None]:
            if False:
                yield 0

        result_stream = timeout_flow(empty_stream())
        values: list[int] = [item async for item in result_stream]
        assert values == []

    @pytest.mark.asyncio
    async def test_timeout_actual_timeout(self) -> None:
        """Test timeout when actual timeout occurs."""
        timeout_flow: Flow[int, int] = timeout_stream(0.001)  # Very short timeout

        # This should trigger a timeout - slow stream generation
        async def test_stream() -> AsyncGenerator[int, None]:
            await asyncio.sleep(0.01)  # 10ms delay before first item
            yield 1

        # Should timeout before getting any items
        result_stream = timeout_flow(test_stream())

        with pytest.raises(FlowTimeoutError):
            values: list[int] = [item async for item in result_stream]


class TestSampleStream:
    """Tests for sample_stream function."""

    @pytest.mark.asyncio
    async def test_sample_basic(self) -> None:
        """Test basic sampling functionality."""
        sample_flow: Flow[int, int] = sample_stream(0.05)  # Sample every 50ms
        assert "sample(0.05)" in sample_flow.name

        # Generate items continuously
        async def continuous_stream() -> AsyncGenerator[int, None]:
            for i in range(20):
                yield i
                await asyncio.sleep(0.01)  # 10ms between items

        result_stream = sample_flow(continuous_stream())
        values: list[int] = []

        # Collect samples for a limited time
        start_time = time.time()
        async for item in result_stream:
            values.append(item)
            if time.time() - start_time > 0.15:  # Stop after 150ms
                break

        # Should have sampled 2-3 values in 150ms at 50ms intervals
        assert 1 <= len(values) <= 4
        # Values should be increasing
        for i in range(1, len(values)):
            assert values[i] > values[i - 1]

    @pytest.mark.asyncio
    async def test_sample_slow_input(self) -> None:
        """Test sampling with slow input stream."""
        sample_flow: Flow[int, int] = sample_stream(0.02)  # Sample every 20ms

        # Input is slower than sample rate
        async def slow_stream() -> AsyncGenerator[int, None]:
            for i in range(3):
                yield i
                await asyncio.sleep(0.05)  # 50ms between items

        result_stream = sample_flow(slow_stream())
        values: list[int] = []

        # Collect all samples
        start_time = time.time()
        async for item in result_stream:
            values.append(item)
            if time.time() - start_time > 0.2:  # Stop after 200ms
                break

        # Should sample each value as it arrives
        assert len(values) >= 2

    @pytest.mark.asyncio
    async def test_sample_empty_stream(self) -> None:
        """Test sampling empty stream."""
        sample_flow: Flow[int, int] = sample_stream(0.01)

        async def empty_stream() -> AsyncGenerator[int, None]:
            if False:
                yield 0

        result_stream = sample_flow(empty_stream())
        values: list[int] = []

        # Should complete without any samples
        start_time = time.time()
        async for item in result_stream:
            values.append(item)
            if time.time() - start_time > 0.05:
                break

        assert values == []

    @pytest.mark.asyncio
    async def test_sample_single_item(self) -> None:
        """Test sampling with single item."""
        sample_flow: Flow[str, str] = sample_stream(0.05)

        async def single_stream() -> AsyncGenerator[str, None]:
            yield "single"
            # Then complete

        result_stream = sample_flow(single_stream())
        values: list[str] = []

        start_time = time.time()
        async for item in result_stream:
            values.append(item)
            if time.time() - start_time > 0.1:
                break

        # Should sample the single item at least once
        assert "single" in values


class TestSampleAdvanced:
    """Additional tests for sample_stream function."""

    @pytest.mark.asyncio
    async def test_sample_with_transform(self) -> None:
        """Test sample_stream with data transformation."""
        from flowengine.combinators.basic import compose, map_stream
        from flowengine.combinators.temporal import sample_stream

        # Create a pipeline that transforms then samples
        transform_then_sample: Flow[int, int] = compose(
            map_stream(lambda x: x * 10),  # Transform data first
            sample_stream(0.02),  # Then sample every 20ms
        )

        async def fast_stream() -> AsyncGenerator[int, None]:
            for i in range(10):
                yield i
                await asyncio.sleep(0.005)  # 5ms between items

        result_stream = transform_then_sample(fast_stream())
        values: list[int] = []

        start_time = time.time()
        async for item in result_stream:
            values.append(item)
            if time.time() - start_time > 0.1:  # Stop after 100ms
                break

        # Should have sampled some transformed values
        assert len(values) >= 1
        # All values should be multiples of 10
        assert all(v % 10 == 0 for v in values)


class TestTemporalErrorHandling:
    """Error handling tests for temporal combinators."""

    @pytest.mark.asyncio
    async def test_delay_stream_negative_seconds(self) -> None:
        """Test delay_stream with negative seconds."""
        # Should work with negative seconds (effectively no delay)
        delay_flow: Flow[int, int] = delay_stream(-0.1)
        input_stream = async_range(2)
        result_stream = delay_flow(input_stream)
        values: list[int] = [item async for item in result_stream]
        assert values == [0, 1]

    @pytest.mark.asyncio
    async def test_throttle_stream_zero_rate(self) -> None:
        """Test throttle_stream with zero rate."""
        with pytest.raises(ZeroDivisionError):
            throttle_stream(0.0)

    @pytest.mark.asyncio
    async def test_throttle_stream_negative_rate(self) -> None:
        """Test throttle_stream with negative rate."""
        # Negative rate should work (negative interval means no delay)
        throttle_flow: Flow[int, int] = throttle_stream(-1.0)
        input_stream = async_range(2)
        result_stream = throttle_flow(input_stream)
        values: list[int] = [item async for item in result_stream]
        assert values == [0, 1]

    @pytest.mark.asyncio
    async def test_timeout_stream_zero_timeout(self) -> None:
        """Test timeout_stream with zero timeout."""
        timeout_flow: Flow[int, int] = timeout_stream(0.0)

        async def simple_stream() -> AsyncGenerator[int, None]:
            yield 1

        # Should timeout immediately
        with pytest.raises(FlowTimeoutError):
            values: list[int] = [item async for item in timeout_flow(simple_stream())]

    @pytest.mark.asyncio
    async def test_sample_stream_zero_interval(self) -> None:
        """Test sample_stream with zero interval."""
        sample_flow: Flow[int, int] = sample_stream(0.0)

        async def fast_stream() -> AsyncGenerator[int, None]:
            for i in range(3):
                yield i
                await asyncio.sleep(0.001)

        # Should still work but sample very frequently
        result_stream = sample_flow(fast_stream())
        values: list[int] = []

        start_time = time.time()
        async for item in result_stream:
            values.append(item)
            if time.time() - start_time > 0.01:  # Stop after 10ms
                break

        # Should get at least some values
        assert len(values) >= 1
