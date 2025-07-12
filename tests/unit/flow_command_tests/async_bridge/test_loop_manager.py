from __future__ import annotations

import asyncio
import threading
from collections.abc import AsyncGenerator
from unittest.mock import AsyncMock, Mock, patch

import pytest

from flow_command.async_bridge.loop_manager import FlowEventLoop
from flow_command.core.exceptions import FlowCommandTimeoutError


class TestFlowEventLoop:
    """Test suite for FlowEventLoop."""

    def test_flow_event_loop_initialization(self) -> None:
        """FlowEventLoop should initialize properly."""
        loop = FlowEventLoop()
        assert loop.loop is not None
        assert loop.thread is not None
        assert loop.thread.is_alive()
        loop.shutdown()

    def test_flow_event_loop_shutdown(self) -> None:
        """FlowEventLoop should shutdown properly."""
        loop = FlowEventLoop()
        original_thread = loop.thread
        loop.shutdown()
        # Give it a moment to shutdown
        original_thread.join(timeout=1.0)
        assert not original_thread.is_alive()

    def test_execute_flow_success(self) -> None:
        """FlowEventLoop.execute_flow should handle successful execution."""
        mock_flow = Mock()
        mock_flow.collect.return_value = AsyncMock(return_value=["result1", "result2"])

        loop = FlowEventLoop()
        try:
            # Create async iterable for input
            async def async_input() -> AsyncGenerator[str, None]:
                return
                yield  # unreachable but makes this an async generator

            result: list[str] = loop.execute_flow(mock_flow, async_input())
            assert result == ["result1", "result2"]
        finally:
            loop.shutdown()

    def test_execute_with_timeout_success(self) -> None:
        """FlowEventLoop.execute_with_timeout should handle successful execution."""

        async def quick_coroutine() -> str:
            return "result"

        loop = FlowEventLoop()
        try:
            result = loop.execute_with_timeout(quick_coroutine(), timeout=1.0)
            assert result == "result"
        finally:
            loop.shutdown()

    def test_execute_with_timeout_timeout(self) -> None:
        """FlowEventLoop.execute_with_timeout should handle timeouts."""

        async def slow_coroutine() -> str:
            await asyncio.sleep(10)  # Long delay
            return "result"

        loop = FlowEventLoop()
        try:
            with pytest.raises(FlowCommandTimeoutError) as exc_info:
                loop.execute_with_timeout(slow_coroutine(), timeout=0.1)
            assert "Flow execution timed out" in str(exc_info.value)
        finally:
            loop.shutdown()

    def test_submit_coroutine(self) -> None:
        """FlowEventLoop.submit should submit coroutines to the event loop."""

        async def test_coroutine() -> int:
            return 42

        loop = FlowEventLoop()
        try:
            future = loop.submit(test_coroutine())
            result = future.result(timeout=1.0)
            assert result == 42
        finally:
            loop.shutdown()

    def test_submit_when_not_running(self) -> None:
        """FlowEventLoop.submit should raise error when not running."""

        async def test_coroutine() -> int:
            return 42

        loop = FlowEventLoop()
        loop.shutdown()

        # Create the coroutine and test exception
        coro = test_coroutine()
        try:
            with pytest.raises(RuntimeError, match="Flow event loop is not running"):
                loop.submit(coro)
        finally:
            # Clean up coroutine to avoid unraisable exception warning
            coro.close()

    def test_is_running_property(self) -> None:
        """FlowEventLoop.is_running should reflect the current state."""
        loop = FlowEventLoop()
        assert loop.is_running is True
        loop.shutdown()
        assert loop.is_running is False

    def test_execute_flow_streaming_success(self) -> None:
        """FlowEventLoop.execute_flow_streaming should handle streaming execution."""
        mock_flow = Mock()
        mock_flow.collect.return_value = AsyncMock(
            return_value=["processed_item1", "processed_item2"]
        )

        loop = FlowEventLoop()
        try:
            result: list[str] = loop.execute_flow_streaming(
                mock_flow, ["item1", "item2"]
            )
            assert result == ["processed_item1", "processed_item2"]
        finally:
            loop.shutdown()

    def test_private_methods_coverage(self) -> None:
        """Test private method coverage for completeness."""
        loop = FlowEventLoop()
        try:
            # Test that private methods work (through public interface)
            assert loop._running is True

            # Test async iterable creation
            async def test_async() -> list[int]:
                async_iter = loop._create_async_iterable([1, 2, 3])
                items = []
                async for item in async_iter:
                    items.append(item)
                return items

            future = loop.submit(test_async())
            result = future.result(timeout=1.0)
            assert result == [1, 2, 3]

        finally:
            loop.shutdown()

    def test_shutdown_methods_coverage(self) -> None:
        """Test shutdown method coverage."""
        loop = FlowEventLoop()

        # Test individual shutdown steps
        assert loop._running is True
        loop._mark_shutdown_started()
        assert loop._running is False

        # Test the rest of shutdown
        loop._stop_event_loop()
        loop._wait_for_shutdown_completion(1.0)
        loop._check_shutdown_success()

        # Verify thread stops
        loop.thread.join(timeout=2.0)
        assert not loop.thread.is_alive()

    def test_convert_to_async_generator_coverage(self) -> None:
        """Test _convert_to_async_generator method for coverage."""
        loop = FlowEventLoop()
        try:
            # Test that the async generator conversion works
            async def test_conversion() -> list[int]:
                async def async_iterable() -> AsyncGenerator[int, None]:
                    for i in range(3):
                        yield i

                async_gen = loop._convert_to_async_generator(async_iterable())
                results = []
                async for item in async_gen:
                    results.append(item)
                return results

            future = loop.submit(test_conversion())
            result = future.result(timeout=1.0)
            assert result == [0, 1, 2]
        finally:
            loop.shutdown()

    def test_shutdown_when_already_shutdown(self) -> None:
        """Test shutdown method when already shutdown (early return path)."""
        loop = FlowEventLoop()
        loop.shutdown()  # First shutdown

        # Second shutdown should return early
        loop.shutdown()  # This should hit the early return on line 102

        assert not loop._running

    def test_stop_event_loop_when_not_running(self) -> None:
        """Test _stop_event_loop when loop is not running."""
        loop = FlowEventLoop()

        # Stop the loop manually first
        loop.loop.call_soon_threadsafe(loop.loop.stop)
        import time

        time.sleep(0.1)  # Give it time to stop

        # Now test the method when loop is not running
        loop._stop_event_loop()  # Should not call call_soon_threadsafe

        loop.shutdown()

    def test_check_shutdown_success_with_alive_thread(self) -> None:
        """Test _check_shutdown_success when thread is still alive."""
        import logging

        loop = FlowEventLoop()

        # Mock the logger to capture warnings
        with patch("flow_command.async_bridge.loop_manager.logger") as mock_logger:
            # Call the method while thread is still alive
            loop._check_shutdown_success()

            # Should have logged a warning
            mock_logger.warning.assert_called_once_with(
                "Flow event loop thread did not shutdown cleanly"
            )

        loop.shutdown()
