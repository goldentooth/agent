"""Tests for FlowRegistry class."""

import _thread
import threading
from typing import Any, Dict, List

import pytest

from flow.flow import Flow
from flow.registry.main import FlowRegistry, FlowRegistryError


def add_one(x: int) -> int:
    """Simple test function that adds one."""
    return x + 1


def add_two(x: int) -> int:
    """Simple test function that adds two."""
    return x + 2


def multiply_two(x: int) -> int:
    """Simple test function that multiplies by two."""
    return x * 2


def identity(x: int) -> int:
    """Simple identity function."""
    return x


class TestFlowRegistryInitialization:
    """Test FlowRegistry initialization."""

    def test_registry_initializes_with_empty_state(self) -> None:
        """Test that registry initializes with empty flows and categories."""
        registry = FlowRegistry()
        assert registry.flows == {}
        assert registry.categories == {}
        assert registry.tags == {}
        assert registry.metadata == {}

    def test_registry_has_thread_lock(self) -> None:
        """Test that registry has thread synchronization."""
        registry = FlowRegistry()
        assert hasattr(registry, "_lock")
        assert isinstance(registry._lock, _thread.LockType)


class TestFlowRegistryRegister:
    """Test FlowRegistry.register method."""

    def test_register_flow_with_name_only(self) -> None:
        """Test registering a flow with just a name."""
        registry = FlowRegistry()
        flow = Flow.from_sync_fn(add_one)

        registry.register("test_flow", flow)

        assert "test_flow" in registry.flows
        assert registry.flows["test_flow"] is flow

    def test_register_flow_with_category(self) -> None:
        """Test registering a flow with a category."""
        registry = FlowRegistry()
        flow = Flow.from_sync_fn(add_one)

        registry.register("test_flow", flow, category="math")

        assert "test_flow" in registry.flows
        assert "math" in registry.categories
        assert "test_flow" in registry.categories["math"]

    def test_register_flow_with_tags(self) -> None:
        """Test registering a flow with tags."""
        registry = FlowRegistry()
        flow = Flow.from_sync_fn(add_one)

        registry.register("test_flow", flow, tags=["utility", "math"])

        assert "test_flow" in registry.flows
        assert "utility" in registry.tags
        assert "math" in registry.tags
        assert "test_flow" in registry.tags["utility"]
        assert "test_flow" in registry.tags["math"]

    def test_register_flow_with_metadata(self) -> None:
        """Test registering a flow with metadata."""
        registry = FlowRegistry()
        flow = Flow.from_sync_fn(add_one)
        metadata = {"description": "Adds one to input", "version": "1.0"}

        registry.register("test_flow", flow, metadata=metadata)

        assert "test_flow" in registry.flows
        assert registry.metadata["test_flow"] == metadata

    def test_register_flow_with_empty_metadata(self) -> None:
        """Test registering a flow with empty metadata dict."""
        registry = FlowRegistry()
        flow = Flow.from_sync_fn(add_one)
        metadata: Dict[str, Any] = {}

        registry.register("test_flow", flow, metadata=metadata)

        assert "test_flow" in registry.flows
        assert registry.metadata["test_flow"] == metadata

    def test_register_duplicate_name_raises_error(self) -> None:
        """Test that registering duplicate names raises an error."""
        registry = FlowRegistry()
        flow1 = Flow.from_sync_fn(add_one)
        flow2 = Flow.from_sync_fn(add_two)

        registry.register("test_flow", flow1)

        with pytest.raises(FlowRegistryError, match="Flow 'test_flow' already exists"):
            registry.register("test_flow", flow2)

    def test_register_invalid_flow_type_raises_error(self) -> None:
        """Test that registering invalid flow type raises an error."""
        registry = FlowRegistry()

        with pytest.raises(FlowRegistryError, match="Flow must be an instance of Flow"):
            registry.register("test_flow", "not a flow")  # type: ignore[arg-type]

    def test_register_empty_name_raises_error(self) -> None:
        """Test that registering with empty name raises an error."""
        registry = FlowRegistry()
        flow = Flow.from_sync_fn(add_one)

        with pytest.raises(FlowRegistryError, match="Flow name cannot be empty"):
            registry.register("", flow)

    def test_register_is_thread_safe(self) -> None:
        """Test that registration is thread-safe."""
        registry = FlowRegistry()
        flow = Flow.from_sync_fn(add_one)
        results: List[str] = []
        errors: List[str] = []

        def register_flow(name: str) -> None:
            try:
                registry.register(name, flow)
                results.append(name)
            except Exception as e:
                errors.append(str(e))

        threads = [
            threading.Thread(target=register_flow, args=(f"flow_{i}",))
            for i in range(10)
        ]

        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()

        assert len(results) == 10
        assert len(errors) == 0
        assert len(registry.flows) == 10


