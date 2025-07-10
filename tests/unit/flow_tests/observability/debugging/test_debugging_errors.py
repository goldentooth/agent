"""Tests for FlowExecutionErrorWithContext class."""

import json
from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from _pytest.capture import CaptureFixture

import pytest

from flow.observability.debugging import (
    FlowDebugger,
    FlowExecutionContext,
    FlowExecutionErrorWithContext,
    get_flow_debugger,
)


class TestFlowExecutionErrorWithContext:
    """Tests for FlowExecutionErrorWithContext class."""

    def test_error_creation(self) -> None:
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

    def test_error_captures_execution_stack(self) -> None:
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

    def test_get_debug_info(self) -> None:
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

    def test_get_debug_info_with_none_values(self) -> None:
        """Test debug info with None values."""
        error = FlowExecutionErrorWithContext("Test error")
        debug_info = error.get_debug_info()

        assert debug_info["error_message"] == "Test error"
        assert debug_info["flow_name"] is None
        assert debug_info["execution_context"] is None
        assert debug_info["original_exception"] is None
        assert debug_info["traceback"] is None
        assert debug_info["execution_stack"] == []

    def test_print_debug_info(self, capsys: "CaptureFixture[str]") -> None:
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

    def test_print_debug_info_with_execution_stack(
        self, capsys: "CaptureFixture[str]"
    ) -> None:
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

    def test_print_debug_info_minimal(self, capsys: "CaptureFixture[str]") -> None:
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
