"""Tests for debugging and introspection utilities."""

import json
from datetime import datetime

import pytest

from goldentooth_agent.flow_engine import Flow
from goldentooth_agent.flow_engine.combinators.basic import map_stream
from goldentooth_agent.flow_engine.observability.debugging import (
    FlowDebugger,
    FlowExecutionContext,
    FlowExecutionErrorWithContext,
    add_flow_breakpoint,
    debug_session,
    debug_stream,
    disable_flow_debugging,
    enable_flow_debugging,
    export_execution_trace,
    get_execution_trace,
    get_flow_debugger,
    inspect_flow,
    remove_flow_breakpoint,
    traced_flow,
)


async def async_range(n: int):
    """Generate an async range of integers."""
    for i in range(n):
        yield i


def increment(x: int) -> int:
    """Increment a number by 1."""
    return x + 1


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

    def test_enable_disable_debugging(self):
        """Test enabling and disabling debugging."""
        debugger = FlowDebugger()

        assert not debugger.debug_enabled

        debugger.enable_debugging()
        assert debugger.debug_enabled

        debugger.disable_debugging()
        assert not debugger.debug_enabled

    def test_add_remove_breakpoint(self):
        """Test adding and removing breakpoints."""
        debugger = FlowDebugger()

        # Add breakpoint
        condition = lambda item, ctx: item > 5
        debugger.add_breakpoint("test_flow", condition)

        assert "test_flow" in debugger.breakpoints
        assert debugger.breakpoints["test_flow"] == condition

        # Remove breakpoint
        debugger.remove_breakpoint("test_flow")
        assert "test_flow" not in debugger.breakpoints

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

    def test_export_trace(self, tmp_path):
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

    def test_get_debug_info(self):
        """Test getting debug info from error."""
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
        assert debug_info["execution_context"] is not None
        assert debug_info["original_exception"] == "Original error"

    def test_print_debug_info(self, capsys):
        """Test printing debug info."""
        context = FlowExecutionContext("test_flow", datetime.now())
        context.current_item = "test_item"
        context.item_index = 5

        error = FlowExecutionErrorWithContext(
            "Test error",
            flow_name="test_flow",
            execution_context=context,
        )

        error.print_debug_info()

        captured = capsys.readouterr()
        assert "Flow Execution Error in 'test_flow'" in captured.out
        assert "Test error" in captured.out
        assert "test_item" in captured.out
        assert "5" in captured.out


class TestDebugStream:
    """Tests for debug_stream function."""

    @pytest.mark.asyncio
    async def test_debug_stream_basic(self):
        """Test basic debug stream functionality."""
        debug_flow = debug_stream(log_items=False)  # Disable logging for test
        assert "debug" in debug_flow.name

        input_stream = async_range(3)
        result_stream = debug_flow(input_stream)
        values = [item async for item in result_stream]

        assert values == [0, 1, 2]

    @pytest.mark.asyncio
    async def test_debug_stream_with_logging(self, capsys):
        """Test debug stream with logging enabled."""
        # Enable debugging globally
        debugger = get_flow_debugger()
        debugger.enable_debugging()

        try:
            debug_flow = debug_stream(log_items=True)

            input_stream = async_range(2)
            result_stream = debug_flow(input_stream)
            values = [item async for item in result_stream]

            assert values == [0, 1]

            captured = capsys.readouterr()
            assert "Debug: debug_stream processing item" in captured.out

        finally:
            debugger.disable_debugging()

    @pytest.mark.asyncio
    async def test_debug_stream_with_breakpoint_condition(self):
        """Test debug stream with breakpoint condition."""
        condition = lambda item: item == 2

        debug_flow = debug_stream(breakpoint_condition=condition, log_items=False)

        input_stream = async_range(4)
        result_stream = debug_flow(input_stream)
        values = [item async for item in result_stream]

        assert values == [0, 1, 2, 3]

    @pytest.mark.asyncio
    async def test_debug_stream_with_error(self):
        """Test debug stream error handling."""

        async def failing_stream():
            yield 1
            raise ValueError("Test error")

        debug_flow = debug_stream(log_items=False)

        with pytest.raises(FlowExecutionErrorWithContext) as exc_info:
            result_stream = debug_flow(failing_stream())
            _ = [item async for item in result_stream]

        assert "Error in debug stream" in str(exc_info.value)
        assert exc_info.value.original_exception is not None


