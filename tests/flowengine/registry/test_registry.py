"""Tests for flow registry system - core functionality.

This module contains the TestFlowRegistry class which tests basic CRUD operations,
flow retrieval, listing, and search functionality.
"""

from flowengine import Flow
from flowengine.combinators.basic import map_stream
from flowengine.registry import (
    FlowRegistry,
    flow_registry,
    get_flow,
    list_flows,
    register_flow,
    registered_flow,
    search_flows,
)


def increment(x: int) -> int:
    """Increment a number by 1."""
    return x + 1


def double(x: int) -> int:
    """Double a number."""
    return x * 2


class TestFlowRegistry:
    """Tests for FlowRegistry class - core registry functionality."""

    def test_registry_creation(self):
        """Test basic FlowRegistry creation."""
        registry = FlowRegistry()

        assert len(registry.flows) == 0
        assert len(registry.categories) == 0

    def test_register_flow_basic(self):
        """Test registering a flow."""
        registry = FlowRegistry()
        flow = map_stream(increment)

        registry.register("increment_flow", flow)

        assert "increment_flow" in registry.flows
        assert registry.flows["increment_flow"] == flow

    def test_register_flow_with_category(self):
        """Test registering a flow with category."""
        registry = FlowRegistry()
        flow = map_stream(increment)

        registry.register("increment_flow", flow, category="math")

        assert "increment_flow" in registry.flows
        assert "math" in registry.categories
        assert "increment_flow" in registry.categories["math"]

    def test_get_flow_exists(self):
        """Test getting an existing flow."""
        registry = FlowRegistry()
        flow = map_stream(increment)
        registry.register("test_flow", flow)

        retrieved = registry.get("test_flow")

        assert retrieved == flow

    def test_list_flows_empty(self):
        """Test listing flows when registry is empty."""
        registry = FlowRegistry()

        flows = registry.list()

        assert flows == []

    def test_list_flows_all(self):
        """Test listing all flows."""
        registry = FlowRegistry()
        flow1 = map_stream(increment)
        flow2 = map_stream(double)

        registry.register("flow1", flow1)
        registry.register("flow2", flow2)

        flows = registry.list()

        assert len(flows) == 2
        assert "flow1" in flows
        assert "flow2" in flows

    def test_search_by_name(self):
        """Test searching flows by name."""
        registry = FlowRegistry()
        increment_flow = map_stream(increment)
        double_flow = map_stream(double)

        registry.register("increment_processor", increment_flow)
        registry.register("double_processor", double_flow)

        # Search for "increment"
        results = registry.search("increment")
        assert results == ["increment_processor"]

        # Search for "processor"
        results = registry.search("processor")
        assert len(results) == 2
        assert "increment_processor" in results
        assert "double_processor" in results
