from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator
from typing import TypeVar

import pytest

from goldentooth_agent.core.background_loop import (
    async_flow,
    schedule_flow,
    timeout_async_flow,
)
from goldentooth_agent.flow_engine import Flow

T = TypeVar("T")


async def list_to_stream(items: list[T]) -> AsyncIterator[T]:
    """Convert a list to an async stream."""
    for item in items:
        yield item


def flow_from_list(items: list[T]) -> Flow[None, T]:
    """Create a flow that yields items from a list."""
    return Flow.from_iterable(items)


async def empty_stream() -> AsyncIterator[None]:
    """Create an empty async stream."""
    return
    yield  # unreachable, but makes this an async generator


class TestBackgroundLoopFlowIntegration:
    """Test suite for background_loop Flow integration."""

    @pytest.mark.asyncio
    async def test_async_flow_basic(self):
        """async_flow should run coroutines in the background loop."""

        async def double_value(x: int) -> int:
            await asyncio.sleep(0.01)
            return x * 2

        flow = flow_from_list([1, 2, 3, 4, 5])
        processed = flow >> async_flow(double_value)
        result = [item async for item in processed(empty_stream())]

        assert result == [2, 4, 6, 8, 10]

    @pytest.mark.asyncio
    async def test_async_flow_with_exceptions(self):
        """async_flow should propagate exceptions."""

        async def failing_operation(x: int) -> int:
            if x == 3:
                raise ValueError("Three is not allowed")
            return x

        flow = flow_from_list([1, 2, 3, 4, 5])
        processed = flow >> async_flow(failing_operation)

        with pytest.raises(ValueError, match="Three is not allowed"):
            [item async for item in processed(empty_stream())]

    @pytest.mark.asyncio
    async def test_schedule_flow(self):
        """schedule_flow should delay items."""
        import time

        start_time = time.time()
        flow = flow_from_list([1, 2, 3])
        processed = flow >> schedule_flow(0.1)
        result = [item async for item in processed(empty_stream())]
        end_time = time.time()

        assert result == [1, 2, 3]
        assert end_time - start_time >= 0.3  # At least 3 * 0.1 seconds

    @pytest.mark.asyncio
    async def test_timeout_async_flow_success(self):
        """timeout_async_flow should return results within timeout."""

        async def quick_operation(x: int) -> int:
            await asyncio.sleep(0.01)
            return x * 2

        flow = flow_from_list([1, 2, 3])
        processed = flow >> timeout_async_flow(quick_operation, 1.0)
        result = [item async for item in processed(empty_stream())]

        assert result == [2, 4, 6]

    @pytest.mark.asyncio
    async def test_timeout_async_flow_timeout(self):
        """timeout_async_flow should handle timeouts."""

        async def slow_operation(x: int) -> int:
            await asyncio.sleep(0.5)
            return x * 2

        flow = flow_from_list([1, 2, 3])
        processed = flow >> timeout_async_flow(slow_operation, 0.1, default_value=0)
        result = [item async for item in processed(empty_stream())]

        assert result == [0, 0, 0]

    @pytest.mark.asyncio
    async def test_timeout_async_flow_skip_on_timeout(self):
        """timeout_async_flow should skip items on timeout when no default."""

        async def mixed_operation(x: int) -> int:
            if x == 2:
                await asyncio.sleep(0.5)
            else:
                await asyncio.sleep(0.01)
            return x * 2

        flow = flow_from_list([1, 2, 3])
        processed = flow >> timeout_async_flow(mixed_operation, 0.1)
        result = [item async for item in processed(empty_stream())]

        assert result == [2, 6]  # 2 is skipped due to timeout
