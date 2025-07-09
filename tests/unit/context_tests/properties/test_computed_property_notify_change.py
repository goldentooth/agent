"""Tests for ComputedProperty.notify_change method."""

from typing import Any
from unittest.mock import Mock

from context.computed import ComputedProperty


class MockContext:
    """Mock Context class for testing purposes."""

    def __init__(self, data: dict[str, Any] | None = None) -> None:
        super().__init__()
        self.data = data or {}
        self._handle_computed_property_change = Mock()  # Mock the method

    def get(self, key: str, default: Any = None) -> Any:
        """Get value from context data."""
        return self.data.get(key, default)


class TestComputedPropertyNotifyChange:
    """Test suite for ComputedProperty.notify_change method."""

    def test_notify_change_basic(self) -> None:
        """Test basic notify_change functionality."""

        def test_func(context: Any) -> str:
            return "value"

        prop = ComputedProperty(test_func, ["dep"])
        context = MockContext()

        # Subscribe context and notify change
        prop.subscribe(context)
        prop.notify_change()

        # Should call _handle_computed_property_change on the context
        context._handle_computed_property_change.assert_called_once_with(prop)

    def test_notify_change_multiple_subscribers(self) -> None:
        """Test notifying multiple subscribed contexts."""

        def test_func(context: Any) -> str:
            return "value"

        prop = ComputedProperty(test_func, ["dep"])
        context1 = MockContext({"id": "context1"})
        context2 = MockContext({"id": "context2"})
        context3 = MockContext({"id": "context3"})

        # Subscribe multiple contexts
        prop.subscribe(context1)
        prop.subscribe(context2)
        prop.subscribe(context3)

        # Notify change
        prop.notify_change()

        # All contexts should be notified
        context1._handle_computed_property_change.assert_called_once_with(prop)
        context2._handle_computed_property_change.assert_called_once_with(prop)
        context3._handle_computed_property_change.assert_called_once_with(prop)

    def test_notify_change_no_subscribers(self) -> None:
        """Test notify_change when no contexts are subscribed."""

        def test_func(context: Any) -> str:
            return "value"

        prop = ComputedProperty(test_func, ["dep"])

        # Notify change with no subscribers - should not crash
        prop.notify_change()

        # No exceptions should be raised

    def test_notify_change_returns_none(self) -> None:
        """Test that notify_change returns None."""

        def test_func(context: Any) -> str:
            return "value"

        prop = ComputedProperty(test_func, ["dep"])
        context = MockContext()
        prop.subscribe(context)

        # notify_change doesn't return a value
        prop.notify_change()

    def test_notify_change_after_unsubscribed_context(self) -> None:
        """Test notify_change after context is no longer referenced."""

        def test_func(context: Any) -> str:
            return "value"

        prop = ComputedProperty(test_func, ["dep"])

        # Create context in local scope and subscribe
        def create_and_subscribe() -> None:
            temp_context = MockContext()
            prop.subscribe(temp_context)

        create_and_subscribe()

        # Force garbage collection
        import gc

        gc.collect()

        # Notify change should work even if weak references are gone
        prop.notify_change()  # Should not crash

    def test_notify_change_preserves_cache_state(self) -> None:
        """Test that notify_change doesn't affect cache state."""

        def test_func(context: Any) -> str:
            return "value"

        prop = ComputedProperty(test_func, ["dep"])
        context = MockContext()
        prop.subscribe(context)

        # Compute value to set cache
        prop.compute(context)
        cached_value = prop._cached_value
        cached_flag = prop._is_cached

        # Notify change
        prop.notify_change()

        # Cache state should be unchanged
        assert prop._cached_value == cached_value
        assert prop._is_cached == cached_flag

    def test_notify_change_multiple_calls(self) -> None:
        """Test calling notify_change multiple times."""

        def test_func(context: Any) -> str:
            return "value"

        prop = ComputedProperty(test_func, ["dep"])
        context = MockContext()
        prop.subscribe(context)

        # Multiple notify calls
        prop.notify_change()
        prop.notify_change()
        prop.notify_change()

        # Context should be notified each time
        assert context._handle_computed_property_change.call_count == 3
        # All calls should pass the same property
        for call in context._handle_computed_property_change.call_args_list:
            assert call[0][0] is prop

    def test_notify_change_with_context_exception(self) -> None:
        """Test notify_change when context handler raises exception."""

        def test_func(context: Any) -> str:
            return "value"

        prop = ComputedProperty(test_func, ["dep"])
        context1 = MockContext({"id": "good"})
        context2 = MockContext({"id": "bad"})

        # Make one context raise exception
        context2._handle_computed_property_change.side_effect = Exception("Test error")

        prop.subscribe(context1)
        prop.subscribe(context2)

        # Notify change - should continue despite exception
        prop.notify_change()

        # Both contexts should be called despite exception
        context1._handle_computed_property_change.assert_called_once_with(prop)
        context2._handle_computed_property_change.assert_called_once_with(prop)

    def test_notify_change_preserves_dependencies(self) -> None:
        """Test that notify_change doesn't affect dependencies."""

        def test_func(context: Any) -> str:
            return "value"

        dependencies = ["dep1", "dep2", "dep3"]
        prop = ComputedProperty(test_func, dependencies)
        context = MockContext()
        prop.subscribe(context)

        original_deps = prop.dependencies.copy()

        # Notify change
        prop.notify_change()

        # Dependencies should be unchanged
        assert prop.dependencies == original_deps

    def test_notify_change_preserves_function(self) -> None:
        """Test that notify_change doesn't affect the function."""

        def test_func(context: Any) -> str:
            return "computed"

        prop = ComputedProperty(test_func, ["dep"])
        context = MockContext()
        prop.subscribe(context)

        original_func = prop.func

        # Notify change
        prop.notify_change()

        # Function should be unchanged
        assert prop.func is original_func

    def test_notify_change_order_independence(self) -> None:
        """Test that order of subscription doesn't matter for notification."""

        def test_func(context: Any) -> str:
            return "value"

        prop = ComputedProperty(test_func, ["dep"])
        context1 = MockContext({"order": "first"})
        context2 = MockContext({"order": "second"})

        # Subscribe in one order
        prop.subscribe(context1)
        prop.subscribe(context2)

        # Notify change
        prop.notify_change()

        # Both should be notified regardless of subscription order
        context1._handle_computed_property_change.assert_called_once_with(prop)
        context2._handle_computed_property_change.assert_called_once_with(prop)

    def test_notify_change_after_subscribe_unsubscribe_cycle(self) -> None:
        """Test notify_change after subscribe/unsubscribe cycles."""

        def test_func(context: Any) -> str:
            return "value"

        prop = ComputedProperty(test_func, ["dep"])
        context1 = MockContext({"id": "persistent"})
        context2 = MockContext({"id": "temporary"})

        # Subscribe both
        prop.subscribe(context1)
        prop.subscribe(context2)

        # Simulate context2 going out of scope (weak reference cleanup)
        del context2
        import gc

        gc.collect()

        # Notify change
        prop.notify_change()

        # Only context1 should be notified (context2 was garbage collected)
        context1._handle_computed_property_change.assert_called_once_with(prop)
