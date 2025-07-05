"""Tests for debug_stream and traced_flow functions."""

import json
from collections.abc import AsyncGenerator
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any

import pytest

if TYPE_CHECKING:
    from pytest import CaptureFixture

from flowengine.observability.debugging import (
    FlowDebugger,
    FlowExecutionContext,
    FlowExecutionErrorWithContext,
    debug_stream,
    get_flow_debugger,
    traced_flow,
)


class TestDebugStream:
    """Tests for debug_stream function."""

    @pytest.mark.asyncio
    async def test_debug_stream_basic(self):
        """Test basic debug stream functionality."""
        debugger = get_flow_debugger()
        debugger.debug_enabled = False  # Disable output for test

        async def test_stream():
            for i in range(3):
                yield i

        debug_flow = debug_stream()
        result = await debug_flow.to_list()(test_stream())

        assert result == [0, 1, 2]

    @pytest.mark.asyncio
    async def test_debug_stream_with_logging(self, capsys: "CaptureFixture[str]"):
        """Test debug stream with logging enabled."""
        debugger = get_flow_debugger()
        debugger.debug_enabled = True

        try:

            async def test_stream():
                for i in range(2):
                    yield i

            debug_flow = debug_stream(log_items=True)
            result = await debug_flow.to_list()(test_stream())

            assert result == [0, 1]

            captured = capsys.readouterr()
            assert "🐛 Debug: debug_stream processing item 1: 0" in captured.out
            assert "🐛 Debug: debug_stream processing item 2: 1" in captured.out
        finally:
            debugger.debug_enabled = False

    @pytest.mark.asyncio
    async def test_debug_stream_with_breakpoint_condition(self):
        """Test debug stream with breakpoint condition."""
        debugger = get_flow_debugger()
        debugger.debug_enabled = True

        try:

            async def test_stream():
                for i in range(5):
                    yield i

            # Mock the breakpoint trigger to avoid interactive input
            original_check = debugger.check_breakpoint

            async def mock_check_breakpoint(
                item: Any, context: FlowExecutionContext
            ) -> None:
                # Just record that breakpoint was hit
                context.metadata["breakpoint_hit"] = True

            debugger.check_breakpoint = mock_check_breakpoint

            debug_flow = debug_stream(breakpoint_condition=lambda x: x == 2)
            result = await debug_flow.to_list()(test_stream())

            assert result == [0, 1, 2, 3, 4]
            # Verify breakpoint was triggered (would be in execution history)
            assert len(debugger.execution_history) > 0

            # Restore original method
            debugger.check_breakpoint = original_check
        finally:
            debugger.debug_enabled = False
            debugger.execution_history.clear()

    @pytest.mark.asyncio
    async def test_debug_stream_error_handling(self):
        """Test debug stream error handling."""

        async def failing_stream():
            yield 1
            raise ValueError("Test error")

        debug_flow = debug_stream()

        with pytest.raises(FlowExecutionErrorWithContext) as exc_info:
            await debug_flow.to_list()(failing_stream())

        error = exc_info.value
        assert "Error in debug stream: Test error" in str(error)
        assert error.flow_name == "debug_stream"
        assert isinstance(error.original_exception, ValueError)
        assert str(error.original_exception) == "Test error"


