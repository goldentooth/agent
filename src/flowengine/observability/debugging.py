"""Debugging and introspection utilities for Flow streams.

This module provides comprehensive debugging tools including stack traces,
execution context tracking, and flow introspection capabilities.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, TypeVar

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
