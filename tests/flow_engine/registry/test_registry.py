"""Tests for flow registry system."""

from goldentooth_agent.flow_engine import Flow
from goldentooth_agent.flow_engine.combinators.basic import map_stream
from goldentooth_agent.flow_engine.registry import (
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
    """Tests for FlowRegistry class."""

    def test_registry_creation(self):
        """Test basic FlowRegistry creation."""
        registry = FlowRegistry()

        assert len(registry._flows) == 0
        assert len(registry._categories) == 0

    def test_register_flow_basic(self):
        """Test registering a flow."""
        registry = FlowRegistry()
        flow = map_stream(increment)

        result = registry.register("increment_flow", flow)

        assert result == flow  # Should return the flow for chaining
        assert "increment_flow" in registry._flows
        assert registry._flows["increment_flow"] == flow

    def test_register_flow_with_category(self):
        """Test registering a flow with category."""
        registry = FlowRegistry()
        flow = map_stream(increment)

        registry.register("increment_flow", flow, category="math")

        assert "increment_flow" in registry._flows
        assert "math" in registry._categories
        assert "increment_flow" in registry._categories["math"]

    def test_register_multiple_flows_same_category(self):
        """Test registering multiple flows in same category."""
        registry = FlowRegistry()
        increment_flow = map_stream(increment)
        double_flow = map_stream(double)

        registry.register("increment_flow", increment_flow, category="math")
        registry.register("double_flow", double_flow, category="math")

        assert len(registry._categories["math"]) == 2
        assert "increment_flow" in registry._categories["math"]
        assert "double_flow" in registry._categories["math"]

    def test_register_flow_no_duplicate_in_category(self):
        """Test that registering same flow twice in category doesn't create duplicates."""
        registry = FlowRegistry()
        flow = map_stream(increment)

        registry.register("increment_flow", flow, category="math")
        registry.register("increment_flow", flow, category="math")  # Register again

        # Should still only have one entry
        assert len(registry._categories["math"]) == 1

    def test_get_flow_exists(self):
        """Test getting an existing flow."""
        registry = FlowRegistry()
        flow = map_stream(increment)
        registry.register("test_flow", flow)

        retrieved = registry.get("test_flow")

        assert retrieved == flow

    def test_get_flow_not_exists(self):
        """Test getting a non-existent flow."""
        registry = FlowRegistry()

        retrieved = registry.get("nonexistent")

        assert retrieved is None

    def test_list_flows_empty(self):
        """Test listing flows when registry is empty."""
        registry = FlowRegistry()

        flows = registry.list_flows()

        assert flows == []

    def test_list_flows_all(self):
        """Test listing all flows."""
        registry = FlowRegistry()
        flow1 = map_stream(increment)
        flow2 = map_stream(double)

        registry.register("flow1", flow1)
        registry.register("flow2", flow2)

        flows = registry.list_flows()

        assert len(flows) == 2
        assert "flow1" in flows
        assert "flow2" in flows

    def test_list_flows_by_category(self):
        """Test listing flows by category."""
        registry = FlowRegistry()
        math_flow = map_stream(increment)
        text_flow = Flow(lambda s: s, name="text_processor")

        registry.register("math_flow", math_flow, category="math")
        registry.register("text_flow", text_flow, category="text")

        math_flows = registry.list_flows(category="math")
        text_flows = registry.list_flows(category="text")

        assert math_flows == ["math_flow"]
        assert text_flows == ["text_flow"]

    def test_list_flows_nonexistent_category(self):
        """Test listing flows for non-existent category."""
        registry = FlowRegistry()

        flows = registry.list_flows(category="nonexistent")

        assert flows == []

    def test_list_categories_empty(self):
        """Test listing categories when none exist."""
        registry = FlowRegistry()

        categories = registry.list_categories()

        assert categories == []

    def test_list_categories(self):
        """Test listing categories."""
        registry = FlowRegistry()
        flow1 = map_stream(increment)
        flow2 = Flow(lambda s: s, name="text_processor")

        registry.register("flow1", flow1, category="math")
        registry.register("flow2", flow2, category="text")

        categories = registry.list_categories()

        assert len(categories) == 2
        assert "math" in categories
        assert "text" in categories

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

    def test_search_by_metadata(self):
        """Test searching flows by metadata."""
        registry = FlowRegistry()

        # Create flow with metadata
        flow = Flow(lambda s: s, name="test_flow")
        flow.metadata = {
            "description": "Processes numbers",
            "tags": ["math", "utility"],
        }

        registry.register("test_flow", flow)

        # Search by metadata value
        results = registry.search("numbers")
        assert "test_flow" in results

        # Search by metadata key
        results = registry.search("description")
        assert "test_flow" in results

        # Search by tag
        results = registry.search("math")
        assert "test_flow" in results

    def test_search_case_insensitive(self):
        """Test that search is case insensitive."""
        registry = FlowRegistry()
        flow = map_stream(increment)
        registry.register("INCREMENT_FLOW", flow)

        results = registry.search("increment")
        assert "INCREMENT_FLOW" in results

        results = registry.search("FLOW")
        assert "INCREMENT_FLOW" in results

    def test_search_no_matches(self):
        """Test searching with no matches."""
        registry = FlowRegistry()
        flow = map_stream(increment)
        registry.register("test_flow", flow)

        results = registry.search("nonexistent")
        assert results == []

    def test_remove_flow_exists(self):
        """Test removing an existing flow."""
        registry = FlowRegistry()
        flow = map_stream(increment)
        registry.register("test_flow", flow, category="math")

        result = registry.remove("test_flow")

        assert result is True
        assert "test_flow" not in registry._flows
        assert "test_flow" not in registry._categories["math"]

    def test_remove_flow_not_exists(self):
        """Test removing a non-existent flow."""
        registry = FlowRegistry()

        result = registry.remove("nonexistent")

        assert result is False

    def test_remove_flow_from_multiple_categories(self):
        """Test removing flow from multiple categories."""
        registry = FlowRegistry()
        flow = map_stream(increment)

        # Register in two different contexts (this simulates the flow being in multiple categories)
        registry.register("multi_flow", flow, category="math")
        registry._categories.setdefault("utility", []).append("multi_flow")

        registry.remove("multi_flow")

        assert "multi_flow" not in registry._flows
        assert "multi_flow" not in registry._categories["math"]
        assert "multi_flow" not in registry._categories["utility"]

    def test_clear_all(self):
        """Test clearing all flows."""
        registry = FlowRegistry()
        flow1 = map_stream(increment)
        flow2 = map_stream(double)

        registry.register("flow1", flow1, category="math")
        registry.register("flow2", flow2, category="text")

        registry.clear()

        assert len(registry._flows) == 0
        assert len(registry._categories) == 0

    def test_clear_by_category(self):
        """Test clearing flows by category."""
        registry = FlowRegistry()
        math_flow = map_stream(increment)
        text_flow = Flow(lambda s: s, name="text_processor")

        registry.register("math_flow", math_flow, category="math")
        registry.register("text_flow", text_flow, category="text")

        registry.clear(category="math")

        assert "math_flow" not in registry._flows
        assert "math" not in registry._categories
        assert "text_flow" in registry._flows  # Should still exist
        assert "text" in registry._categories

    def test_clear_nonexistent_category(self):
        """Test clearing a non-existent category."""
        registry = FlowRegistry()
        flow = map_stream(increment)
        registry.register("test_flow", flow)

        # Should not raise error
        registry.clear(category="nonexistent")

        # Original flow should still exist
        assert "test_flow" in registry._flows

    def test_info_exists(self):
        """Test getting info for existing flow."""
        registry = FlowRegistry()
        flow = map_stream(increment)
        flow.metadata = {"description": "Increments numbers"}

        registry.register("increment_flow", flow, category="math")

        info = registry.info("increment_flow")

        assert info is not None
        assert info["name"] == "increment_flow"
        assert info["flow_name"] == flow.name
        assert info["function_name"] != "anonymous"  # Should have function name
        assert info["metadata"]["description"] == "Increments numbers"
        assert "math" in info["categories"]
        assert "repr" in info

    def test_info_not_exists(self):
        """Test getting info for non-existent flow."""
        registry = FlowRegistry()

        info = registry.info("nonexistent")

        assert info is None

    def test_info_no_metadata(self):
        """Test getting info for flow without metadata."""
        registry = FlowRegistry()
        flow = Flow(lambda s: s, name="simple_flow")

        registry.register("simple_flow", flow)

        info = registry.info("simple_flow")

        assert info is not None
        assert info["metadata"] == {}
        assert info["categories"] == []

    def test_info_multiple_categories(self):
        """Test getting info for flow in multiple categories."""
        registry = FlowRegistry()
        flow = map_stream(increment)

        registry.register("multi_flow", flow, category="math")
        # Manually add to another category
        registry._categories.setdefault("utility", []).append("multi_flow")

        info = registry.info("multi_flow")

        assert len(info["categories"]) == 2
        assert "math" in info["categories"]
        assert "utility" in info["categories"]

    def test_print_registry_empty(self, capsys):
        """Test printing empty registry."""
        registry = FlowRegistry()

        registry.print_registry()

        captured = capsys.readouterr()
        assert "Flow Registry" in captured.out
        assert "(empty)" in captured.out

    def test_print_registry_with_flows(self, capsys):
        """Test printing registry with flows."""
        registry = FlowRegistry()
        math_flow = map_stream(increment)
        uncategorized_flow = Flow(lambda s: s, name="uncategorized")

        registry.register("math_flow", math_flow, category="math")
        registry.register("uncategorized_flow", uncategorized_flow)

        registry.print_registry()

        captured = capsys.readouterr()
        output = captured.out

        assert "Flow Registry" in output
        assert "math" in output
        assert "math_flow" in output
        assert "Uncategorized" in output
        assert "uncategorized_flow" in output


class TestGlobalFunctions:
    """Tests for global convenience functions."""

    def test_register_flow_function(self):
        """Test register_flow convenience function."""
        # Clear global registry first
        flow_registry.clear()

        flow = map_stream(increment)
        result = register_flow("test_flow", flow, category="test")

        assert result == flow
        assert flow_registry.get("test_flow") == flow

    def test_get_flow_function(self):
        """Test get_flow convenience function."""
        flow_registry.clear()

        flow = map_stream(increment)
        flow_registry.register("test_flow", flow)

        retrieved = get_flow("test_flow")
        assert retrieved == flow

        retrieved = get_flow("nonexistent")
        assert retrieved is None

    def test_list_flows_function(self):
        """Test list_flows convenience function."""
        flow_registry.clear()

        flow1 = map_stream(increment)
        flow2 = map_stream(double)

        flow_registry.register("flow1", flow1, category="math")
        flow_registry.register("flow2", flow2, category="math")

        all_flows = list_flows()
        assert len(all_flows) == 2

        math_flows = list_flows(category="math")
        assert len(math_flows) == 2

    def test_search_flows_function(self):
        """Test search_flows convenience function."""
        flow_registry.clear()

        flow = map_stream(increment)
        flow_registry.register("increment_processor", flow)

        results = search_flows("increment")
        assert "increment_processor" in results


class TestRegisteredFlowDecorator:
    """Tests for registered_flow decorator."""

    def test_registered_flow_decorator_basic(self):
        """Test basic registered_flow decorator usage."""
        flow_registry.clear()

        @registered_flow("decorated_flow")
        def create_flow():
            return map_stream(increment)

        flow = create_flow()

        # Flow should be registered
        assert flow_registry.get("decorated_flow") == flow

    def test_registered_flow_decorator_with_category(self):
        """Test registered_flow decorator with category."""
        flow_registry.clear()

        @registered_flow("categorized_flow", category="decorators")
        def create_flow():
            return map_stream(double)

        flow = create_flow()

        # Flow should be registered with category
        assert flow_registry.get("categorized_flow") == flow
        assert "categorized_flow" in flow_registry.list_flows(category="decorators")

    def test_registered_flow_decorator_returns_flow(self):
        """Test that decorator returns the original flow."""
        flow_registry.clear()

        original_flow = map_stream(increment)

        @registered_flow("return_test")
        def create_flow():
            return original_flow

        returned_flow = create_flow()

        assert returned_flow == original_flow
        assert flow_registry.get("return_test") == original_flow

    def test_registered_flow_decorator_chaining(self):
        """Test that decorator can be used with other decorators."""
        flow_registry.clear()

        # This tests that the decorator works with Flow class methods
        @registered_flow("chained_flow", category="test")
        @Flow.from_sync_fn
        def process_number(x: int) -> int:
            return x * 3

        # The flow should be registered
        registered_flow_obj = flow_registry.get("chained_flow")
        assert registered_flow_obj is not None

        # Verify it works (this would require async execution in real usage)
        assert "chained_flow" in flow_registry.list_flows()


class TestFlowRegistryIntegration:
    """Integration tests for flow registry functionality."""

    def test_registry_workflow(self):
        """Test a complete registry workflow."""
        registry = FlowRegistry()

        # Register flows
        increment_flow = map_stream(increment)
        double_flow = map_stream(double)

        registry.register("increment", increment_flow, category="math")
        registry.register("double", double_flow, category="math")
        registry.register(
            "identity", Flow(lambda s: s, name="identity"), category="utility"
        )

        # List and search
        all_flows = registry.list_flows()
        assert len(all_flows) == 3

        math_flows = registry.list_flows(category="math")
        assert len(math_flows) == 2

        search_results = registry.search("inc")
        assert "increment" in search_results

        # Get info
        info = registry.info("increment")
        assert info["categories"] == ["math"]

        # Remove and verify
        registry.remove("double")
        assert len(registry.list_flows(category="math")) == 1

        # Clear category
        registry.clear(category="math")
        assert len(registry.list_flows()) == 1  # Only utility flow remains

    def test_registry_edge_cases(self):
        """Test edge cases and error conditions."""
        registry = FlowRegistry()

        # Register flow with empty name
        flow = map_stream(increment)
        registry.register("", flow)
        assert registry.get("") == flow

        # Register same name twice (should overwrite)
        flow1 = map_stream(increment)
        flow2 = map_stream(double)
        registry.register("same_name", flow1)
        registry.register("same_name", flow2)
        assert registry.get("same_name") == flow2

        # Search with empty query
        results = registry.search("")
        assert len(results) == len(registry._flows)  # All flows match empty string

        # Operations on empty registry
        empty_registry = FlowRegistry()
        assert empty_registry.list_flows() == []
        assert empty_registry.list_categories() == []
        assert empty_registry.search("anything") == []
        assert empty_registry.remove("anything") is False
        assert empty_registry.info("anything") is None
