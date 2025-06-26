"""Shared test fixtures for Flow tests."""

import pytest
from goldentooth_agent.core.flow import Flow


# Shared async stream generators
async def async_range(n: int):
    """Generate numbers from 0 to n-1 in a stream."""
    for i in range(n):
        yield i


async def async_string_range(n: int):
    """Generate string values in a stream."""
    for i in range(n):
        yield f"item_{i}"


async def async_empty():
    """Generate empty stream."""
    return
    yield  # unreachable


async def async_exception_stream(n: int, fail_at: int = 2):
    """Stream that raises an exception after yielding some values."""
    for i in range(n):
        if i == fail_at:
            raise ValueError(f"Exception at item {i}")
        yield i


# Shared transformation functions
def increment(x: int) -> int:
    return x + 1


def double(x: int) -> int:
    return x * 2


def is_even(x: int) -> bool:
    return x % 2 == 0


def is_positive(x: int) -> bool:
    return x > 0


def square(x: int) -> int:
    return x * x


# Shared Flow fixtures
@pytest.fixture
def increment_flow():
    """Flow that increments integers."""
    return Flow.from_sync_fn(increment)


@pytest.fixture
def double_flow():
    """Flow that doubles integers."""
    return Flow.from_sync_fn(double)


@pytest.fixture
def square_flow():
    """Flow that squares integers."""
    return Flow.from_sync_fn(square)


# Shared test utilities
def assert_items_equal(actual, expected):
    """Assert that two iterables contain the same items, regardless of order."""
    assert set(actual) == set(expected)


def assert_items_in_order(actual, expected):
    """Assert that two iterables contain the same items in the same order."""
    assert list(actual) == list(expected)
