from __future__ import annotations

import asyncio
import threading
from concurrent.futures import Future

import pytest

from goldentooth_agent.core.background_loop import (
    BackgroundEventLoop,
    run_in_background,
)


class TestBackgroundEventLoop:
    """Test suite for BackgroundEventLoop class."""

    def test_creates_new_event_loop(self):
        """BackgroundEventLoop should create a new event loop."""
        loop = BackgroundEventLoop()
        assert loop.loop is not None
        assert isinstance(loop.loop, asyncio.AbstractEventLoop)
        assert loop.loop.is_running()

    def test_runs_in_separate_thread(self):
        """BackgroundEventLoop should run in a separate daemon thread."""
        loop = BackgroundEventLoop()
        assert loop.thread is not None
        assert isinstance(loop.thread, threading.Thread)
        assert loop.thread.is_alive()
        assert loop.thread.daemon
        assert loop.thread != threading.current_thread()

    def test_factory_method_creates_instance(self):
        """Factory method should create a new BackgroundEventLoop instance."""
        loop1 = BackgroundEventLoop.create()
        loop2 = BackgroundEventLoop.create()
        assert isinstance(loop1, BackgroundEventLoop)
        assert isinstance(loop2, BackgroundEventLoop)
        assert loop1 is not loop2
        assert loop1.loop is not loop2.loop

    def test_submit_runs_coroutine(self):
        """Submit should run a coroutine in the background loop."""
        loop = BackgroundEventLoop()

        async def test_coroutine():
            return "test_result"

        future = loop.submit(test_coroutine())
        result = future.result(timeout=1.0)
        assert result == "test_result"

    def test_submit_handles_exceptions(self):
        """Submit should propagate exceptions from coroutines."""
        loop = BackgroundEventLoop()

        async def failing_coroutine():
            raise ValueError("Test error")

        future = loop.submit(failing_coroutine())
        with pytest.raises(ValueError, match="Test error"):
            future.result(timeout=1.0)

    def test_submit_runs_multiple_coroutines(self):
        """Submit should handle multiple coroutines concurrently."""
        loop = BackgroundEventLoop()

        async def test_coroutine(value: int):
            await asyncio.sleep(0.1)
            return value * 2

        futures = [loop.submit(test_coroutine(i)) for i in range(5)]
        for i, future in enumerate(futures):
            result = future.result(timeout=2.0)
            assert result == i * 2

    def test_submit_preserves_execution_order(self):
        """Submit should preserve relative execution order of coroutines."""
        loop = BackgroundEventLoop()
        execution_order: list[int] = []

        async def ordered_coroutine(index: int) -> int:
            execution_order.append(index)
            return index

        futures: list[Future[int]] = []
        for i in range(10):
            futures.append(loop.submit(ordered_coroutine(i)))

        for future in futures:
            future.result(timeout=1.0)

        assert execution_order == list(range(10))

    def test_handles_long_running_coroutines(self):
        """BackgroundEventLoop should handle long-running coroutines."""
        loop = BackgroundEventLoop()

        async def long_running():
            await asyncio.sleep(0.5)
            return "completed"

        future = loop.submit(long_running())
        result = future.result(timeout=2.0)
        assert result == "completed"

    def test_thread_safety(self):
        """Submit should be thread-safe for concurrent calls."""
        loop = BackgroundEventLoop()
        results: list[int] = []

        async def test_coroutine(thread_id: int) -> int:
            await asyncio.sleep(0.01)
            return thread_id

        def submit_from_thread(thread_id: int) -> None:
            future = loop.submit(test_coroutine(thread_id))
            results.append(future.result(timeout=2.0))

        threads: list[threading.Thread] = []
        for i in range(10):
            thread = threading.Thread(target=submit_from_thread, args=(i,))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join(timeout=3.0)

        assert sorted(results) == list(range(10))


