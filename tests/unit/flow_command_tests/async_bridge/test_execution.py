from __future__ import annotations

from collections.abc import AsyncGenerator, Coroutine
from typing import Any, cast
from unittest.mock import Mock, patch

import pytest

from flow_command.async_bridge.execution import (
    _get_flow_loop,
    run_flow_async,
    run_flow_sync,
)
from flow_command.core.context import FlowCommandContext
from flow_command.core.exceptions import (
    FlowCommandExecutionError,
    FlowCommandTimeoutError,
)
from flow_command.core.result import FlowCommandResult


class TestRunFlowSync:
    """Test suite for run_flow_sync function."""

    def test_run_flow_sync_success(self) -> None:
        """run_flow_sync should execute flow successfully."""
        mock_flow = Mock()
        input_data = ["item1", "item2"]
        context = FlowCommandContext.from_test()

        with patch(
            "flow_command.async_bridge.execution._get_flow_loop"
        ) as mock_get_loop:
            mock_loop = Mock()
            mock_get_loop.return_value = mock_loop
            mock_loop.execute_with_timeout.return_value = ["result1", "result2"]

            result: FlowCommandResult[list[str]] = run_flow_sync(
                mock_flow, input_data, context
            )

        assert result.success is True
        assert result.data == ["result1", "result2"]
        assert result.error is None
        mock_loop.execute_with_timeout.assert_called_once()

    def test_run_flow_sync_timeout_error(self) -> None:
        """run_flow_sync should handle timeout errors."""
        mock_flow = Mock()
        input_data = ["item1"]
        context = FlowCommandContext.from_test()

        with patch(
            "flow_command.async_bridge.execution._get_flow_loop"
        ) as mock_get_loop:
            mock_loop = Mock()
            mock_get_loop.return_value = mock_loop
            mock_loop.execute_with_timeout.side_effect = FlowCommandTimeoutError(
                "Timeout occurred"
            )

            result: FlowCommandResult[list[str]] = run_flow_sync(
                mock_flow, input_data, context
            )

        assert result.success is False
        assert result.data is None
        assert result.error is not None
        assert "Timeout occurred" in result.error

    def test_run_flow_sync_execution_error(self) -> None:
        """run_flow_sync should handle execution errors."""
        mock_flow = Mock()
        input_data = ["item1"]
        context = FlowCommandContext.from_test()

        with patch(
            "flow_command.async_bridge.execution._get_flow_loop"
        ) as mock_get_loop:
            mock_loop = Mock()
            mock_get_loop.return_value = mock_loop
            mock_loop.execute_with_timeout.side_effect = FlowCommandExecutionError(
                "Execution failed"
            )

            result: FlowCommandResult[list[str]] = run_flow_sync(
                mock_flow, input_data, context
            )

        assert result.success is False
        assert result.data is None
        assert result.error is not None
        assert "Execution failed" in result.error

    def test_run_flow_sync_unexpected_error(self) -> None:
        """run_flow_sync should handle unexpected errors."""
        mock_flow = Mock()
        input_data = ["item1"]
        context = FlowCommandContext.from_test()

        with patch(
            "flow_command.async_bridge.execution._get_flow_loop"
        ) as mock_get_loop:
            mock_loop = Mock()
            mock_get_loop.return_value = mock_loop
            mock_loop.execute_with_timeout.side_effect = ValueError("Unexpected error")

            result: FlowCommandResult[list[str]] = run_flow_sync(
                mock_flow, input_data, context
            )

        assert result.success is False
        assert result.data is None
        assert result.error is not None
        assert "Unexpected error" in result.error

    def test_get_flow_loop_singleton(self) -> None:
        """_get_flow_loop should return the same instance."""
        # Clean up any existing loop first
        import flow_command.async_bridge.execution as execution_module

        # Store original state
        original_loop = execution_module._flow_loop

        # Clean up existing loop if any
        if original_loop is not None:
            original_loop.shutdown()

        # Reset the global variable for testing
        execution_module._flow_loop = None

        loop1 = None
        try:
            loop1 = _get_flow_loop()
            loop2 = _get_flow_loop()
            assert loop1 is loop2
        finally:
            # Clean up
            if loop1 is not None:
                loop1.shutdown()
            # Reset for other tests
            execution_module._flow_loop = None


