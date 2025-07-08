"""Test the test utility functions."""

from __future__ import annotations

import time
from typing import AsyncGenerator

import pytest

from flowengine.flow import Flow
from tests.flowengine.observability.conftest import (
    assert_performance_within_bounds,
    cleanup_observability,
    create_test_flow,
    generate_test_stream,
)


@pytest.mark.asyncio
async def test_create_test_flow_default() -> None:
    """Test create_test_flow with default parameters."""
    flow = create_test_flow()
    assert flow.name == "test_flow"
    assert isinstance(flow, Flow)
    assert flow.metadata == {}


@pytest.mark.asyncio
async def test_create_test_flow_custom() -> None:
    """Test create_test_flow with custom parameters."""
    flow = create_test_flow(
        name="custom_flow",
        transform_fn=lambda x: x * 2,
        metadata={"type": "test"},
    )
    assert flow.name == "custom_flow"
    assert flow.metadata == {"type": "test"}


@pytest.mark.asyncio
async def test_create_test_flow_execution() -> None:
    """Test create_test_flow execution."""
    flow = create_test_flow(transform_fn=lambda x: x * 3)

    async def test_stream() -> AsyncGenerator[int, None]:
        for i in range(3):
            yield i

    result: list[int] = []
    async for item in flow(test_stream()):
        result.append(item)

    assert result == [0, 3, 6]


@pytest.mark.asyncio
async def test_generate_test_stream_default() -> None:
    """Test generate_test_stream with default parameters."""
    result: list[int] = []
    async for item in generate_test_stream():
        result.append(item)

    assert result == list(range(10))


@pytest.mark.asyncio
async def test_generate_test_stream_custom_items() -> None:
    """Test generate_test_stream with custom items."""
    custom_items = [1, 3, 5, 7]
    result: list[int] = []
    async for item in generate_test_stream(items=custom_items):
        result.append(item)

    assert result == custom_items


@pytest.mark.asyncio
async def test_generate_test_stream_custom_size() -> None:
    """Test generate_test_stream with custom size."""
    result: list[int] = []
    async for item in generate_test_stream(size=5):
        result.append(item)

    assert result == list(range(5))


@pytest.mark.asyncio
async def test_generate_test_stream_with_delay() -> None:
    """Test generate_test_stream with delay."""
    start_time = time.perf_counter()
    result: list[int] = []
    async for item in generate_test_stream(items=[1, 2], delay=0.01):
        result.append(item)

    elapsed = time.perf_counter() - start_time
    assert result == [1, 2]
    assert elapsed >= 0.01  # At least one delay occurred


def test_assert_performance_within_bounds_pass() -> None:
    """Test assert_performance_within_bounds passes for good performance."""
    # Should not raise an exception
    assert_performance_within_bounds(0.5, 1.0)
    assert_performance_within_bounds(1.0, 1.0)
    assert_performance_within_bounds(1.05, 1.0)  # Within tolerance


def test_assert_performance_within_bounds_fail() -> None:
    """Test assert_performance_within_bounds fails for poor performance."""
    with pytest.raises(AssertionError, match="Performance exceeded bounds"):
        assert_performance_within_bounds(2.0, 1.0)


def test_assert_performance_within_bounds_custom_tolerance() -> None:
    """Test assert_performance_within_bounds with custom tolerance."""
    # Should pass with higher tolerance
    assert_performance_within_bounds(1.5, 1.0, tolerance=0.6)

    # Should fail with lower tolerance
    with pytest.raises(AssertionError):
        assert_performance_within_bounds(1.05, 1.0, tolerance=0.01)


def test_cleanup_observability() -> None:
    """Test cleanup_observability utility."""
    # Should not raise an exception
    cleanup_observability()