class TestFlowRegistryUnregister:
    """Test FlowRegistry.unregister method."""

    def test_unregister_existing_flow(self) -> None:
        """Test unregistering an existing flow."""
        registry = FlowRegistry()
        flow = Flow.from_sync_fn(add_one)

        registry.register("test_flow", flow)
        assert "test_flow" in registry.flows

        registry.unregister("test_flow")
        assert "test_flow" not in registry.flows

    def test_unregister_removes_from_categories(self) -> None:
        """Test that unregistering removes flow from categories."""
        registry = FlowRegistry()
        flow = Flow.from_sync_fn(add_one)

        registry.register("test_flow", flow, category="math")
        assert "test_flow" in registry.categories["math"]

        registry.unregister("test_flow")
        assert "test_flow" not in registry.categories["math"]

    def test_unregister_removes_from_tags(self) -> None:
        """Test that unregistering removes flow from tags."""
        registry = FlowRegistry()
        flow = Flow.from_sync_fn(add_one)

        registry.register("test_flow", flow, tags=["utility", "math"])
        assert "test_flow" in registry.tags["utility"]
        assert "test_flow" in registry.tags["math"]

        registry.unregister("test_flow")
        assert "test_flow" not in registry.tags["utility"]
        assert "test_flow" not in registry.tags["math"]

    def test_unregister_removes_metadata(self) -> None:
        """Test that unregistering removes flow metadata."""
        registry = FlowRegistry()
        flow = Flow.from_sync_fn(add_one)
        metadata = {"description": "Test flow"}

        registry.register("test_flow", flow, metadata=metadata)
        assert "test_flow" in registry.metadata

        registry.unregister("test_flow")
        assert "test_flow" not in registry.metadata

    def test_unregister_nonexistent_flow_raises_error(self) -> None:
        """Test that unregistering nonexistent flow raises an error."""
        registry = FlowRegistry()

        with pytest.raises(FlowRegistryError, match="Flow 'nonexistent' not found"):
            registry.unregister("nonexistent")


class TestFlowRegistryGet:
    """Test FlowRegistry.get method."""

    def test_get_existing_flow(self) -> None:
        """Test getting an existing flow."""
        registry = FlowRegistry()
        flow = Flow.from_sync_fn(add_one)

        registry.register("test_flow", flow)
        retrieved = registry.get("test_flow")

        assert retrieved is flow

    def test_get_nonexistent_flow_raises_error(self) -> None:
        """Test that getting nonexistent flow raises an error."""
        registry = FlowRegistry()

        with pytest.raises(FlowRegistryError, match="Flow 'nonexistent' not found"):
            registry.get("nonexistent")

    def test_get_with_default_returns_default(self) -> None:
        """Test that get with default returns default for nonexistent flow."""
        registry = FlowRegistry()
        default_flow = Flow.from_sync_fn(identity)

        retrieved = registry.get("nonexistent", default=default_flow)

        assert retrieved is default_flow

    def test_get_with_default_none_returns_none(self) -> None:
        """Test that get with default None returns None for nonexistent flow."""
        registry = FlowRegistry()

        retrieved = registry.get("nonexistent", default=None)

        assert retrieved is None


class TestFlowRegistryList:
    """Test FlowRegistry.list method."""

    def test_list_all_flows(self) -> None:
        """Test listing all flows."""
        registry = FlowRegistry()
        flow1 = Flow.from_sync_fn(add_one)
        flow2 = Flow.from_sync_fn(add_two)

        registry.register("flow1", flow1)
        registry.register("flow2", flow2)

        flows = registry.list()

        assert len(flows) == 2
        assert "flow1" in flows
        assert "flow2" in flows

    def test_list_flows_by_category(self) -> None:
        """Test listing flows by category."""
        registry = FlowRegistry()
        flow1 = Flow.from_sync_fn(add_one)
        flow2 = Flow.from_sync_fn(add_two)
        flow3 = Flow.from_sync_fn(multiply_two)

        registry.register("flow1", flow1, category="math")
        registry.register("flow2", flow2, category="math")
        registry.register("flow3", flow3, category="other")

        math_flows = registry.list(category="math")

        assert len(math_flows) == 2
        assert "flow1" in math_flows
        assert "flow2" in math_flows
        assert "flow3" not in math_flows

    def test_list_flows_empty_category(self) -> None:
        """Test listing flows for empty category."""
        registry = FlowRegistry()

        flows = registry.list(category="nonexistent")

        assert flows == []

    def test_list_flows_with_tags(self) -> None:
        """Test listing flows with specific tags."""
        registry = FlowRegistry()
        flow1 = Flow.from_sync_fn(add_one)
        flow2 = Flow.from_sync_fn(add_two)
        flow3 = Flow.from_sync_fn(multiply_two)

        registry.register("flow1", flow1, tags=["math", "utility"])
        registry.register("flow2", flow2, tags=["math"])
        registry.register("flow3", flow3, tags=["utility"])

        math_flows = registry.list(tags=["math"])

        assert len(math_flows) == 2
        assert "flow1" in math_flows
        assert "flow2" in math_flows
        assert "flow3" not in math_flows


