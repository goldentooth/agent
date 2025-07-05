"""Tests for debugging and introspection utilities."""

import json
from collections.abc import AsyncGenerator
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any

import pytest

if TYPE_CHECKING:
    from pytest import CaptureFixture

from flowengine.observability.debugging import (
    BreakpointCondition,
    BreakpointRegistry,
    FlowDebugger,
    FlowExecutionContext,
    FlowExecutionErrorWithContext,
    debug_stream,
    get_flow_debugger,
    traced_flow,
)


class TestFlowExecutionContext:
    """Tests for FlowExecutionContext class."""

    def test_context_creation(self):
        """Test basic context creation."""
        context = FlowExecutionContext(
            flow_name="test_flow",
            started_at=datetime.now(),
            input_type="int",
        )

        assert context.flow_name == "test_flow"
        assert context.input_type == "int"
        assert context.item_index == 0
        assert context.parent_flow is None

    def test_context_to_dict(self):
        """Test context serialization to dictionary."""
        now = datetime.now()
        context = FlowExecutionContext(
            flow_name="test_flow",
            started_at=now,
            current_item="test_item",
            item_index=5,
            parent_flow="parent_flow",
        )

        context_dict = context.to_dict()

        assert context_dict["flow_name"] == "test_flow"
        assert context_dict["started_at"] == now.isoformat()
        assert context_dict["current_item"] == "test_item"
        assert context_dict["item_index"] == 5
        assert context_dict["parent_flow"] == "parent_flow"
        assert "execution_id" in context_dict


class TestBreakpointTypes:
    """Tests for breakpoint-related type aliases."""

    def test_breakpoint_condition_callable(self):
        """Test BreakpointCondition type works with callables."""
        context = FlowExecutionContext("test", datetime.now())

        # Simple condition
        condition: BreakpointCondition = lambda item, ctx: item > 5
        assert condition(10, context) is True
        assert condition(3, context) is False

    def test_breakpoint_registry_dict(self):
        """Test BreakpointRegistry type works with dictionaries."""
        condition: BreakpointCondition = lambda item, ctx: True
        registry: BreakpointRegistry = {"test_flow": condition}

        assert "test_flow" in registry
        assert registry["test_flow"] == condition


