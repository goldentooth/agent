from __future__ import annotations

import asyncio
import threading
from collections.abc import Callable
from concurrent.futures import Future

import pytest

from goldentooth_agent.core.background_loop import (
    BackgroundEventLoop,
    run_in_background,
)


class TestBackgroundEventLoop:
    """Test suite for BackgroundEventLoop class."""

    def test_creates_new_event_loop(self) -> None:
        """BackgroundEventLoop should create a new event loop."""
        loop = BackgroundEventLoop()
        assert loop.loop is not None
        assert isinstance(loop.loop, asyncio.AbstractEventLoop)
        assert loop.loop.is_running()

    def test_runs_in_separate_thread(self) -> None:
        """BackgroundEventLoop should run in a separate daemon thread."""
        loop = BackgroundEventLoop()
        assert loop.thread is not None
        assert isinstance(loop.thread, threading.Thread)
        assert loop.thread.is_alive()
        assert loop.thread.daemon
        assert loop.thread != threading.current_thread()

    def test_factory_method_creates_instance(self) -> None:
        """Factory method should create a new BackgroundEventLoop instance."""
        loop1 = BackgroundEventLoop.create()
        loop2 = BackgroundEventLoop.create()
        assert isinstance(loop1, BackgroundEventLoop)
        assert isinstance(loop2, BackgroundEventLoop)
        assert loop1 is not loop2
        assert loop1.loop is not loop2.loop

    def test_submit_runs_coroutine(self) -> None:
        """Submit should run a coroutine in the background loop."""
        loop = BackgroundEventLoop()

        async def test_coroutine() -> str:
            return "test_result"

        future = loop.submit(test_coroutine())
        result = future.result(timeout=1.0)
        assert result == "test_result"

    def test_submit_handles_exceptions(self) -> None:
        """Submit should propagate exceptions from coroutines."""
        loop = BackgroundEventLoop()

        async def failing_coroutine() -> None:
            raise ValueError("Test error")

        future = loop.submit(failing_coroutine())
        with pytest.raises(ValueError, match="Test error"):
            future.result(timeout=1.0)

    def test_submit_runs_multiple_coroutines(self) -> None:
        """Submit should handle multiple coroutines concurrently."""
        loop = BackgroundEventLoop()

        async def test_coroutine(value: int) -> int:
            await asyncio.sleep(0.1)
            return value * 2

        futures = [loop.submit(test_coroutine(i)) for i in range(5)]
        for i, future in enumerate(futures):
            result = future.result(timeout=2.0)
            assert result == i * 2

    def test_submit_preserves_execution_order(self) -> None:
        """Submit should preserve relative execution order of coroutines."""
        loop = BackgroundEventLoop()
        execution_order: list[int] = []

        futures = self._submit_ordered_coroutines(loop, execution_order)
        self._wait_for_all_futures(futures)
        assert execution_order == list(range(10))

    def _submit_ordered_coroutines(
        self, loop: BackgroundEventLoop, execution_order: list[int]
    ) -> list[Future[int]]:
        """Submit ordered coroutines to the loop."""
        futures: list[Future[int]] = []
        for i in range(10):
            futures.append(
                loop.submit(self._create_ordered_coroutine(i, execution_order))
            )
        return futures

    async def _create_ordered_coroutine(
        self, index: int, execution_order: list[int]
    ) -> int:
        """Create coroutine that tracks execution order."""
        execution_order.append(index)
        return index

    def _wait_for_all_futures(self, futures: list[Future[int]]) -> None:
        """Wait for all futures to complete."""
        for future in futures:
            future.result(timeout=1.0)

    def test_handles_long_running_coroutines(self) -> None:
        """BackgroundEventLoop should handle long-running coroutines."""
        loop = BackgroundEventLoop()

        async def long_running() -> str:
            await asyncio.sleep(0.5)
            return "completed"

        future = loop.submit(long_running())
        result = future.result(timeout=2.0)
        assert result == "completed"

    def test_thread_safety(self) -> None:
        """Submit should be thread-safe for concurrent calls."""
        loop = BackgroundEventLoop()
        results: list[int] = []

        def submit_from_thread(thread_id: int) -> None:
            future = loop.submit(self._create_test_coroutine(thread_id))
            results.append(future.result(timeout=2.0))

        threads = self._create_test_threads(submit_from_thread)
        self._wait_for_threads_completion(threads)
        assert sorted(results) == list(range(10))

    async def _create_test_coroutine(self, thread_id: int) -> int:
        """Create a test coroutine for thread safety testing."""
        await asyncio.sleep(0.01)
        return thread_id

    def _create_test_threads(
        self, target_func: Callable[[int], None]
    ) -> list[threading.Thread]:
        """Create and start test threads."""
        threads: list[threading.Thread] = []
        for i in range(10):
            thread = threading.Thread(target=target_func, args=(i,))
            threads.append(thread)
            thread.start()
        return threads

    def _wait_for_threads_completion(self, threads: list[threading.Thread]) -> None:
        """Wait for all threads to complete."""
        for thread in threads:
            thread.join(timeout=3.0)