class TestFlowRegistrySearch:
    """Test FlowRegistry.search method."""

    def test_search_by_name(self) -> None:
        """Test searching flows by name."""
        registry = FlowRegistry()
        flow1 = Flow.from_sync_fn(add_one)
        flow2 = Flow.from_sync_fn(add_two)

        registry.register("math_add", flow1)
        registry.register("string_concat", flow2)

        results = registry.search("math")

        assert len(results) == 1
        assert "math_add" in results

    def test_search_case_insensitive(self) -> None:
        """Test that search is case insensitive."""
        registry = FlowRegistry()
        flow = Flow.from_sync_fn(add_one)

        registry.register("MathAdd", flow)

        results = registry.search("math")

        assert len(results) == 1
        assert "MathAdd" in results

    def test_search_in_metadata(self) -> None:
        """Test searching in flow metadata."""
        registry = FlowRegistry()
        flow = Flow.from_sync_fn(add_one)
        metadata = {"description": "Performs mathematical addition"}

        registry.register("add_one", flow, metadata=metadata)

        results = registry.search("mathematical")

        assert len(results) == 1
        assert "add_one" in results

    def test_search_no_results(self) -> None:
        """Test search with no matching results."""
        registry = FlowRegistry()
        flow = Flow.from_sync_fn(add_one)

        registry.register("add_one", flow)

        results = registry.search("nonexistent")

        assert results == []

    def test_search_empty_query(self) -> None:
        """Test search with empty query returns all flows."""
        registry = FlowRegistry()
        flow1 = Flow.from_sync_fn(add_one)
        flow2 = Flow.from_sync_fn(add_two)

        registry.register("flow1", flow1)
        registry.register("flow2", flow2)

        results = registry.search("")

        assert len(results) == 2
        assert "flow1" in results
        assert "flow2" in results


class TestFlowRegistryClear:
    """Test FlowRegistry.clear method."""

    def test_clear_all_flows(self) -> None:
        """Test clearing all flows."""
        registry = FlowRegistry()
        flow1 = Flow.from_sync_fn(add_one)
        flow2 = Flow.from_sync_fn(add_two)

        registry.register("flow1", flow1, category="math")
        registry.register("flow2", flow2, category="other")

        registry.clear()

        assert len(registry.flows) == 0
        assert len(registry.categories) == 0
        assert len(registry.tags) == 0
        assert len(registry.metadata) == 0

    def test_clear_specific_category(self) -> None:
        """Test clearing flows from a specific category."""
        registry = FlowRegistry()
        flow1 = Flow.from_sync_fn(add_one)
        flow2 = Flow.from_sync_fn(add_two)
        flow3 = Flow.from_sync_fn(multiply_two)

        registry.register("flow1", flow1, category="math")
        registry.register("flow2", flow2, category="math")
        registry.register("flow3", flow3, category="other")

        registry.clear(category="math")

        assert "flow1" not in registry.flows
        assert "flow2" not in registry.flows
        assert "flow3" in registry.flows
        assert "math" not in registry.categories  # Category should be deleted
        assert len(registry.categories.get("other", [])) == 1

    def test_clear_nonexistent_category(self) -> None:
        """Test clearing nonexistent category does nothing."""
        registry = FlowRegistry()
        flow = Flow.from_sync_fn(add_one)

        registry.register("flow1", flow)

        registry.clear(category="nonexistent")

        assert len(registry.flows) == 1
        assert "flow1" in registry.flows