class TestFlowDebugger:
    """Tests for FlowDebugger class."""

    def test_debugger_creation(self):
        """Test FlowDebugger creation."""
        debugger = FlowDebugger()

        assert debugger.execution_stack == []
        assert debugger.execution_history == []
        assert debugger.breakpoints == {}
        assert not debugger.debug_enabled
        assert debugger.max_history == 1000

    def test_enable_debugging(self):
        """Test enabling debugging."""
        debugger = FlowDebugger()
        assert not debugger.debug_enabled

        debugger.enable_debugging()
        assert debugger.debug_enabled

    def test_disable_debugging(self):
        """Test disabling debugging."""
        debugger = FlowDebugger()
        debugger.enable_debugging()
        assert debugger.debug_enabled

        debugger.disable_debugging()
        assert not debugger.debug_enabled

    def test_add_breakpoint(self):
        """Test adding breakpoints."""
        debugger = FlowDebugger()

        # Add breakpoint with default condition
        debugger.add_breakpoint("test_flow")
        assert "test_flow" in debugger.breakpoints

        # Add breakpoint with custom condition
        condition: BreakpointCondition = lambda item, ctx: item > 5
        debugger.add_breakpoint("custom_flow", condition)

        assert "custom_flow" in debugger.breakpoints
        assert debugger.breakpoints["custom_flow"] == condition

    def test_remove_breakpoint(self):
        """Test removing breakpoints."""
        debugger = FlowDebugger()

        # Add a breakpoint first
        debugger.add_breakpoint("test_flow")
        assert "test_flow" in debugger.breakpoints

        # Remove the breakpoint
        debugger.remove_breakpoint("test_flow")
        assert "test_flow" not in debugger.breakpoints

        # Removing non-existent breakpoint should not raise error
        debugger.remove_breakpoint("non_existent")  # Should not raise

    @pytest.mark.asyncio
    async def test_execution_context_manager(self):
        """Test execution context manager."""
        debugger = FlowDebugger()

        async with debugger.execution_context("test_flow") as context:
            assert context.flow_name == "test_flow"
            assert len(debugger.execution_stack) == 1
            assert debugger.execution_stack[0] == context

        # After exiting context
        assert len(debugger.execution_stack) == 0
        assert len(debugger.execution_history) == 1
        assert debugger.execution_history[0] == context

    @pytest.mark.asyncio
    async def test_execution_context_history_limit(self):
        """Test execution context history limit enforcement."""
        debugger = FlowDebugger()
        debugger.max_history = 2  # Set small limit for testing

        # Add contexts beyond the limit
        async with debugger.execution_context("flow1"):
            pass
        async with debugger.execution_context("flow2"):
            pass
        async with debugger.execution_context("flow3"):  # This should trigger cleanup
            pass

        # Should only keep the last 2 contexts
        assert len(debugger.execution_history) == 2
        assert debugger.execution_history[0].flow_name == "flow2"
        assert debugger.execution_history[1].flow_name == "flow3"

    @pytest.mark.asyncio
    async def test_execution_context_stack_corruption(self):
        """Test execution context cleanup when stack is corrupted."""
        debugger = FlowDebugger()

        async with debugger.execution_context("flow1") as context1:
            # Manually corrupt the stack to test the safety check
            debugger.execution_stack.clear()  # This simulates stack corruption

            # The context manager should still clean up safely
            pass

        # Both contexts should be in history even with corrupted stack
        assert len(debugger.execution_history) == 1
        assert debugger.execution_history[0] == context1

    @pytest.mark.asyncio
    async def test_execution_context_wrong_order_cleanup(self):
        """Test execution context when contexts exit out of order."""
        debugger = FlowDebugger()

        async with debugger.execution_context("flow1") as context1:
            async with debugger.execution_context("flow2") as context2:
                # Manually swap the stack order to test the safety check
                debugger.execution_stack[0], debugger.execution_stack[1] = (
                    debugger.execution_stack[1],
                    debugger.execution_stack[0],
                )
                # context2 will exit first but won't be the last in stack

        # Both should be in history despite the corruption
        assert len(debugger.execution_history) == 2

    def test_context_to_dict_with_none_values(self):
        """Test context serialization with None values."""
        context = FlowExecutionContext(
            flow_name="test_flow",
            started_at=datetime.now(),
            current_item=None,  # Explicitly test None case
        )

        context_dict = context.to_dict()
        assert context_dict["current_item"] is None

    def test_enable_disable_debugging_cycle(self):
        """Test multiple enable/disable cycles."""
        debugger = FlowDebugger()

        for _ in range(3):
            assert not debugger.debug_enabled
            debugger.enable_debugging()
            assert debugger.debug_enabled
            debugger.disable_debugging()
            assert not debugger.debug_enabled

    @pytest.mark.asyncio
    async def test_check_breakpoint_disabled(self):
        """Test breakpoint checking when debugging is disabled."""
        debugger = FlowDebugger()
        debugger.add_breakpoint("test_flow", lambda item, ctx: True)

        context = FlowExecutionContext("test_flow", datetime.now())

        # Should not trigger breakpoint when debugging disabled
        await debugger.check_breakpoint("test_item", context)

        # No exceptions should be raised

    @pytest.mark.asyncio
    async def test_check_breakpoint_no_condition_match(self):
        """Test breakpoint checking when condition doesn't match."""
        debugger = FlowDebugger()
        debugger.enable_debugging()
        debugger.add_breakpoint("test_flow", lambda item, ctx: item > 10)

        context = FlowExecutionContext("test_flow", datetime.now())

        # Should not trigger breakpoint for item = 5
        await debugger.check_breakpoint(5, context)

        # No exceptions should be raised

    def test_get_execution_trace(self):
        """Test getting execution trace."""
        debugger = FlowDebugger()

        # Add some history
        context1 = FlowExecutionContext("flow1", datetime.now())
        context2 = FlowExecutionContext("flow2", datetime.now())

        debugger.execution_history = [context1, context2]

        trace = debugger.get_execution_trace()

        assert len(trace) == 2
        assert all(isinstance(item, dict) for item in trace)
        assert trace[0]["flow_name"] == "flow1"
        assert trace[1]["flow_name"] == "flow2"

    def test_export_trace(self, tmp_path: Path):
        """Test exporting execution trace."""
        debugger = FlowDebugger()

        # Add some history
        context = FlowExecutionContext("test_flow", datetime.now())
        debugger.execution_history = [context]
        debugger.breakpoints["test_flow"] = lambda item, ctx: True

        filepath = tmp_path / "trace.json"
        debugger.export_trace(str(filepath))

        assert filepath.exists()

        # Verify JSON content
        with open(filepath) as f:
            data = json.load(f)

        assert "timestamp" in data
        assert "current_stack" in data
        assert "execution_history" in data
        assert "breakpoints" in data
        assert "test_flow" in data["breakpoints"]


