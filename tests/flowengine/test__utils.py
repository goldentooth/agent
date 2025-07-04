"""Tests for flowengine internal utilities."""

import asyncio

import pytest

from flowengine._utils import maybe_await


class TestMaybeAwait:
    """Tests for maybe_await function."""

    @pytest.mark.asyncio
    async def test_sync_function(self):
        """Test maybe_await with sync function."""

        def sync_func(x: int) -> int:
            return x * 2

        result = await maybe_await(sync_func, 5)
        assert result == 10

    @pytest.mark.asyncio
    async def test_async_function(self):
        """Test maybe_await with async function."""

        async def async_func(x: int) -> int:
            await asyncio.sleep(0.001)
            return x * 3

        result = await maybe_await(async_func, 4)
        assert result == 12

    @pytest.mark.asyncio
    async def test_with_kwargs(self):
        """Test maybe_await with keyword arguments."""

        def func_with_kwargs(x: int, multiplier: int = 2) -> int:
            return x * multiplier

        result = await maybe_await(func_with_kwargs, 5, multiplier=3)
        assert result == 15

    @pytest.mark.asyncio
    async def test_non_callable_raises_error(self):
        """Test maybe_await with non-callable raises ValueError."""
        with pytest.raises(ValueError, match="Expected a callable"):
            await maybe_await("not a function")  # type: ignore[arg-type]
