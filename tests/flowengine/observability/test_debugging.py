"""Tests for debugging and introspection utilities."""

import json
from datetime import datetime

import pytest

from flowengine.observability.debugging import FlowExecutionContext


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
