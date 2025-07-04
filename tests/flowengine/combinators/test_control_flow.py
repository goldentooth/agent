"""Tests for control flow combinators."""

import pytest

from flowengine.combinators.basic import map_stream
from flowengine.combinators.control_flow import if_then_stream


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