class TestFlowExecutionErrorWithContext:
    """Tests for FlowExecutionErrorWithContext class."""

    def test_error_creation(self):
        """Test error creation with context."""
        context = FlowExecutionContext("test_flow", datetime.now())
        original_error = ValueError("Original error")

        error = FlowExecutionErrorWithContext(
            "Test error",
            flow_name="test_flow",
            execution_context=context,
            original_exception=original_error,
        )

        assert str(error) == "Test error"
        assert error.flow_name == "test_flow"
        assert error.execution_context == context
        assert error.original_exception == original_error

    def test_error_captures_execution_stack(self):
        """Test that error captures current execution stack."""
        debugger = get_flow_debugger()

        # Add some contexts to the global debugger stack
        context1 = FlowExecutionContext("flow1", datetime.now())
        context2 = FlowExecutionContext("flow2", datetime.now())
        debugger.execution_stack = [context1, context2]

        try:
            error = FlowExecutionErrorWithContext("Test error")

            assert len(error.execution_stack) == 2
            assert error.execution_stack[0] == context1
            assert error.execution_stack[1] == context2
        finally:
            # Clean up
            debugger.execution_stack.clear()

    def test_get_debug_info(self):
        """Test getting comprehensive debug information."""
        context = FlowExecutionContext("test_flow", datetime.now())
        original_error = ValueError("Original error")

        error = FlowExecutionErrorWithContext(
            "Test error",
            flow_name="test_flow",
            execution_context=context,
            original_exception=original_error,
        )

        debug_info = error.get_debug_info()

        assert debug_info["error_message"] == "Test error"
        assert debug_info["flow_name"] == "test_flow"
        assert debug_info["execution_context"] == context.to_dict()
        assert debug_info["original_exception"] == "Original error"
        assert isinstance(debug_info["execution_stack"], list)
        assert "traceback" in debug_info

    def test_get_debug_info_with_none_values(self):
        """Test debug info with None values."""
        error = FlowExecutionErrorWithContext("Test error")
        debug_info = error.get_debug_info()

        assert debug_info["error_message"] == "Test error"
        assert debug_info["flow_name"] is None
        assert debug_info["execution_context"] is None
        assert debug_info["original_exception"] is None
        assert debug_info["traceback"] is None
        assert debug_info["execution_stack"] == []

    def test_print_debug_info(self, capsys: "CaptureFixture[str]"):
        """Test printing debug information."""
        context = FlowExecutionContext("test_flow", datetime.now())
        context.current_item = "test_item"
        context.item_index = 5

        original_error = ValueError("Original error")
        error = FlowExecutionErrorWithContext(
            "Test error",
            flow_name="test_flow",
            execution_context=context,
            original_exception=original_error,
        )

        error.print_debug_info()
        captured = capsys.readouterr()

        assert "❌ Flow Execution Error in 'test_flow'" in captured.out
        assert "Message: Test error" in captured.out
        assert "Current Item: test_item" in captured.out
        assert "Item Index: 5" in captured.out
        assert "Original Exception:" in captured.out
        assert "ValueError: Original error" in captured.out

    def test_print_debug_info_with_execution_stack(self, capsys: "CaptureFixture[str]"):
        """Test printing debug info with execution stack."""
        debugger = get_flow_debugger()

        # Add contexts to the execution stack
        context1 = FlowExecutionContext("flow1", datetime.now())
        context1.item_index = 1
        context2 = FlowExecutionContext("flow2", datetime.now())
        context2.item_index = 2

        debugger.execution_stack = [context1, context2]

        try:
            error = FlowExecutionErrorWithContext("Test error", flow_name="test_flow")
            error.print_debug_info()
            captured = capsys.readouterr()

            assert "📚 Execution Stack:" in captured.out
            assert "└─ flow2 (item 2)" in captured.out
            assert "  └─ flow1 (item 1)" in captured.out
        finally:
            debugger.execution_stack.clear()

    def test_print_debug_info_minimal(self, capsys: "CaptureFixture[str]"):
        """Test printing debug info with minimal information."""
        error = FlowExecutionErrorWithContext("Test error")
        error.print_debug_info()
        captured = capsys.readouterr()

        assert "❌ Flow Execution Error in 'None'" in captured.out
        assert "Message: Test error" in captured.out
        # Should not contain optional sections
        assert "Current Item:" not in captured.out
        assert "📚 Execution Stack:" not in captured.out
        assert "🔍 Original Exception:" not in captured.out


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

        with pytest.raises(FlowExecutionErrorWithContext) as exc_info:
            await traced.to_list()(test_stream())

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
