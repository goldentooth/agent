"""Debugging and introspection utilities for Flow streams.

This module provides comprehensive debugging tools including stack traces,
execution context tracking, and flow introspection capabilities.
"""

from __future__ import annotations

import json
from collections.abc import AsyncGenerator, Callable
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, TypeVar

from ..exceptions import FlowError
from ..flow import Flow

# Type aliases for debugging
DebugMetadata = dict[str, Any]
DebugData = dict[str, Any]
TraceData = list[DebugData]
AnyFlow = Flow[Any, Any]
AnyItem = Any
ItemCondition = Callable[[Any], bool]

Input = TypeVar("Input")
Output = TypeVar("Output")


@dataclass
class FlowExecutionContext:
    """Context information for a Flow execution."""

    flow_name: str
    started_at: datetime
    input_type: str | None = None
    current_item: AnyItem = None
    item_index: int = 0
    parent_flow: str | None = None
    execution_id: str = field(default_factory=lambda: f"flow_{id(object())}")
    metadata: DebugMetadata = field(default_factory=lambda: {})

    def to_dict(self) -> DebugData:
        """Convert context to dictionary for serialization."""
        return {
            "flow_name": self.flow_name,
            "started_at": self.started_at.isoformat(),
            "input_type": self.input_type,
            "current_item": (
                str(self.current_item) if self.current_item is not None else None
            ),
            "item_index": self.item_index,
            "parent_flow": self.parent_flow,
            "execution_id": self.execution_id,
            "metadata": self.metadata,
        }


# Breakpoint-related aliases (after FlowExecutionContext is defined)
BreakpointCondition = Callable[[Any, FlowExecutionContext], bool]
BreakpointRegistry = dict[str, BreakpointCondition]


class FlowDebugger:
    """Debugging system for Flow executions."""

    def __init__(self) -> None:  # pyright: ignore[reportMissingSuperCall]
        self.execution_stack: list[FlowExecutionContext] = []
        self.execution_history: list[FlowExecutionContext] = []
        self.breakpoints: BreakpointRegistry = {}
        self.debug_enabled = False
        self.max_history = 1000

    def enable_debugging(self) -> None:
        """Enable debugging mode."""
        self.debug_enabled = True

    def disable_debugging(self) -> None:
        """Disable debugging mode."""
        self.debug_enabled = False

    def add_breakpoint(
        self,
        flow_name: str,
        condition: BreakpointCondition = lambda item, _ctx: True,
    ) -> None:
        """Add a breakpoint for a specific flow.

        Args:
            flow_name: Name of the flow to break on
            condition: Function that determines when to break (item, context) -> bool
        """
        self.breakpoints[flow_name] = condition

    def remove_breakpoint(self, flow_name: str) -> None:
        """Remove a breakpoint for a flow."""
        self.breakpoints.pop(flow_name, None)

    @asynccontextmanager
    async def execution_context(
        self, flow_name: str, parent_flow: str | None = None
    ) -> AsyncGenerator[FlowExecutionContext]:
        """Context manager for tracking flow execution."""
        context = FlowExecutionContext(
            flow_name=flow_name, started_at=datetime.now(), parent_flow=parent_flow
        )

        self.execution_stack.append(context)

        try:
            yield context
        finally:
            if self.execution_stack and self.execution_stack[-1] == context:
                self.execution_stack.pop()

            # Add to history
            self.execution_history.append(context)
            if len(self.execution_history) > self.max_history:
                self.execution_history.pop(0)

    async def check_breakpoint(
        self, item: AnyItem, context: FlowExecutionContext
    ) -> None:
        """Check if a breakpoint should trigger."""
        if not self.debug_enabled:
            return

        flow_name = context.flow_name
        if flow_name in self.breakpoints:
            condition = self.breakpoints[flow_name]
            if condition(item, context):
                await self._trigger_breakpoint(item, context)

    async def _trigger_breakpoint(
        self, item: AnyItem, context: FlowExecutionContext
    ) -> None:
        """Trigger a breakpoint and enter interactive mode."""
        print(f"\n🔍 Breakpoint hit in flow: {context.flow_name}")
        print(f"   Item: {item}")
        print(f"   Index: {context.item_index}")
        print(f"   Context: {context.to_dict()}")
        print("   Commands: (c)ontinue, (s)tack, (i)nspect, (q)uit")
        await self._handle_breakpoint_commands(item)

    async def _handle_breakpoint_commands(self, item: AnyItem) -> None:
        """Handle interactive breakpoint commands."""
        while True:
            try:
                command = input("debug> ").strip().lower()
                if command in ["c", "continue"]:
                    break
                elif command in ["s", "stack"]:
                    self._print_execution_stack()
                elif command in ["i", "inspect"]:
                    self._print_item_inspection(item)
                elif command in ["q", "quit"]:
                    raise KeyboardInterrupt("Debug session terminated")
                else:
                    print("Unknown command. Use (c)ontinue, (s)tack, (i)nspect, (q)uit")
            except (EOFError, KeyboardInterrupt):
                break

    def _print_execution_stack(self) -> None:
        """Print the current execution stack."""
        print("\n📚 Execution Stack:")
        for i, context in enumerate(reversed(self.execution_stack)):
            indent = "  " * i
            print(f"{indent}└─ {context.flow_name} (item {context.item_index})")

    def _print_item_inspection(self, item: AnyItem) -> None:
        """Print detailed inspection of the current item."""
        print("\n🔬 Item Inspection:")
        print(f"   Type: {type(item).__name__}")
        print(f"   Value: {repr(item)}")
        print(f"   String: {str(item)}")
        if hasattr(item, "__dict__"):
            print(f"   Attributes: {list(item.__dict__.keys())}")

    def get_execution_trace(self) -> TraceData:
        """Get the full execution trace."""
        return [ctx.to_dict() for ctx in self.execution_history]

    def export_trace(self, filepath: str) -> None:
        """Export execution trace to a JSON file."""
        trace_data = {
            "timestamp": datetime.now().isoformat(),
            "current_stack": [ctx.to_dict() for ctx in self.execution_stack],
            "execution_history": self.get_execution_trace(),
            "breakpoints": list(self.breakpoints.keys()),
        }

        with open(filepath, "w") as f:
            json.dump(trace_data, f, indent=2)


