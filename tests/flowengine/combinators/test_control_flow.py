"""Tests for control flow combinators."""

import asyncio

import pytest

from flowengine.combinators.basic import map_stream
from flowengine.combinators.control_flow import (
    if_then_stream,
    recover_stream,
    retry_stream,
)
from flowengine.exceptions import FlowExecutionError


# Helper functions
def increment(x: int) -> int:
    """Increment a number by 1."""
    return x + 1


def double(x: int) -> int:
    """Double a number."""
    return x * 2


def is_even(x: int) -> bool:
    """Check if a number is even."""
    return x % 2 == 0


async def async_range(n: int):
    """Generate an async range of integers."""
    for i in range(n):
        yield i


class TestIfThenStream:
    """Tests for if_then_stream function."""

    @pytest.mark.asyncio
    async def test_if_then_basic(self):
        """Test basic if-then functionality."""
        increment_flow = map_stream(increment)
        double_flow = map_stream(double)
        if_then_flow = if_then_stream(is_even, increment_flow, double_flow)

        assert "if_then(is_even, map(increment), map(double))" in if_then_flow.name

        input_stream = async_range(4)  # [0, 1, 2, 3]
        result_stream = if_then_flow(input_stream)
        values = [item async for item in result_stream]
        # 0 (even): 0+1=1, 1 (odd): 1*2=2, 2 (even): 2+1=3, 3 (odd): 3*2=6
        assert values == [1, 2, 3, 6]

    @pytest.mark.asyncio
    async def test_if_then_no_else(self):
        """Test if-then without else clause."""
        increment_flow = map_stream(increment)
        if_then_flow = if_then_stream(is_even, increment_flow)

        assert "if_then(is_even, map(increment))" in if_then_flow.name

        input_stream = async_range(5)  # [0, 1, 2, 3, 4]
        result_stream = if_then_flow(input_stream)
        values = [item async for item in result_stream]
        # Only even numbers are processed: 0->1, 2->3, 4->5
        assert values == [1, 3, 5]


class TestRetryStream:
    """Tests for retry_stream function."""

    @pytest.mark.asyncio
    async def test_retry_success_first_try(self):
        """Test retry when first attempt succeeds."""
        attempt_count = 0

        def count_attempts(x: int) -> int:
            nonlocal attempt_count
            attempt_count += 1
            return x * 2

        process_flow = map_stream(count_attempts)
        retry_flow = retry_stream(3, process_flow)

        assert "retry(3, map(count_attempts))" in retry_flow.name

        input_stream = async_range(2)
        result_stream = retry_flow(input_stream)
        values = [item async for item in result_stream]

        assert values == [0, 2]
        assert attempt_count == 2  # One per item, no retries

    @pytest.mark.asyncio
    async def test_retry_with_eventual_success(self):
        """Test retry with failures then success."""
        attempts = {}

        def flaky_operation(x: int) -> int:
            if x not in attempts:
                attempts[x] = 0
            attempts[x] += 1

            # Fail first 2 attempts for each item
            if attempts[x] < 3:
                raise ValueError(f"Attempt {attempts[x]} failed")
            return x * 2

        process_flow = map_stream(flaky_operation)
        retry_flow = retry_stream(3, process_flow)

        input_stream = async_range(2)
        result_stream = retry_flow(input_stream)
        values = [item async for item in result_stream]

        assert values == [0, 2]
        assert attempts == {0: 3, 1: 3}  # 3 attempts each

    @pytest.mark.asyncio
    async def test_retry_all_attempts_fail(self):
        """Test retry when all attempts fail."""

        def always_fail(x: int) -> int:
            raise ValueError("Always fails")

        process_flow = map_stream(always_fail)
        retry_flow = retry_stream(2, process_flow)

        input_stream = async_range(1)
        result_stream = retry_flow(input_stream)

        with pytest.raises(FlowExecutionError) as exc_info:
            _ = [item async for item in result_stream]

        assert "Failed after 2 retries" in str(exc_info.value)
        assert "Always fails" in str(exc_info.value)


class TestRecoverStream:
    """Tests for recover_stream function."""

    @pytest.mark.asyncio
    async def test_recover_basic(self):
        """Test basic recovery functionality."""

        async def handler(error: Exception, item: int) -> int:
            return -1  # Return -1 for any error

        recover_flow = recover_stream(handler)
        assert "recover(handler)" in recover_flow.name

        async def failing_stream():
            yield 1
            raise ValueError("Test error")

        result_stream = recover_flow(failing_stream())
        values = [item async for item in result_stream]

        # First item passes through, second triggers recovery
        assert values == [1, -1]