class TestFlowRegistryProperties:
    """Test FlowRegistry properties."""

    def test_flows_property(self) -> None:
        """Test that flows property returns read-only view."""
        registry = FlowRegistry()
        flow = Flow.from_sync_fn(add_one)

        registry.register("test_flow", flow)
        flows = registry.flows

        assert "test_flow" in flows
        assert flows["test_flow"] is flow

    def test_categories_property(self) -> None:
        """Test that categories property returns read-only view."""
        registry = FlowRegistry()
        flow = Flow.from_sync_fn(add_one)

        registry.register("test_flow", flow, category="math")
        categories = registry.categories

        assert "math" in categories
        assert "test_flow" in categories["math"]

    def test_tags_property(self) -> None:
        """Test that tags property returns read-only view."""
        registry = FlowRegistry()
        flow = Flow.from_sync_fn(add_one)

        registry.register("test_flow", flow, tags=["utility"])
        tags = registry.tags

        assert "utility" in tags
        assert "test_flow" in tags["utility"]

    def test_metadata_property(self) -> None:
        """Test that metadata property returns read-only view."""
        registry = FlowRegistry()
        flow = Flow.from_sync_fn(add_one)
        metadata = {"description": "Test flow"}

        registry.register("test_flow", flow, metadata=metadata)
        meta = registry.metadata

        assert "test_flow" in meta
        assert meta["test_flow"] == metadata


class TestFlowRegistryThreadSafety:
    """Test FlowRegistry thread safety."""

    def test_concurrent_register_operations(self) -> None:
        """Test concurrent register operations."""
        registry = FlowRegistry()
        flow = Flow.from_sync_fn(add_one)
        results: List[str] = []
        errors: List[str] = []

        def register_flows(start_index: int) -> None:
            for i in range(start_index, start_index + 10):
                try:
                    registry.register(f"flow_{i}", flow)
                    results.append(f"flow_{i}")
                except Exception as e:
                    errors.append(str(e))

        threads = [
            threading.Thread(target=register_flows, args=(i * 10,)) for i in range(5)
        ]

        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()

        assert len(results) == 50
        assert len(errors) == 0
        assert len(registry.flows) == 50

    def test_concurrent_mixed_operations(self) -> None:
        """Test concurrent mixed operations (register, get, list, search)."""
        registry = FlowRegistry()
        flow = Flow.from_sync_fn(add_one)

        # Pre-populate with some flows
        for i in range(10):
            registry.register(f"flow_{i}", flow)

        results: List[str] = []
        errors: List[str] = []

        def mixed_operations() -> None:
            try:
                # Register new flow
                registry.register(f"flow_{threading.current_thread().ident}", flow)
                results.append("register")

                # Get existing flow
                registry.get("flow_0")
                results.append("get")

                # List flows
                registry.list()
                results.append("list")

                # Search flows
                registry.search("flow")
                results.append("search")

            except Exception as e:
                errors.append(str(e))

        threads = [threading.Thread(target=mixed_operations) for _ in range(5)]

        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()

        assert len(results) == 20  # 4 operations * 5 threads
        assert len(errors) == 0