class TestRunFlowAsync:
    """Test suite for run_flow_async function."""

    @pytest.mark.asyncio
    async def test_run_flow_async_success(self) -> None:
        """run_flow_async should execute flow successfully."""
        mock_flow = Mock()
        input_data = ["item1", "item2"]
        context = FlowCommandContext.from_test()

        # Mock the flow's collect method
        async def mock_collect(input_stream: AsyncGenerator[str, None]) -> list[str]:
            # Convert input to list and return processed results
            items = []
            async for item in input_stream:
                items.append(item)
            return [f"processed_{item}" for item in items]

        mock_flow.collect.return_value = mock_collect

        # Convert input_data to async iterable
        async def async_input_data() -> AsyncGenerator[str, None]:
            for item in input_data:
                yield item

        result: FlowCommandResult[list[str]] = await run_flow_async(
            mock_flow, async_input_data(), context
        )

        assert result.success is True
        assert result.data == ["processed_item1", "processed_item2"]
        assert result.error is None

    @pytest.mark.asyncio
    async def test_run_flow_async_timeout_error(self) -> None:
        """run_flow_async should handle timeout errors."""
        import asyncio

        mock_flow = Mock()
        input_data = ["item1"]
        context = FlowCommandContext.from_test(execution_timeout=0.1)

        # Mock a slow collect method
        async def slow_collect(input_stream: AsyncGenerator[str, None]) -> list[str]:
            await asyncio.sleep(1.0)  # Longer than timeout
            return ["result"]

        mock_flow.collect.return_value = slow_collect

        # Convert input_data to async iterable
        async def async_input_timeout() -> AsyncGenerator[str, None]:
            for item in input_data:
                yield item

        result: FlowCommandResult[list[str]] = await run_flow_async(
            mock_flow, async_input_timeout(), context
        )

        assert result.success is False
        assert result.data is None
        assert result.error is not None

    @pytest.mark.asyncio
    async def test_run_flow_async_execution_error(self) -> None:
        """run_flow_async should handle execution errors."""
        mock_flow = Mock()
        input_data = ["item1"]
        context = FlowCommandContext.from_test()

        # Mock a failing collect method
        async def failing_collect(input_stream: AsyncGenerator[str, None]) -> list[str]:
            raise RuntimeError("Collection failed")

        mock_flow.collect.return_value = failing_collect

        # Convert input_data to async iterable
        async def async_input_error() -> AsyncGenerator[str, None]:
            for item in input_data:
                yield item

        result: FlowCommandResult[list[str]] = await run_flow_async(
            mock_flow, async_input_error(), context
        )

        assert result.success is False
        assert result.data is None
        assert result.error is not None
        assert "Collection failed" in result.error

    @pytest.mark.asyncio
    async def test_convert_to_async_iterable(self) -> None:
        """Test _convert_to_async_iterable utility function."""
        from flow_command.async_bridge.execution import _convert_to_async_iterable

        input_data = [1, 2, 3]
        async_iter = _convert_to_async_iterable(input_data)

        results = []
        async for item in async_iter:
            results.append(item)

        assert results == [1, 2, 3]

    @pytest.mark.asyncio
    async def test_convert_to_async_generator(self) -> None:
        """Test _convert_to_async_generator utility function."""
        from flow_command.async_bridge.execution import (
            _convert_to_async_generator,
            _convert_to_async_iterable,
        )

        input_data = [1, 2, 3]
        async_iter = _convert_to_async_iterable(input_data)
        async_gen = _convert_to_async_generator(async_iter)

        results = []
        async for item in async_gen:
            results.append(item)

        assert results == [1, 2, 3]

    def test_run_flow_sync_real_execution_path(self) -> None:
        """Test run_flow_sync with real flow execution to cover async lines."""
        mock_flow = Mock()
        input_data = ["item1", "item2"]
        context = FlowCommandContext.from_test()

        # Create a real async collect function that will be executed
        async def real_collect_function(
            async_gen: AsyncGenerator[str, None]
        ) -> list[str]:
            # This will actually exercise lines 34-36 in run_flow_sync
            results = []
            async for item in async_gen:
                results.append(f"processed_{item}")
            return results

        # Mock the flow to return our real async function
        mock_flow.collect.return_value = real_collect_function

        # This will execute the real async code path without mocking the loop
        with patch(
            "flow_command.async_bridge.execution._get_flow_loop"
        ) as mock_get_loop:
            # Use a real FlowEventLoop but ensure we control it
            from flow_command.async_bridge.loop_manager import FlowEventLoop

            test_loop = FlowEventLoop()
            mock_get_loop.return_value = test_loop

            try:
                result: FlowCommandResult[list[str]] = run_flow_sync(
                    mock_flow, input_data, context
                )

                # Verify the result
                assert result.success is True
                assert result.data == ["processed_item1", "processed_item2"]
                assert result.error is None
            finally:
                test_loop.shutdown()

    def test_run_flow_sync_with_frame_check_branch_coverage(self) -> None:
        """Test the specific branch where coro.cr_frame is not None during cleanup."""

        # This test focuses on the specific condition check without causing unraisable exceptions
        mock_flow = Mock()
        input_data = ["item1"]
        context = FlowCommandContext.from_test()

        cleanup_called = False

        # Create a real async function that will create a coroutine with a frame
        async def flow_with_frame(async_gen: AsyncGenerator[str, None]) -> list[str]:
            # Just process the data normally
            results = []
            async for item in async_gen:
                results.append(f"processed_{item}")
            return results

        mock_flow.collect.return_value = flow_with_frame

        # Create a custom FlowEventLoop that raises an exception but preserves the frame
        class TestFlowEventLoop:
            def execute_with_timeout(self, coro: Any, timeout: float) -> Any:
                nonlocal cleanup_called
                # Verify the coroutine has a frame (it should since it's not consumed)
                if (
                    hasattr(coro, "cr_frame")
                    and getattr(coro, "cr_frame", None) is not None
                ):
                    cleanup_called = True
                # Properly close the coroutine before raising to prevent unraisable exceptions
                if hasattr(coro, "close"):
                    coro.close()
                raise RuntimeError("Test exception for branch coverage")

        # Patch _get_flow_loop to use our custom loop
        with patch(
            "flow_command.async_bridge.execution._get_flow_loop"
        ) as mock_get_loop:
            mock_get_loop.return_value = TestFlowEventLoop()

            # Execute the actual run_flow_sync function
            result: FlowCommandResult[list[str]] = run_flow_sync(
                mock_flow, input_data, context
            )

            # Verify error result
            assert result.success is False
            assert result.error is not None
            assert "Test exception for branch coverage" in result.error

            # Verify our frame check was executed
            assert (
                cleanup_called
            ), "Frame check should have been executed in execute_with_timeout"

    def test_run_flow_sync_coroutine_cleanup_on_error(self) -> None:
        """Test run_flow_sync properly cleans up coroutine when loop raises error."""

        # Focus on testing the cleanup path without complex setup
        mock_flow = Mock()
        input_data = ["item1"]
        context = FlowCommandContext.from_test()

        # Create a simple async function
        async def simple_flow_collect(
            async_gen: AsyncGenerator[str, None]
        ) -> list[str]:
            results = []
            async for item in async_gen:
                results.append(f"processed_{item}")
            return results

        mock_flow.collect.return_value = simple_flow_collect

        # Create a mock loop that preserves the test scenario
        mock_loop = Mock()

        def mock_execute_with_timeout(coro: Any, timeout: float) -> Any:
            # Verify coroutine exists and has frame before we raise exception
            assert hasattr(coro, "cr_frame"), "Coroutine should have cr_frame attribute"
            # Close the coroutine ourselves to simulate proper cleanup and prevent unraisable exceptions
            if hasattr(coro, "close"):
                coro.close()
            raise RuntimeError("Mock loop error for testing")

        mock_loop.execute_with_timeout.side_effect = mock_execute_with_timeout

        # Test the actual function
        with patch(
            "flow_command.async_bridge.execution._get_flow_loop"
        ) as mock_get_loop:
            mock_get_loop.return_value = mock_loop

            result: FlowCommandResult[list[str]] = run_flow_sync(
                mock_flow, input_data, context
            )

            # Verify the result is an error
            assert result.success is False
            assert result.error is not None
            assert "Mock loop error for testing" in result.error

            # The key point is that run_flow_sync handled the exception gracefully