class TestTracedFlow:
    """Tests for traced_flow function."""

    @pytest.mark.asyncio
    async def test_traced_flow_basic(self):
        """Test basic traced flow functionality."""
        from flowengine.flow import Flow

        # Create a simple flow to trace
        async def simple_flow_fn(
            stream: AsyncGenerator[int, None],
        ) -> AsyncGenerator[int, None]:
            async for item in stream:
                yield item * 2

        simple_flow = Flow(simple_flow_fn, name="simple_flow")
        traced = traced_flow(simple_flow)

        async def test_stream():
            for i in range(3):
                yield i

        result = await traced.to_list()(test_stream())
        assert result == [0, 2, 4]
        assert traced.name == "traced(simple_flow)"

    @pytest.mark.asyncio
    async def test_traced_flow_with_breakpoints(self):
        """Test traced flow with breakpoint checking."""
        from flowengine.flow import Flow

        debugger = get_flow_debugger()
        debugger.debug_enabled = True

        try:
            # Create a simple flow
            async def multiply_flow_fn(
                stream: AsyncGenerator[int, None],
            ) -> AsyncGenerator[int, None]:
                async for item in stream:
                    yield item * 3

            multiply_flow = Flow(multiply_flow_fn, name="multiply_flow")

            # Mock breakpoint checking
            original_check = debugger.check_breakpoint
            breakpoint_hits: list[tuple[int, str]] = []

            async def mock_check_breakpoint(
                item: Any, context: FlowExecutionContext
            ) -> None:
                breakpoint_hits.append((item, context.flow_name))

            debugger.check_breakpoint = mock_check_breakpoint

            traced = traced_flow(multiply_flow)

            async def test_stream():
                for i in range(2):
                    yield i

            result = await traced.to_list()(test_stream())

            assert result == [0, 3]
            assert len(breakpoint_hits) == 2
            assert breakpoint_hits[0] == (0, "multiply_flow")
            assert breakpoint_hits[1] == (3, "multiply_flow")

            # Restore original
            debugger.check_breakpoint = original_check
        finally:
            debugger.debug_enabled = False
            debugger.execution_history.clear()

    @pytest.mark.asyncio
    async def test_traced_flow_error_handling(self):
        """Test traced flow error handling and enhancement."""
        from flowengine.flow import Flow

        # Create a flow that raises an error
        async def failing_flow_fn(
            stream: AsyncGenerator[int, None],
        ) -> AsyncGenerator[int, None]:
            async for item in stream:
                if item == 1:
                    raise ValueError("Test error in flow")
                yield item

        failing_flow = Flow(failing_flow_fn, name="failing_flow")
        traced = traced_flow(failing_flow)

        async def test_stream():
            for i in range(3):
                yield i

        with pytest.raises(FlowExecutionErrorWithContext) as exc_info:
            await traced.to_list()(test_stream())

        error = exc_info.value
        assert "Error in flow 'failing_flow': Test error in flow" in str(error)
        assert error.flow_name == "failing_flow"
        assert isinstance(error.original_exception, ValueError)

    @pytest.mark.asyncio
    async def test_traced_flow_preserves_enhanced_errors(self):
        """Test that traced flow preserves already enhanced errors."""
        from flowengine.flow import Flow

        # Create a flow that raises an already enhanced error
        async def enhanced_error_flow_fn(
            stream: AsyncGenerator[int, None],
        ) -> AsyncGenerator[int, None]:
            async for item in stream:
                if item == 1:
                    enhanced_error = FlowExecutionErrorWithContext(
                        "Pre-enhanced error",
                        flow_name="inner_flow",
                        original_exception=RuntimeError("Inner error"),
                    )
                    raise enhanced_error
                yield item

        enhanced_error_flow = Flow(enhanced_error_flow_fn, name="enhanced_error_flow")
        traced = traced_flow(enhanced_error_flow)

        async def test_stream():
            for i in range(3):
                yield i

        # Use explicit async context manager style to ensure proper cleanup
        test_gen = test_stream()
        try:
            with pytest.raises(FlowExecutionErrorWithContext) as exc_info:
                await traced.to_list()(test_gen)
        finally:
            # Ensure the generator is properly closed
            if hasattr(test_gen, "aclose"):
                await test_gen.aclose()

        error = exc_info.value
        # Should preserve the original enhanced error, not double-wrap it
        assert str(error) == "Pre-enhanced error"
        assert error.flow_name == "inner_flow"
        assert isinstance(error.original_exception, RuntimeError)

    @pytest.mark.asyncio
    async def test_traced_flow_execution_context_tracking(self):
        """Test that traced flow properly tracks execution context."""
        from flowengine.flow import Flow

        debugger = get_flow_debugger()

        # Create a flow
        async def context_flow_fn(
            stream: AsyncGenerator[int, None],
        ) -> AsyncGenerator[int, None]:
            async for item in stream:
                yield item + 10

        context_flow = Flow(context_flow_fn, name="context_flow")
        traced = traced_flow(context_flow)

        result = await self._execute_traced_flow_test(traced)
        self._verify_execution_tracking(debugger, result)

    async def _execute_traced_flow_test(self, traced_flow: Any) -> list[int]:
        """Helper to execute traced flow test."""

        async def test_stream():
            for i in range(2):
                yield i

        return await traced_flow.to_list()(test_stream())

    def _verify_execution_tracking(
        self, debugger: FlowDebugger, result: list[int]
    ) -> None:
        """Helper to verify execution tracking results."""
        assert result == [10, 11]
        assert len(debugger.execution_history) > 0

        # Find our flow in the history
        context_entries = [
            ctx for ctx in debugger.execution_history if ctx.flow_name == "context_flow"
        ]
        assert len(context_entries) > 0

        context_entry = context_entries[0]
        assert context_entry.flow_name == "context_flow"
        assert context_entry.item_index == 2  # Processed 2 items

        # Clean up
        debugger.execution_history.clear()