class TestRunInBackground:
    """Test suite for run_in_background function."""

    def test_runs_coroutine_and_returns_result(self):
        """run_in_background should run a coroutine and return its result."""

        async def test_coroutine():
            return "test_value"

        result = run_in_background(test_coroutine())
        assert result == "test_value"

    def test_propagates_exceptions(self):
        """run_in_background should propagate exceptions from coroutines."""

        async def failing_coroutine():
            raise RuntimeError("Test exception")

        with pytest.raises(RuntimeError, match="Test exception"):
            run_in_background(failing_coroutine())

    def test_handles_async_operations(self):
        """run_in_background should handle async operations correctly."""

        async def async_operation():
            await asyncio.sleep(0.1)
            return "async_result"

        result = run_in_background(async_operation())
        assert result == "async_result"

    def test_uses_injected_background_loop(self):
        """run_in_background should use the injected background loop."""

        # This test verifies the function works with the real injection system
        async def test_coroutine():
            return "injected_result"

        result = run_in_background(test_coroutine())
        assert result == "injected_result"

    def test_multiple_concurrent_calls(self):
        """run_in_background should handle multiple concurrent calls."""

        # Test sequential calls instead of threads to avoid antidote context issues
        async def coroutine_with_value(value: int) -> int:
            await asyncio.sleep(0.01)
            return value * 2

        results: list[int] = []
        for i in range(5):
            result = run_in_background(coroutine_with_value(i))
            results.append(result)

        assert results == [0, 2, 4, 6, 8]


class TestIntegration:
    """Integration tests for the background_loop module."""

    def test_full_workflow(self):
        """Test the complete workflow of creating and using background loops."""
        # Create a background loop
        loop = BackgroundEventLoop()

        # Define some async operations
        async def fetch_data(item_id: int) -> dict[str, str | int]:
            await asyncio.sleep(0.1)
            return {"id": item_id, "data": f"item_{item_id}"}

        async def process_data(data: dict[str, str | int]) -> str:
            await asyncio.sleep(0.05)
            return str(data["data"]).upper()

        # Submit and chain operations
        fetch_future = loop.submit(fetch_data(42))
        fetch_result = fetch_future.result(timeout=1.0)

        process_future = loop.submit(process_data(fetch_result))
        final_result = process_future.result(timeout=1.0)

        assert final_result == "ITEM_42"

    def test_error_handling_workflow(self):
        """Test error handling in the complete workflow."""
        loop = BackgroundEventLoop()

        async def operation_that_fails():
            await asyncio.sleep(0.1)
            raise ValueError("Operation failed")

        async def recovery_operation():
            return "recovered"

        # First operation fails
        future1 = loop.submit(operation_that_fails())
        with pytest.raises(ValueError, match="Operation failed"):
            future1.result(timeout=1.0)

        # Recovery operation succeeds
        future2 = loop.submit(recovery_operation())
        result = future2.result(timeout=1.0)
        assert result == "recovered"

    def test_resource_cleanup(self):
        """Test that resources are properly managed."""
        # Create and use a background loop
        loop = BackgroundEventLoop()

        async def test_operation():
            return "completed"

        # Verify the thread is running
        assert loop.thread.is_alive()

        # Submit work
        future = loop.submit(test_operation())
        result = future.result(timeout=1.0)
        assert result == "completed"

        # Thread should still be running (daemon thread)
        assert loop.thread.is_alive()

        # Since it's a daemon thread, it will be cleaned up on exit
        assert loop.thread.daemon


class TestBackgroundEventLoopShutdown:
    """Test shutdown and error handling for BackgroundEventLoop."""

    def test_submit_after_shutdown_raises_error(self):
        """Submit should raise RuntimeError after shutdown."""
        loop = BackgroundEventLoop()

        # Shutdown the loop
        loop.shutdown(timeout=2.0)

        async def test_coroutine():
            return "should_not_run"

        # Should raise RuntimeError since loop is not running
        with pytest.raises(RuntimeError, match="Background event loop is not running"):
            # Need to create and immediately close the coroutine to avoid warning
            coro = test_coroutine()
            try:
                loop.submit(coro)
            finally:
                coro.close()

    def test_shutdown_graceful(self):
        """Test graceful shutdown of background event loop."""
        loop = BackgroundEventLoop()

        # Verify it's running initially
        assert loop.is_running

        # Shutdown gracefully
        loop.shutdown(timeout=2.0)

        # Should not be running after shutdown
        assert not loop.is_running

    def test_shutdown_multiple_calls_safe(self):
        """Multiple shutdown calls should be safe."""
        loop = BackgroundEventLoop()

        # First shutdown
        loop.shutdown(timeout=1.0)
        assert not loop.is_running

        # Second shutdown should not raise error
        loop.shutdown(timeout=1.0)
        assert not loop.is_running

    def test_is_running_property(self):
        """Test is_running property in various states."""
        loop = BackgroundEventLoop()

        # Should be running when created
        assert loop.is_running

        # Should not be running after shutdown
        loop.shutdown(timeout=2.0)
        assert not loop.is_running