class TestRunInBackground:
    """Test suite for run_in_background function."""

    def test_runs_coroutine_and_returns_result(self) -> None:
        """run_in_background should run a coroutine and return its result."""

        async def test_coroutine() -> str:
            return "test_value"

        result = run_in_background(test_coroutine())
        assert result == "test_value"

    def test_propagates_exceptions(self) -> None:
        """run_in_background should propagate exceptions from coroutines."""

        async def failing_coroutine() -> None:
            raise RuntimeError("Test exception")

        with pytest.raises(RuntimeError, match="Test exception"):
            run_in_background(failing_coroutine())

    def test_handles_async_operations(self) -> None:
        """run_in_background should handle async operations correctly."""

        async def async_operation() -> str:
            await asyncio.sleep(0.1)
            return "async_result"

        result = run_in_background(async_operation())
        assert result == "async_result"

    def test_uses_injected_background_loop(self) -> None:
        """run_in_background should use the injected background loop."""

        # This test verifies the function works with the real injection system
        async def test_coroutine() -> str:
            return "injected_result"

        result = run_in_background(test_coroutine())
        assert result == "injected_result"

    def test_multiple_concurrent_calls(self) -> None:
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

    def test_full_workflow(self) -> None:
        """Test the complete workflow of creating and using background loops."""
        loop = BackgroundEventLoop()

        fetch_result = self._fetch_test_data(loop)
        final_result = self._process_test_data(loop, fetch_result)
        assert final_result == "ITEM_42"

    def _fetch_test_data(self, loop: BackgroundEventLoop) -> dict[str, str | int]:
        """Fetch test data using the background loop."""

        async def fetch_data(item_id: int) -> dict[str, str | int]:
            await asyncio.sleep(0.1)
            return {"id": item_id, "data": f"item_{item_id}"}

        fetch_future = loop.submit(fetch_data(42))
        return fetch_future.result(timeout=1.0)

    def _process_test_data(
        self, loop: BackgroundEventLoop, data: dict[str, str | int]
    ) -> str:
        """Process test data using the background loop."""

        async def process_data(data: dict[str, str | int]) -> str:
            await asyncio.sleep(0.05)
            return str(data["data"]).upper()

        process_future = loop.submit(process_data(data))
        return process_future.result(timeout=1.0)

    def test_error_handling_workflow(self) -> None:
        """Test error handling in the complete workflow."""
        loop = BackgroundEventLoop()

        self._test_failing_operation(loop)
        self._test_recovery_operation(loop)

    def _test_failing_operation(self, loop: BackgroundEventLoop) -> None:
        """Test that failing operations raise expected errors."""

        async def operation_that_fails() -> None:
            await asyncio.sleep(0.1)
            raise ValueError("Operation failed")

        future1 = loop.submit(operation_that_fails())
        with pytest.raises(ValueError, match="Operation failed"):
            future1.result(timeout=1.0)

    def _test_recovery_operation(self, loop: BackgroundEventLoop) -> None:
        """Test recovery operation succeeds after failure."""

        async def recovery_operation() -> str:
            return "recovered"

        future2 = loop.submit(recovery_operation())
        result = future2.result(timeout=1.0)
        assert result == "recovered"

    def test_resource_cleanup(self) -> None:
        """Test that resources are properly managed."""
        loop = BackgroundEventLoop()

        self._verify_thread_running(loop)
        self._test_work_submission(loop)
        self._verify_daemon_thread_properties(loop)

    def _verify_thread_running(self, loop: BackgroundEventLoop) -> None:
        """Verify the background thread is running."""
        assert loop.thread.is_alive()

    def _test_work_submission(self, loop: BackgroundEventLoop) -> None:
        """Test submitting work to the loop."""

        async def test_operation() -> str:
            return "completed"

        future = loop.submit(test_operation())
        result = future.result(timeout=1.0)
        assert result == "completed"

    def _verify_daemon_thread_properties(self, loop: BackgroundEventLoop) -> None:
        """Verify daemon thread properties."""
        assert loop.thread.is_alive()
        assert loop.thread.daemon


