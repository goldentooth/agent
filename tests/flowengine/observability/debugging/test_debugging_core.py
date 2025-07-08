"""Tests for core debugging components: FlowExecutionContext, BreakpointTypes, FlowDebugger."""

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
    get_flow_debugger,
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
    async def test_execution_context_manager(self) -> None:
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
    async def test_execution_context_history_limit(self) -> None:
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
    async def test_execution_context_stack_corruption(self) -> None:
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
    async def test_execution_context_wrong_order_cleanup(self) -> None:
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
    async def test_check_breakpoint_disabled(self) -> None:
        """Test breakpoint checking when debugging is disabled."""
        debugger = FlowDebugger()
        debugger.add_breakpoint("test_flow", lambda item, ctx: True)

        context = FlowExecutionContext("test_flow", datetime.now())

        # Should not trigger breakpoint when debugging disabled
        await debugger.check_breakpoint("test_item", context)

        # No exceptions should be raised

    @pytest.mark.asyncio
    async def test_check_breakpoint_no_condition_match(self) -> None:
        """Test breakpoint checking when condition doesn't match."""
        debugger = FlowDebugger()
        debugger.enable_debugging()
        debugger.add_breakpoint("test_flow", lambda item, ctx: item > 10)

        context = FlowExecutionContext("test_flow", datetime.now())

        # Should not trigger breakpoint for item = 5
        await debugger.check_breakpoint(5, context)

        # No exceptions should be raised

    @pytest.mark.asyncio
    async def test_check_breakpoint_condition_matches(self) -> None:
        """Test breakpoint checking when condition matches."""
        debugger = FlowDebugger()
        debugger.enable_debugging()

        # Mock the trigger method to avoid interactive input
        from unittest.mock import patch

        trigger_called = False

        async def mock_trigger(item: Any, context: FlowExecutionContext) -> None:
            nonlocal trigger_called
            trigger_called = True

        debugger.add_breakpoint("test_flow", lambda item, ctx: item == 5)
        context = FlowExecutionContext("test_flow", datetime.now())

        with patch.object(debugger, "trigger_breakpoint", side_effect=mock_trigger):
            # Should trigger breakpoint for item = 5
            await debugger.check_breakpoint(5, context)
            assert trigger_called

    @pytest.mark.asyncio
    async def test_check_breakpoint_no_breakpoint_registered(self) -> None:
        """Test breakpoint checking when no breakpoint is registered for flow."""
        debugger = FlowDebugger()
        debugger.enable_debugging()

        # No breakpoints added
        context = FlowExecutionContext("test_flow", datetime.now())

        # Should not trigger anything - flow not in breakpoints registry
        await debugger.check_breakpoint("test_item", context)

        # No exceptions should be raised

    @pytest.mark.asyncio
    async def test_trigger_breakpoint_output(
        self, capsys: "CaptureFixture[str]"
    ) -> None:
        """Test breakpoint trigger output."""
        debugger = FlowDebugger()
        context = FlowExecutionContext("test_flow", datetime.now())
        context.item_index = 3

        # Mock the command handler to avoid infinite loop
        from unittest.mock import patch

        async def mock_handler(item: Any) -> None:
            pass  # Do nothing to avoid input loop

        with patch.object(
            debugger, "handle_breakpoint_commands", side_effect=mock_handler
        ):
            await debugger.trigger_breakpoint("test_item", context)
            captured = capsys.readouterr()

            assert "🔍 Breakpoint hit in flow: test_flow" in captured.out
            assert "Item: test_item" in captured.out
            assert "Index: 3" in captured.out
            assert "Commands: (c)ontinue, (s)tack, (i)nspect, (q)uit" in captured.out

    def test_print_execution_stack(self, capsys: "CaptureFixture[str]"):
        """Test execution stack printing."""
        debugger = FlowDebugger()

        # Add some contexts to the stack
        context1 = FlowExecutionContext("flow1", datetime.now())
        context1.item_index = 1
        context2 = FlowExecutionContext("flow2", datetime.now())
        context2.item_index = 2

        debugger.execution_stack = [context1, context2]

        debugger.print_execution_stack()
        captured = capsys.readouterr()

        assert "📚 Execution Stack:" in captured.out
        assert "└─ flow2 (item 2)" in captured.out
        assert "  └─ flow1 (item 1)" in captured.out

    def test_print_item_inspection_simple(self, capsys: "CaptureFixture[str]"):
        """Test item inspection printing for simple types."""
        debugger = FlowDebugger()

        debugger.print_item_inspection("test_string")
        captured = capsys.readouterr()

        assert "🔬 Item Inspection:" in captured.out
        assert "Type: str" in captured.out
        assert "Value: 'test_string'" in captured.out
        assert "String: test_string" in captured.out

    def test_print_item_inspection_with_attributes(self, capsys: "CaptureFixture[str]"):
        """Test item inspection printing for objects with attributes."""
        debugger = FlowDebugger()

        class TestObject:
            def __init__(self) -> None:
                super().__init__()
                self.attr1 = "value1"
                self.attr2 = "value2"

        test_obj = TestObject()
        debugger.print_item_inspection(test_obj)
        captured = capsys.readouterr()

        assert "🔬 Item Inspection:" in captured.out
        assert "Type: TestObject" in captured.out
        assert "Attributes:" in captured.out
        assert "attr1" in captured.out
        assert "attr2" in captured.out

    @pytest.mark.asyncio
    async def test_handle_breakpoint_commands_continue(self, monkeypatch: Any) -> None:
        """Test breakpoint command handling - continue command."""
        debugger = FlowDebugger()

        # Mock input to simulate user entering 'c' command
        inputs = iter(["c"])

        def mock_input(prompt: str) -> str:
            return str(next(inputs))

        monkeypatch.setattr("builtins.input", mock_input)

        # Should exit loop without raising
        await debugger.handle_breakpoint_commands("test_item")

    @pytest.mark.asyncio
    async def test_handle_breakpoint_commands_stack(
        self, monkeypatch: Any, capsys: "CaptureFixture[str]"
    ) -> None:
        """Test breakpoint command handling - stack command."""
        debugger = FlowDebugger()

        # Add a context to the stack
        context = FlowExecutionContext("test_flow", datetime.now())
        debugger.execution_stack = [context]

        # Mock input to simulate user entering 's' then 'c'
        inputs = iter(["s", "c"])

        def mock_input(prompt: str) -> str:
            return str(next(inputs))

        monkeypatch.setattr("builtins.input", mock_input)

        await debugger.handle_breakpoint_commands("test_item")
        captured = capsys.readouterr()

        assert "📚 Execution Stack:" in captured.out

    @pytest.mark.asyncio
    async def test_handle_breakpoint_commands_inspect(
        self, monkeypatch: Any, capsys: "CaptureFixture[str]"
    ) -> None:
        """Test breakpoint command handling - inspect command."""
        debugger = FlowDebugger()

        # Mock input to simulate user entering 'i' then 'c'
        inputs = iter(["i", "c"])

        def mock_input(prompt: str) -> str:
            return str(next(inputs))

        monkeypatch.setattr("builtins.input", mock_input)

        await debugger.handle_breakpoint_commands("test_item")
        captured = capsys.readouterr()

        assert "🔬 Item Inspection:" in captured.out

    @pytest.mark.asyncio
    async def test_handle_breakpoint_commands_quit(self, monkeypatch: Any) -> None:
        """Test breakpoint command handling - quit command."""
        debugger = FlowDebugger()

        # Mock input to simulate user entering 'q'
        inputs = iter(["q"])

        def mock_input(prompt: str) -> str:
            return str(next(inputs))

        monkeypatch.setattr("builtins.input", mock_input)

        # Should not raise KeyboardInterrupt in test
        await debugger.handle_breakpoint_commands("test_item")

    @pytest.mark.asyncio
    async def test_handle_breakpoint_commands_unknown(
        self, monkeypatch: Any, capsys: "CaptureFixture[str]"
    ) -> None:
        """Test breakpoint command handling - unknown command."""
        debugger = FlowDebugger()

        # Mock input to simulate user entering unknown command then 'c'
        inputs = iter(["unknown", "c"])

        def mock_input(prompt: str) -> str:
            return str(next(inputs))

        monkeypatch.setattr("builtins.input", mock_input)

        await debugger.handle_breakpoint_commands("test_item")
        captured = capsys.readouterr()

        assert "Unknown command" in captured.out

    @pytest.mark.asyncio
    async def test_handle_breakpoint_commands_eof(self, monkeypatch: Any) -> None:
        """Test breakpoint command handling - EOF exception."""
        debugger = FlowDebugger()

        # Mock input to raise EOFError
        def mock_input(_):
            raise EOFError()

        monkeypatch.setattr("builtins.input", mock_input)

        # Should handle EOFError gracefully
        await debugger.handle_breakpoint_commands("test_item")

    @pytest.mark.asyncio
    async def test_handle_breakpoint_commands_keyboard_interrupt(
        self, monkeypatch: Any
    ) -> None:
        """Test breakpoint command handling - KeyboardInterrupt exception."""
        debugger = FlowDebugger()

        # Mock input to raise KeyboardInterrupt
        def mock_input(_):
            raise KeyboardInterrupt()

        monkeypatch.setattr("builtins.input", mock_input)

        # Should handle KeyboardInterrupt gracefully
        await debugger.handle_breakpoint_commands("test_item")

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

    def test_step_debugger_function(self):
        """Test step_debugger convenience function."""
        from flowengine import Flow
        from flowengine.combinators.basic import map_stream
        from flowengine.observability.debugging import step_debugger

        def increment(x: int) -> int:
            return x + 1

        flow = map_stream(increment)
        stepped_flow = step_debugger(flow)

        # Basic validation - returned flow should be a Flow
        assert isinstance(stepped_flow, Flow)
        # Should be a different instance (wrapped with debugging)
        assert stepped_flow is not flow
