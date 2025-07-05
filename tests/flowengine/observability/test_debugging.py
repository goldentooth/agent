"""Tests for debugging and introspection utilities."""

import json
from datetime import datetime

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