# Global debugger instance
_flow_debugger = FlowDebugger()


class FlowExecutionErrorWithContext(FlowError):
    """Enhanced flow execution error with debugging context."""

    def __init__(
        self,
        message: str,
        flow_name: str | None = None,
        execution_context: FlowExecutionContext | None = None,
        original_exception: Exception | None = None,
    ) -> None:
        super().__init__(message)
        self.flow_name = flow_name
        self.execution_context = execution_context
        self.original_exception = original_exception

        # Capture execution stack
        self.execution_stack = list(_flow_debugger.execution_stack)

    def get_debug_info(self) -> DebugData:
        """Get comprehensive debug information."""
        import traceback

        return {
            "error_message": str(self),
            "flow_name": self.flow_name,
            "execution_context": (
                self.execution_context.to_dict() if self.execution_context else None
            ),
            "execution_stack": [ctx.to_dict() for ctx in self.execution_stack],
            "original_exception": (
                str(self.original_exception) if self.original_exception else None
            ),
            "traceback": traceback.format_exc() if self.original_exception else None,
        }

    def print_debug_info(self) -> None:
        """Print comprehensive debug information."""
        print(f"\n❌ Flow Execution Error in '{self.flow_name}'")
        print(f"   Message: {str(self)}")

        if self.execution_context:
            print(f"   Current Item: {self.execution_context.current_item}")
            print(f"   Item Index: {self.execution_context.item_index}")

        if self.execution_stack:
            print("\n📚 Execution Stack:")
            for i, ctx in enumerate(reversed(self.execution_stack)):
                indent = "  " * i
                print(f"{indent}└─ {ctx.flow_name} (item {ctx.item_index})")

        if self.original_exception:
            print("\n🔍 Original Exception:")
            print(
                f"   {type(self.original_exception).__name__}: {self.original_exception}"
            )


def debug_stream(
    breakpoint_condition: ItemCondition | None = None, log_items: bool = True
) -> Flow[Any, Any]:
    """Create a flow that adds debugging capabilities to the pipeline.

    Args:
        breakpoint_condition: Optional condition to trigger breakpoints
        log_items: Whether to log items as they pass through

    Returns:
        A flow that provides debugging and passes items through unchanged.
    """
    from collections.abc import AsyncGenerator

    async def _flow(stream: AsyncGenerator[Any, None]) -> AsyncGenerator[Any, None]:
        flow_name = "debug_stream"
        parent_flow = (
            _flow_debugger.execution_stack[-1].flow_name
            if _flow_debugger.execution_stack
            else None
        )

        async with _flow_debugger.execution_context(flow_name, parent_flow) as context:
            try:
                async for item in stream:
                    context.current_item = item
                    context.item_index += 1

                    if log_items and _flow_debugger.debug_enabled:
                        print(
                            f"🐛 Debug: {flow_name} processing item {context.item_index}: {item}"
                        )

                    # Check breakpoint
                    if breakpoint_condition and breakpoint_condition(item):
                        await _flow_debugger.check_breakpoint(item, context)

                    yield item

            except Exception as e:
                # Enhance exception with debugging context
                enhanced_error = FlowExecutionErrorWithContext(
                    f"Error in debug stream: {str(e)}",
                    flow_name=flow_name,
                    execution_context=context,
                    original_exception=e,
                )
                raise enhanced_error from e

    return Flow(_flow, name="debug")


# Convenience functions for accessing the global debugger
def get_flow_debugger() -> FlowDebugger:
    """Get the global flow debugger instance."""
    return _flow_debugger
