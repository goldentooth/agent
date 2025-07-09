"""Tests for ComputedPropertiesManager class."""

from unittest.mock import Mock, patch

import pytest

from context.computed import ComputedProperty
from context.computed_properties_manager import ComputedPropertiesManager
from context.main import Context


class TestComputedPropertiesManager:
    """Test suite for ComputedPropertiesManager class."""

    def test_init_creates_empty_manager(self) -> None:
        """Test that manager initializes with empty state."""
        manager = ComputedPropertiesManager()

        assert len(manager._computed_properties) == 0
        assert len(manager._dependency_graph) == 0
        assert manager.get_keys() == []

    def test_add_computed_property_basic(self) -> None:
        """Test adding a basic computed property."""
        manager = ComputedPropertiesManager()
        context = Mock()

        def compute_func(ctx: Context) -> str:
            return "computed_value"

        manager.add_computed_property("test_key", compute_func, None, context)

        assert manager.is_computed_property("test_key")
        assert "test_key" in manager.get_keys()
        assert isinstance(manager._computed_properties["test_key"], ComputedProperty)

    def test_add_computed_property_with_dependencies(self) -> None:
        """Test adding computed property with dependencies."""
        manager = ComputedPropertiesManager()
        context = Mock()

        def compute_func(ctx: Context) -> str:
            return "computed_value"

        manager.add_computed_property(
            "test_key", compute_func, ["dep1", "dep2"], context
        )

        assert manager.is_computed_property("test_key")
        assert manager._dependency_graph.has_dependents("dep1")
        assert manager._dependency_graph.has_dependents("dep2")
        assert "test_key" in manager._dependency_graph.get_dependents("dep1")
        assert "test_key" in manager._dependency_graph.get_dependents("dep2")

    def test_remove_computed_property_basic(self) -> None:
        """Test removing a computed property."""
        manager = ComputedPropertiesManager()
        context = Mock()

        def compute_func(ctx: Context) -> str:
            return "computed_value"

        manager.add_computed_property("test_key", compute_func, None, context)
        assert manager.is_computed_property("test_key")

        manager.remove_computed_property("test_key")
        assert not manager.is_computed_property("test_key")
        assert "test_key" not in manager.get_keys()

    def test_remove_computed_property_with_dependencies(self) -> None:
        """Test removing computed property removes dependencies."""
        manager = ComputedPropertiesManager()
        context = Mock()

        def compute_func(ctx: Context) -> str:
            return "computed_value"

        manager.add_computed_property(
            "test_key", compute_func, ["dep1", "dep2"], context
        )
        assert manager._dependency_graph.has_dependents("dep1")

        manager.remove_computed_property("test_key")
        assert not manager._dependency_graph.has_dependents("dep1")
        assert not manager._dependency_graph.has_dependents("dep2")

    def test_remove_nonexistent_property(self) -> None:
        """Test removing non-existent property doesn't raise error."""
        manager = ComputedPropertiesManager()

        # Should not raise an exception
        manager.remove_computed_property("nonexistent")

    def test_get_computed_value_success(self) -> None:
        """Test getting computed value successfully."""
        manager = ComputedPropertiesManager()
        context = Mock()

        def compute_func(ctx: Context) -> str:
            return "computed_value"

        manager.add_computed_property("test_key", compute_func, None, context)

        result = manager.get_computed_value("test_key", context)
        assert result == "computed_value"

    def test_get_computed_value_nonexistent(self) -> None:
        """Test getting computed value for non-existent key raises error."""
        manager = ComputedPropertiesManager()
        context = Mock()

        with pytest.raises(
            KeyError, match="No computed property found for key: nonexistent"
        ):
            manager.get_computed_value("nonexistent", context)

    def test_is_computed_property_true(self) -> None:
        """Test is_computed_property returns True for existing property."""
        manager = ComputedPropertiesManager()
        context = Mock()

        def compute_func(ctx: Context) -> str:
            return "computed_value"

        manager.add_computed_property("test_key", compute_func, None, context)
        assert manager.is_computed_property("test_key")

    def test_is_computed_property_false(self) -> None:
        """Test is_computed_property returns False for non-existent property."""
        manager = ComputedPropertiesManager()
        assert not manager.is_computed_property("nonexistent")

    def test_get_all_properties(self) -> None:
        """Test getting all properties returns copy."""
        manager = ComputedPropertiesManager()
        context = Mock()

        def compute_func1(ctx: Context) -> str:
            return "value1"

        def compute_func2(ctx: Context) -> str:
            return "value2"

        manager.add_computed_property("key1", compute_func1, None, context)
        manager.add_computed_property("key2", compute_func2, None, context)

        properties = manager.get_all_properties()
        assert len(properties) == 2
        assert "key1" in properties
        assert "key2" in properties
        assert isinstance(properties["key1"], ComputedProperty)
        assert isinstance(properties["key2"], ComputedProperty)

        # Should be a copy
        assert properties is not manager._computed_properties

    def test_invalidate_property(self) -> None:
        """Test invalidating a property."""
        manager = ComputedPropertiesManager()
        context = Mock()

        def compute_func(ctx: Context) -> str:
            return "computed_value"

        manager.add_computed_property("test_key", compute_func, None, context)

        # Mock the invalidate method to verify it's called
        with patch.object(
            manager._computed_properties["test_key"], "invalidate"
        ) as mock_invalidate:
            manager.invalidate_property("test_key")
            mock_invalidate.assert_called_once()

    def test_invalidate_nonexistent_property(self) -> None:
        """Test invalidating non-existent property doesn't raise error."""
        manager = ComputedPropertiesManager()

        # Should not raise an exception
        manager.invalidate_property("nonexistent")

    def test_invalidate_dependent_properties(self) -> None:
        """Test invalidating dependent properties."""
        manager = ComputedPropertiesManager()
        context = Mock()

        def compute_func(ctx: Context) -> str:
            return "computed_value"

        # Add a computed property that depends on "base_key"
        manager.add_computed_property(
            "computed_key", compute_func, ["base_key"], context
        )

        # Mock the invalidate and notify_change methods
        computed_prop = manager._computed_properties["computed_key"]
        with patch.object(computed_prop, "invalidate") as mock_invalidate:
            with patch.object(computed_prop, "notify_change") as mock_notify:
                manager.invalidate_dependent_properties("base_key")

                mock_invalidate.assert_called_once()
                mock_notify.assert_called_once()

    def test_invalidate_dependent_properties_no_dependents(self) -> None:
        """Test invalidating when no dependents exist."""
        manager = ComputedPropertiesManager()

        # Should not raise an exception
        manager.invalidate_dependent_properties("nonexistent")

    def test_handle_property_change(self) -> None:
        """Test handling property change."""
        manager = ComputedPropertiesManager()
        context = Mock()
        context._emit_change_event = Mock()

        def compute_func(ctx: Context) -> str:
            return "new_value"

        manager.add_computed_property("test_key", compute_func, ["dep1"], context)
        computed_prop = manager._computed_properties["test_key"]

        # Mock the property to simulate cached state
        computed_prop._is_cached = True
        computed_prop._cached_value = "old_value"

        # Mock invalidate_dependent_properties to verify it's called
        with patch.object(
            manager, "invalidate_dependent_properties"
        ) as mock_invalidate:
            manager.handle_property_change(computed_prop, context)

            # Verify emit_change_event was called
            context._emit_change_event.assert_called_once()
            args = context._emit_change_event.call_args[0]
            assert args[0] == "test_key"  # key
            assert args[1] == "new_value"  # new_value

            # Verify invalidate_dependent_properties was called
            mock_invalidate.assert_called_once_with("test_key")

    def test_handle_property_change_no_context_emit(self) -> None:
        """Test handling property change when context doesn't have emit method."""
        manager = ComputedPropertiesManager()
        context = Mock()
        # Don't add _emit_change_event to context

        def compute_func(ctx: Context) -> str:
            return "new_value"

        manager.add_computed_property("test_key", compute_func, None, context)
        computed_prop = manager._computed_properties["test_key"]

        # Should not raise an exception
        manager.handle_property_change(computed_prop, context)

    def test_handle_property_change_nonexistent_property(self) -> None:
        """Test handling change for non-existent property."""
        manager = ComputedPropertiesManager()
        context = Mock()

        # Create a computed property that's not in the manager
        mock_computed_prop = Mock(spec=ComputedProperty)

        # Should not raise an exception
        manager.handle_property_change(mock_computed_prop, context)

    def test_get_keys(self) -> None:
        """Test getting all keys."""
        manager = ComputedPropertiesManager()
        context = Mock()

        def compute_func(ctx: Context) -> str:
            return "value"

        manager.add_computed_property("key1", compute_func, None, context)
        manager.add_computed_property("key2", compute_func, None, context)

        keys = manager.get_keys()
        assert len(keys) == 2
        assert "key1" in keys
        assert "key2" in keys

    def test_copy_to_manager(self) -> None:
        """Test copying to another manager."""
        manager1 = ComputedPropertiesManager()
        manager2 = ComputedPropertiesManager()
        context = Mock()

        def compute_func(ctx: Context) -> str:
            return "value"

        # Add properties to first manager
        manager1.add_computed_property("key1", compute_func, ["dep1"], context)
        manager1.add_computed_property("key2", compute_func, ["dep2"], context)

        # Copy to second manager
        manager1.copy_to_manager(manager2)

        # Verify properties were copied
        assert manager2.is_computed_property("key1")
        assert manager2.is_computed_property("key2")
        assert manager2._dependency_graph.has_dependents("dep1")
        assert manager2._dependency_graph.has_dependents("dep2")

        # Verify they are separate instances
        assert manager2._computed_properties is not manager1._computed_properties

    def test_clear(self) -> None:
        """Test clearing all properties."""
        manager = ComputedPropertiesManager()
        context = Mock()

        def compute_func(ctx: Context) -> str:
            return "value"

        manager.add_computed_property("key1", compute_func, ["dep1"], context)
        assert len(manager.get_keys()) == 1
        assert manager._dependency_graph.has_dependents("dep1")

        manager.clear()
        assert len(manager.get_keys()) == 0
        assert not manager._dependency_graph.has_dependents("dep1")

    def test_multiple_properties_same_dependency(self) -> None:
        """Test multiple properties depending on same key."""
        manager = ComputedPropertiesManager()
        context = Mock()

        def compute_func1(ctx: Context) -> str:
            return "value1"

        def compute_func2(ctx: Context) -> str:
            return "value2"

        manager.add_computed_property("key1", compute_func1, ["shared_dep"], context)
        manager.add_computed_property("key2", compute_func2, ["shared_dep"], context)

        dependents = manager._dependency_graph.get_dependents("shared_dep")
        assert len(dependents) == 2
        assert "key1" in dependents
        assert "key2" in dependents

    def test_computed_property_without_dependencies(self) -> None:
        """Test computed property without explicit dependencies."""
        manager = ComputedPropertiesManager()
        context = Mock()

        def compute_func(ctx: Context) -> str:
            return "value"

        manager.add_computed_property("key1", compute_func, None, context)

        # Should work without dependencies
        assert manager.is_computed_property("key1")
        assert manager.get_computed_value("key1", context) == "value"

    def test_computed_property_with_empty_dependencies(self) -> None:
        """Test computed property with empty dependencies list."""
        manager = ComputedPropertiesManager()
        context = Mock()

        def compute_func(ctx: Context) -> str:
            return "value"

        manager.add_computed_property("key1", compute_func, [], context)

        # Should work with empty dependencies
        assert manager.is_computed_property("key1")
        assert manager.get_computed_value("key1", context) == "value"