class TestTracedFlow:
    """Tests for traced_flow function."""

    @pytest.mark.asyncio
    async def test_traced_flow_basic(self):
        """Test basic traced flow functionality."""
        original_flow = map_stream(increment)
        traced = traced_flow(original_flow)

        assert "traced" in traced.name
        assert original_flow.name in traced.name

        input_stream = async_range(3)
        result_stream = traced(input_stream)
        values = [item async for item in result_stream]

        assert values == [1, 2, 3]

    @pytest.mark.asyncio
    async def test_traced_flow_with_error(self):
        """Test traced flow error handling."""

        async def failing_flow_func(stream):
            async for item in stream:
                if item == 2:
                    raise ValueError("Test error")
                yield item

        failing_flow = Flow(failing_flow_func, name="failing_flow")
        traced = traced_flow(failing_flow)

        with pytest.raises(FlowExecutionErrorWithContext) as exc_info:
            input_stream = async_range(4)
            result_stream = traced(input_stream)
            _ = [item async for item in result_stream]

        assert "Error in flow 'failing_flow'" in str(exc_info.value)
        assert exc_info.value.flow_name == "failing_flow"


class TestConvenienceFunctions:
    """Tests for module-level convenience functions."""

    def test_get_flow_debugger(self):
        """Test get_flow_debugger function."""
        debugger = get_flow_debugger()
        assert isinstance(debugger, FlowDebugger)

    def test_enable_disable_flow_debugging(self):
        """Test global debugging enable/disable functions."""
        debugger = get_flow_debugger()

        enable_flow_debugging()
        assert debugger.debug_enabled

        disable_flow_debugging()
        assert not debugger.debug_enabled

    def test_add_remove_flow_breakpoint(self):
        """Test global breakpoint management functions."""
        debugger = get_flow_debugger()

        condition = lambda item, ctx: True
        add_flow_breakpoint("test_flow", condition)

        assert "test_flow" in debugger.breakpoints

        remove_flow_breakpoint("test_flow")
        assert "test_flow" not in debugger.breakpoints

    def test_get_execution_trace_function(self):
        """Test get_execution_trace convenience function."""
        trace = get_execution_trace()
        assert isinstance(trace, list)

    def test_export_execution_trace_function(self, tmp_path):
        """Test export_execution_trace convenience function."""
        filepath = tmp_path / "trace.json"
        export_execution_trace(str(filepath))

        assert filepath.exists()

    def test_inspect_flow_function(self):
        """Test inspect_flow convenience function."""
        flow = map_stream(increment)
        inspection = inspect_flow(flow)

        assert isinstance(inspection, dict)
        assert "name" in inspection
        assert "type" in inspection
        assert "function_name" in inspection
        assert "is_async" in inspection


class TestDebugSession:
    """Tests for debug_session context manager."""

    @pytest.mark.asyncio
    async def test_debug_session_enables_debugging(self):
        """Test that debug_session enables debugging."""
        debugger = get_flow_debugger()
        original_state = debugger.debug_enabled

        try:
            async with debug_session() as session_debugger:
                assert debugger.debug_enabled
                assert session_debugger == debugger

            # Should restore original state
            assert debugger.debug_enabled == original_state

        finally:
            debugger.debug_enabled = original_state

    @pytest.mark.asyncio
    async def test_debug_session_disable_breakpoints(self):
        """Test debug_session with breakpoints disabled."""
        debugger = get_flow_debugger()
        original_state = debugger.debug_enabled

        try:
            async with debug_session(enable_breakpoints=False) as session_debugger:
                assert not debugger.debug_enabled
                assert session_debugger == debugger

        finally:
            debugger.debug_enabled = original_state

    @pytest.mark.asyncio
    async def test_debug_session_restores_state(self):
        """Test that debug_session restores original state."""
        debugger = get_flow_debugger()

        # Start with debugging enabled
        debugger.enable_debugging()
        assert debugger.debug_enabled

        try:
            async with debug_session(enable_breakpoints=False):
                assert not debugger.debug_enabled

            # Should restore to enabled
            assert debugger.debug_enabled

        finally:
            debugger.disable_debugging()
