"""Tests for the maybe_await utility."""

import asyncio

import pytest

from goldentooth_agent.core.util.maybe_await import maybe_await


# Test fixtures - synchronous functions
def sync_function():
    """A simple synchronous function."""
    return "sync_result"


def sync_function_with_args(arg1, arg2, kwarg1=None):
    """A synchronous function that takes arguments."""
    return f"sync: {arg1}, {arg2}, {kwarg1}"


def sync_function_that_raises():
    """A synchronous function that raises an exception."""
    raise ValueError("sync error")


# Test fixtures - asynchronous functions
async def async_function():
    """A simple asynchronous function."""
    return "async_result"


async def async_function_with_args(arg1, arg2, kwarg1=None):
    """An asynchronous function that takes arguments."""
    return f"async: {arg1}, {arg2}, {kwarg1}"


async def async_function_that_raises():
    """An asynchronous function that raises an exception."""
    raise ValueError("async error")


async def async_function_with_delay():
    """An asynchronous function with a delay."""
    await asyncio.sleep(0.01)  # Small delay for testing
    return "delayed_result"


class TestMaybeAwait:
    """Test cases for maybe_await function."""

    @pytest.mark.asyncio
    async def test_sync_function_no_args(self):
        """Test calling a synchronous function with no arguments."""
        result = await maybe_await(sync_function)
        assert result == "sync_result"

    @pytest.mark.asyncio
    async def test_sync_function_with_args(self):
        """Test calling a synchronous function with positional and keyword arguments."""
        result = await maybe_await(
            sync_function_with_args, "arg1", "arg2", kwarg1="kwarg1"
        )
        assert result == "sync: arg1, arg2, kwarg1"

    @pytest.mark.asyncio
    async def test_async_function_no_args(self):
        """Test calling an asynchronous function with no arguments."""
        result = await maybe_await(async_function)
        assert result == "async_result"

    @pytest.mark.asyncio
    async def test_async_function_with_args(self):
        """Test calling an asynchronous function with positional and keyword arguments."""
        result = await maybe_await(
            async_function_with_args, "arg1", "arg2", kwarg1="kwarg1"
        )
        assert result == "async: arg1, arg2, kwarg1"

    @pytest.mark.asyncio
    async def test_async_function_with_delay(self):
        """Test calling an asynchronous function that has a delay."""
        result = await maybe_await(async_function_with_delay)
        assert result == "delayed_result"

    @pytest.mark.asyncio
    async def test_sync_function_exception(self):
        """Test that exceptions from synchronous functions are properly raised."""
        with pytest.raises(ValueError, match="sync error"):
            await maybe_await(sync_function_that_raises)

    @pytest.mark.asyncio
    async def test_async_function_exception(self):
        """Test that exceptions from asynchronous functions are properly raised."""
        with pytest.raises(ValueError, match="async error"):
            await maybe_await(async_function_that_raises)

    @pytest.mark.asyncio
    async def test_non_callable_raises_error(self):
        """Test that passing a non-callable raises ValueError."""
        with pytest.raises(ValueError, match="Expected a callable, got str"):
            await maybe_await("not_a_function")

        with pytest.raises(ValueError, match="Expected a callable, got int"):
            await maybe_await(42)

        with pytest.raises(ValueError, match="Expected a callable, got NoneType"):
            await maybe_await(None)

    @pytest.mark.asyncio
    async def test_lambda_functions(self):
        """Test with lambda functions (both sync and async)."""
        # Synchronous lambda
        sync_lambda = lambda x: x * 2
        result = await maybe_await(sync_lambda, 5)
        assert result == 10

        # Asynchronous lambda that returns a coroutine
        async def async_multiply(x):
            await asyncio.sleep(0.01)
            return x * 3

        async_lambda = lambda x: async_multiply(x)
        result = await maybe_await(async_lambda, 5)
        assert result == 15

    @pytest.mark.asyncio
    async def test_method_calls(self):
        """Test calling methods on objects."""

        class TestClass:
            def sync_method(self, value):
                return f"sync_method: {value}"

            async def async_method(self, value):
                return f"async_method: {value}"

        obj = TestClass()

        # Synchronous method
        result = await maybe_await(obj.sync_method, "test")
        assert result == "sync_method: test"

        # Asynchronous method
        result = await maybe_await(obj.async_method, "test")
        assert result == "async_method: test"

    @pytest.mark.asyncio
    async def test_builtin_functions(self):
        """Test with built-in functions."""
        # Built-in function
        result = await maybe_await(len, [1, 2, 3, 4])
        assert result == 4

        # Built-in function with string
        result = await maybe_await(str.upper, "hello")
        assert result == "HELLO"

    @pytest.mark.asyncio
    async def test_coroutine_detection(self):
        """Test that coroutine detection works correctly."""

        # This should test the core logic of inspecting the result
        def returns_coroutine():
            return async_function()  # Returns a coroutine object

        def returns_regular_value():
            return "regular_value"

        # Should await the coroutine returned by the function
        result = await maybe_await(returns_coroutine)
        assert result == "async_result"

        # Should return the regular value directly
        result = await maybe_await(returns_regular_value)
        assert result == "regular_value"

    @pytest.mark.asyncio
    async def test_empty_args_kwargs(self):
        """Test with explicit empty args and kwargs."""
        result = await maybe_await(sync_function, *[], **{})
        assert result == "sync_result"

        result = await maybe_await(async_function, *[], **{})
        assert result == "async_result"

    @pytest.mark.asyncio
    async def test_mixed_argument_types(self):
        """Test with various argument types."""

        def mixed_args_func(pos_arg, *args, keyword_arg=None, **kwargs):
            return {
                "pos_arg": pos_arg,
                "args": args,
                "keyword_arg": keyword_arg,
                "kwargs": kwargs,
            }

        result = await maybe_await(
            mixed_args_func,
            "position",
            "extra1",
            "extra2",
            keyword_arg="keyword",
            extra_kwarg="extra",
        )

        expected = {
            "pos_arg": "position",
            "args": ("extra1", "extra2"),
            "keyword_arg": "keyword",
            "kwargs": {"extra_kwarg": "extra"},
        }
        assert result == expected
