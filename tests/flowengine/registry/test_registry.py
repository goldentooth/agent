"""Tests for flow registry system - core functionality.

This module contains the TestFlowRegistry class which tests basic CRUD operations,
flow retrieval, listing, and search functionality.
"""

from typing import Any

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


class TestRegistryFiltering:
    """Tests for FlowRegistry filtering and search functionality."""

    def _setup_category_registry(self) -> FlowRegistry:
        """Helper to set up registry with categorized flows."""
        registry = FlowRegistry()

        def text_upper(x: str) -> str:
            return x.upper()

        def identity(x: int) -> int:
            return x

        math_flow1 = map_stream(increment)
        math_flow2 = map_stream(double)
        text_flow = Flow.from_sync_fn(text_upper)
        utility_flow = Flow.from_sync_fn(identity)

        registry.register("increment", math_flow1, category="math")
        registry.register("double", math_flow2, category="math")
        registry.register("uppercase", text_flow, category="text")
        registry.register("identity", utility_flow, category="utility")
        return registry

    def test_category_filtering(self):
        """Test filtering flows by category."""
        registry = self._setup_category_registry()

        math_flows = registry.list(category="math")
        assert len(math_flows) == 2
        assert "increment" in math_flows
        assert "double" in math_flows

        text_flows = registry.list(category="text")
        assert len(text_flows) == 1
        assert "uppercase" in text_flows

        utility_flows = registry.list(category="utility")
        assert len(utility_flows) == 1
        assert "identity" in utility_flows

        # Test non-existent category
        empty_flows = registry.list(category="nonexistent")
        assert len(empty_flows) == 0

    def _setup_tag_registry(self) -> FlowRegistry:
        """Helper to set up registry with tagged flows for tag filtering tests."""
        registry = FlowRegistry()

        def text_upper(x: str) -> str:
            return x.upper()

        def identity(x: int) -> int:
            return x

        flow1 = map_stream(increment)
        flow2 = map_stream(double)
        flow3 = Flow.from_sync_fn(text_upper)
        flow4 = Flow.from_sync_fn(identity)

        registry.register("increment", flow1, tags=["math", "simple"])
        registry.register("double", flow2, tags=["math", "multiply"])
        registry.register("uppercase", flow3, tags=["text", "simple"])
        registry.register("identity", flow4, tags=["utility", "simple"])
        return registry

    def test_single_tag_filtering(self):
        """Test filtering flows by single tags."""
        registry = self._setup_tag_registry()

        math_flows = registry.list(tags=["math"])
        assert len(math_flows) == 2
        assert "increment" in math_flows
        assert "double" in math_flows

        simple_flows = registry.list(tags=["simple"])
        assert len(simple_flows) == 3
        assert "increment" in simple_flows
        assert "uppercase" in simple_flows
        assert "identity" in simple_flows

    def test_multiple_tag_filtering(self):
        """Test filtering flows by multiple tags (AND operation)."""
        registry = self._setup_tag_registry()

        math_simple_flows = registry.list(tags=["math", "simple"])
        assert len(math_simple_flows) == 1
        assert "increment" in math_simple_flows

        # Test non-existent tag
        empty_flows = registry.list(tags=["nonexistent"])
        assert len(empty_flows) == 0

    def _setup_combined_registry(self) -> FlowRegistry:
        """Helper to set up registry with both categories and tags."""
        registry = FlowRegistry()

        def text_upper(x: str) -> str:
            return x.upper()

        flow1 = map_stream(increment)
        flow2 = map_stream(double)
        flow3 = Flow.from_sync_fn(text_upper)

        registry.register("increment", flow1, category="math", tags=["simple", "basic"])
        registry.register("double", flow2, category="math", tags=["multiply", "basic"])
        registry.register(
            "uppercase", flow3, category="text", tags=["simple", "transform"]
        )
        return registry

    def test_category_precedence_over_tags(self):
        """Test that category takes precedence over tags in filtering."""
        registry = self._setup_combined_registry()

        math_flows = registry.list(category="math", tags=["simple"])
        assert len(math_flows) == 2
        assert "increment" in math_flows
        assert "double" in math_flows

        text_flows = registry.list(category="text")
        assert len(text_flows) == 1
        assert "uppercase" in text_flows

    def test_tag_filtering_without_category(self):
        """Test tag filtering when no category is specified."""
        registry = self._setup_combined_registry()

        basic_flows = registry.list(tags=["basic"])
        assert len(basic_flows) == 2
        assert "increment" in basic_flows
        assert "double" in basic_flows

        simple_flows = registry.list(tags=["simple"])
        assert len(simple_flows) == 2
        assert "increment" in simple_flows
        assert "uppercase" in simple_flows

    def _setup_search_registry(self) -> FlowRegistry:
        """Helper to set up registry with metadata for search tests."""
        registry = FlowRegistry()

        def text_upper(x: str) -> str:
            return x.upper()

        flow1 = map_stream(increment)
        flow2 = map_stream(double)
        flow3 = Flow.from_sync_fn(text_upper)

        registry.register(
            "increment_processor",
            flow1,
            category="math",
            tags=["simple", "arithmetic"],
            metadata={"description": "Increments numbers by one", "author": "test"},
        )
        registry.register(
            "double_multiplier",
            flow2,
            category="math",
            tags=["multiply", "arithmetic"],
            metadata={"description": "Doubles the input value", "author": "test"},
        )
        registry.register(
            "text_transformer",
            flow3,
            category="text",
            tags=["transform", "string"],
            metadata={"description": "Converts text to uppercase", "author": "demo"},
        )
        return registry

    def test_search_by_name(self):
        """Test searching flows by name."""
        registry = self._setup_search_registry()

        name_results = registry.search("processor")
        assert len(name_results) == 1
        assert "increment_processor" in name_results

    def test_search_by_metadata(self):
        """Test searching flows by metadata."""
        registry = self._setup_search_registry()

        # Test search by metadata description
        number_results = registry.search("numbers")
        assert len(number_results) == 1
        assert "increment_processor" in number_results

        # Test search by metadata author
        test_results = registry.search("test")
        assert len(test_results) == 2
        assert "increment_processor" in test_results
        assert "double_multiplier" in test_results

    def test_search_patterns(self):
        """Test search pattern matching."""
        registry = self._setup_search_registry()

        # Test search by partial name match
        multi_results = registry.search("multi")
        assert len(multi_results) == 1
        assert "double_multiplier" in multi_results

        # Test case-insensitive search
        case_results = registry.search("TEXT")
        assert len(case_results) == 1
        assert "text_transformer" in case_results

    def test_search_edge_cases(self):
        """Test search edge cases."""
        registry = self._setup_search_registry()

        # Test search with no matches
        no_results = registry.search("nonexistent")
        assert len(no_results) == 0

        # Test empty search returns all flows
        all_results = registry.search("")
        assert len(all_results) == 3
        assert "increment_processor" in all_results
        assert "double_multiplier" in all_results
        assert "text_transformer" in all_results