class TestConvenienceFunctions:
    """Test global convenience functions."""

    def test_register_flow_convenience(self) -> None:
        """Test register_flow convenience function."""
        from flow.registry import flow_registry, register_flow

        # Clear the global registry
        flow_registry.clear()

        flow = Flow.from_sync_fn(add_one)
        result = register_flow("test_flow", flow, category="math")

        assert result is flow
        assert "test_flow" in flow_registry.flows
        assert flow_registry.flows["test_flow"] is flow

    def test_get_flow_convenience(self) -> None:
        """Test get_flow convenience function."""
        from flow.registry import flow_registry, get_flow

        # Clear the global registry
        flow_registry.clear()

        flow = Flow.from_sync_fn(add_one)
        flow_registry.register("test_flow", flow)

        result = get_flow("test_flow")
        assert result is flow

        result = get_flow("nonexistent")
        assert result is None

    def test_list_flows_convenience(self) -> None:
        """Test list_flows convenience function."""
        from flow.registry import flow_registry, list_flows

        # Clear the global registry
        flow_registry.clear()

        flow1 = Flow.from_sync_fn(add_one)
        flow2 = Flow.from_sync_fn(add_two)

        flow_registry.register("flow1", flow1, category="math")
        flow_registry.register("flow2", flow2, category="other")

        # List all flows
        all_flows = list_flows()
        assert len(all_flows) == 2
        assert "flow1" in all_flows
        assert "flow2" in all_flows

        # List flows by category
        math_flows = list_flows(category="math")
        assert len(math_flows) == 1
        assert "flow1" in math_flows

    def test_search_flows_convenience(self) -> None:
        """Test search_flows convenience function."""
        from flow.registry import flow_registry, search_flows

        # Clear the global registry
        flow_registry.clear()

        flow1 = Flow.from_sync_fn(add_one)
        flow2 = Flow.from_sync_fn(add_two)

        flow_registry.register("flow1", flow1)
        flow_registry.register("flow2", flow2)

        results = search_flows("flow")
        assert len(results) == 2
        assert "flow1" in results
        assert "flow2" in results

        results = search_flows("flow1")
        assert len(results) == 1
        assert "flow1" in results

    def test_unregister_flow_convenience(self) -> None:
        """Test unregister_flow convenience function."""
        from flow.registry import flow_registry, unregister_flow

        # Clear the global registry
        flow_registry.clear()

        flow = Flow.from_sync_fn(add_one)
        flow_registry.register("test_flow", flow)

        assert "test_flow" in flow_registry.flows

        unregister_flow("test_flow")
        assert "test_flow" not in flow_registry.flows

    def test_clear_registry_convenience(self) -> None:
        """Test clear_registry convenience function."""
        from flow.registry import clear_registry, flow_registry

        # Clear the global registry
        flow_registry.clear()

        flow1 = Flow.from_sync_fn(add_one)
        flow2 = Flow.from_sync_fn(add_two)

        flow_registry.register("flow1", flow1, category="math")
        flow_registry.register("flow2", flow2, category="other")

        assert len(flow_registry.flows) == 2

        # Test clearing all flows
        clear_registry()
        assert len(flow_registry.flows) == 0

    def test_export_registry_convenience(self) -> None:
        """Test export_registry convenience function."""
        import json

        from flow.registry import export_registry, flow_registry

        # Setup registry with test data
        flow_registry.clear()
        flow1 = Flow.from_sync_fn(add_one)
        flow2 = Flow.from_sync_fn(add_two)
        flow_registry.register(
            "flow1", flow1, category="math", metadata={"desc": "adds 1"}
        )
        flow_registry.register("flow2", flow2, category="math", tags=["utility"])

        # Test JSON export
        exported = export_registry("json")
        data = json.loads(exported)

        # Verify structure and content
        assert all(
            key in data for key in ["flows", "categories", "tags", "metadata", "stats"]
        )
        assert len(data["flows"]) == 2
        assert all(name in data["flows"] for name in ["flow1", "flow2"])

    def test_import_registry_convenience(self) -> None:
        """Test import_registry convenience function."""
        from flow.registry import flow_registry, import_registry

        # Clear registry and create test data
        flow_registry.clear()
        test_data = {
            "flows": {"flow1": {"name": "flow1"}},
            "categories": {"math": ["flow1"]},
            "tags": {"utility": ["flow1"]},
            "metadata": {"flow1": {"desc": "test flow"}},
        }

        # Test import from dict
        import_registry(test_data)

        # Verify categories and tags structure imported
        assert "math" in flow_registry.categories
        assert "utility" in flow_registry.tags

    def test_import_registry_error_paths(self) -> None:
        """Test import_registry error handling."""
        import pytest

        from flow.registry import import_registry

        # Test invalid JSON string
        with pytest.raises(ValueError, match="Invalid JSON data"):
            import_registry("invalid json")

        # Test missing required keys
        with pytest.raises(ValueError, match="Missing required keys"):
            import_registry({"flows": {}})  # Missing categories, tags, metadata


class TestRegisteredFlowDecorator:
    """Test registered_flow decorator functionality."""

    def setup_method(self) -> None:
        """Setup test with clean registry."""
        from flow.registry import clear_registry

        clear_registry()

    def test_registered_flow_decorator_with_flow_instance(self) -> None:
        """Test registered_flow decorator with Flow instance."""
        from flow.registry import get_flow
        from flow.registry.main import registered_flow

        # Create a flow
        test_flow = Flow.from_sync_fn(add_one)

        # Decorate it
        @registered_flow("test_flow_instance")
        def get_flow_instance() -> Flow[int, int]:
            return test_flow

        # The decorator should register the flow and return a cached factory
        assert callable(get_flow_instance)

        # Should be registered in the global registry
        registered_flow_obj = get_flow("test_flow_instance")
        assert registered_flow_obj is not None
        assert registered_flow_obj == test_flow

    def test_registered_flow_decorator_import_from_init(self) -> None:
        """Test that registered_flow can be imported from registry package."""
        from flow.registry import registered_flow

        # Should be importable
        assert registered_flow is not None
        assert callable(registered_flow)
