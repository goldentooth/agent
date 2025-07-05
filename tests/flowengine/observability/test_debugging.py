"""Tests for debugging and introspection utilities."""

import json
from datetime import datetime
from pathlib import Path

import pytest

from flowengine.observability.debugging import (
    BreakpointCondition,
    BreakpointRegistry,
    FlowDebugger,
    FlowExecutionContext,
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
