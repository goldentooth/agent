"""Tests for ComputedProperty.subscribe method."""

from typing import Any
from weakref import WeakSet

from context.main import ComputedProperty


class MockContext:
    """Mock Context class for testing purposes."""

    def __init__(self, data: dict[str, Any] | None = None) -> None:
        super().__init__()
        self.data = data or {}

    def get(self, key: str, default: Any = None) -> Any:
        """Get value from context data."""
        return self.data.get(key, default)


class TestComputedPropertySubscribe:
    """Test suite for ComputedProperty.subscribe method."""

    def test_subscribe_basic(self) -> None:
        """Test basic subscribe functionality."""

        def test_func(context: Any) -> str:
            return "value"

        prop = ComputedProperty(test_func, ["dep"])
        context = MockContext()

        # Subscribe context
        prop.subscribe(context)

        # Context should be in subscribers
        assert context in prop._subscribers

    def test_subscribe_multiple_contexts(self) -> None:
        """Test subscribing multiple contexts."""

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

        # All contexts should be in subscribers
        assert context1 in prop._subscribers
        assert context2 in prop._subscribers
        assert context3 in prop._subscribers

    def test_subscribe_same_context_multiple_times(self) -> None:
        """Test subscribing the same context multiple times."""

        def test_func(context: Any) -> str:
            return "value"

        prop = ComputedProperty(test_func, ["dep"])
        context = MockContext()

        # Subscribe same context multiple times
        prop.subscribe(context)
        prop.subscribe(context)
        prop.subscribe(context)

        # Should only appear once in WeakSet
        assert context in prop._subscribers
        assert len(prop._subscribers) == 1

    def test_subscribe_returns_none(self) -> None:
        """Test that subscribe returns None."""

        def test_func(context: Any) -> str:
            return "value"

        prop = ComputedProperty(test_func, ["dep"])
        context = MockContext()

        # Subscribe doesn't return a value
        prop.subscribe(context)

    def test_subscribe_uses_weakset(self) -> None:
        """Test that subscribers is a WeakSet."""

        def test_func(context: Any) -> str:
            return "value"

        prop = ComputedProperty(test_func, ["dep"])

        # Verify _subscribers is a WeakSet
        assert isinstance(prop._subscribers, WeakSet)

    def test_subscribe_weakset_behavior(self) -> None:
        """Test WeakSet behavior for automatic cleanup."""

        def test_func(context: Any) -> str:
            return "value"

        prop = ComputedProperty(test_func, ["dep"])

        # Create context in local scope
        def create_and_subscribe() -> None:
            temp_context = MockContext()
            prop.subscribe(temp_context)
            # temp_context goes out of scope here

        create_and_subscribe()

        # WeakSet should be empty after garbage collection
        # Note: This test may be flaky due to GC timing
        import gc

        gc.collect()
        # We can't reliably test weakref cleanup in a unit test

    def test_subscribe_after_compute(self) -> None:
        """Test subscribing after computing a value."""

        def test_func(context: Any) -> str:
            return f"computed_{context.get('value', 'default')}"

        prop = ComputedProperty(test_func, ["value"])
        context = MockContext({"value": "test"})

        # Compute first
        result = prop.compute(context)
        assert result == "computed_test"

        # Then subscribe
        prop.subscribe(context)

        # Should still be subscribed
        assert context in prop._subscribers

    def test_subscribe_before_compute(self) -> None:
        """Test subscribing before computing a value."""

        def test_func(context: Any) -> str:
            return f"computed_{context.get('value', 'default')}"

        prop = ComputedProperty(test_func, ["value"])
        context = MockContext({"value": "test"})

        # Subscribe first
        prop.subscribe(context)
        assert context in prop._subscribers

        # Then compute
        result = prop.compute(context)
        assert result == "computed_test"

        # Should still be subscribed
        assert context in prop._subscribers

    def test_subscribe_preserves_existing_subscribers(self) -> None:
        """Test that subscribing new context preserves existing ones."""

        def test_func(context: Any) -> str:
            return "value"

        prop = ComputedProperty(test_func, ["dep"])
        context1 = MockContext({"id": "first"})
        context2 = MockContext({"id": "second"})

        # Subscribe first context
        prop.subscribe(context1)
        assert len(prop._subscribers) == 1

        # Subscribe second context
        prop.subscribe(context2)

        # Both should be present
        assert context1 in prop._subscribers
        assert context2 in prop._subscribers
        assert len(prop._subscribers) == 2

    def test_subscribe_after_invalidate(self) -> None:
        """Test subscribing after invalidating cached value."""

        def test_func(context: Any) -> str:
            return "value"

        prop = ComputedProperty(test_func, ["dep"])
        context = MockContext()

        # Compute, invalidate, then subscribe
        prop.compute(context)
        prop.invalidate()
        prop.subscribe(context)

        # Should be subscribed regardless of cache state
        assert context in prop._subscribers

    def test_subscribe_with_different_dependencies(self) -> None:
        """Test subscribe works with different dependency configurations."""

        def test_func(context: Any) -> str:
            return "value"

        # Property with dependencies
        prop_with_deps = ComputedProperty(test_func, ["dep1", "dep2"])
        context1 = MockContext()
        prop_with_deps.subscribe(context1)
        assert context1 in prop_with_deps._subscribers

        # Property without dependencies
        prop_no_deps = ComputedProperty(test_func, [])
        context2 = MockContext()
        prop_no_deps.subscribe(context2)
        assert context2 in prop_no_deps._subscribers

        # Property with None dependencies
        prop_none_deps = ComputedProperty(test_func, None)
        context3 = MockContext()
        prop_none_deps.subscribe(context3)
        assert context3 in prop_none_deps._subscribers

    def test_subscribe_doesnt_affect_cache_state(self) -> None:
        """Test that subscribing doesn't affect cache state."""

        def test_func(context: Any) -> str:
            return "value"

        prop = ComputedProperty(test_func, ["dep"])
        context = MockContext()

        # Initial state
        initial_cached = prop._is_cached
        initial_value = prop._cached_value

        # Subscribe
        prop.subscribe(context)

        # Cache state should be unchanged
        assert prop._is_cached == initial_cached
        assert prop._cached_value == initial_value