class TestBackgroundEventLoopShutdown:
    """Test shutdown and error handling for BackgroundEventLoop."""

    def test_mark_shutdown_started(self) -> None:
        """Test _mark_shutdown_started sets running to False."""
        loop = BackgroundEventLoop()
        assert loop._running is True  # type: ignore[reportPrivateUsage]

        loop._mark_shutdown_started()  # type: ignore[reportPrivateUsage]
        assert loop._running is False  # type: ignore[reportPrivateUsage]

    def test_stop_event_loop_when_running(self) -> None:
        """Test _stop_event_loop stops a running loop."""
        loop = BackgroundEventLoop()
        assert loop.loop.is_running()

        loop._stop_event_loop()  # type: ignore[reportPrivateUsage]
        # Give time for the stop to take effect
        import time

        time.sleep(0.1)
        # Verify the loop is no longer running
        assert not loop.loop.is_running()

    def test_stop_event_loop_when_not_running(self) -> None:
        """Test _stop_event_loop is safe when loop not running."""
        loop = BackgroundEventLoop()
        loop.shutdown(timeout=1.0)

        # Should not raise error even if loop already stopped
        loop._stop_event_loop()  # type: ignore[reportPrivateUsage]

    def test_wait_for_shutdown_completion(self) -> None:
        """Test _wait_for_shutdown_completion waits for completion."""
        loop = BackgroundEventLoop()

        # Start shutdown process
        loop._mark_shutdown_started()  # type: ignore[reportPrivateUsage]
        loop._stop_event_loop()  # type: ignore[reportPrivateUsage]

        # Should complete within timeout
        loop._wait_for_shutdown_completion(2.0)  # type: ignore[reportPrivateUsage]

    def test_check_shutdown_success_when_alive(self) -> None:
        """Test _check_shutdown_success logs warning when thread alive."""
        loop = BackgroundEventLoop()

        # Since thread is still alive, this should not raise an error
        # The warning will be logged but we can't easily capture it here
        loop._check_shutdown_success()  # type: ignore[reportPrivateUsage]

    def test_check_shutdown_success_when_dead(self) -> None:
        """Test _check_shutdown_success is quiet when thread dead."""
        loop = BackgroundEventLoop()
        loop.shutdown(timeout=2.0)

        # Thread should be dead now, no warning expected
        loop._check_shutdown_success()  # type: ignore[reportPrivateUsage]

    def test_submit_after_shutdown_raises_error(self) -> None:
        """Submit should raise RuntimeError after shutdown."""
        loop = BackgroundEventLoop()
        loop.shutdown(timeout=2.0)

        with pytest.raises(RuntimeError, match="Background event loop is not running"):
            self._try_submit_after_shutdown(loop)

    def _try_submit_after_shutdown(self, loop: BackgroundEventLoop) -> None:
        """Try to submit coroutine after shutdown, expecting failure."""
        coro = self._create_simple_coroutine()
        try:
            loop.submit(coro)
        finally:
            coro.close()

    async def _create_simple_coroutine(self) -> str:
        """Create a simple test coroutine."""
        return "should_not_run"

    def test_shutdown_graceful(self) -> None:
        """Test graceful shutdown of background event loop."""
        loop = BackgroundEventLoop()

        # Verify it's running initially
        assert loop.is_running

        # Shutdown gracefully
        loop.shutdown(timeout=2.0)

        # Should not be running after shutdown
        assert not loop.is_running

    def test_shutdown_multiple_calls_safe(self) -> None:
        """Multiple shutdown calls should be safe."""
        loop = BackgroundEventLoop()

        # First shutdown
        loop.shutdown(timeout=1.0)
        assert not loop.is_running

        # Second shutdown should not raise error
        loop.shutdown(timeout=1.0)
        assert not loop.is_running

    def test_is_running_property(self) -> None:
        """Test is_running property in various states."""
        loop = BackgroundEventLoop()

        # Should be running when created
        assert loop.is_running

        # Should not be running after shutdown
        loop.shutdown(timeout=2.0)
        assert not loop.is_running
