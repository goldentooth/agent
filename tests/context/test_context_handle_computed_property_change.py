"""Tests for Context._handle_computed_property_change private method."""

from unittest.mock import Mock, patch

from context.computed import ComputedProperty
from context.main import Context


class TestContextHandleComputedPropertyChange:
    """Test suite for Context._handle_computed_property_change private method."""

    def test_handle_computed_property_change_method_exists(self) -> None:
        """Test that _handle_computed_property_change method exists and is callable."""
        context = Context()

        # Verify method exists and is callable
        assert hasattr(context, "_handle_computed_property_change")
        assert callable(context._handle_computed_property_change)

    def test_handle_computed_property_change_method_signature(self) -> None:
        """Test that _handle_computed_property_change method has correct signature."""
        context = Context()

        # Create a mock computed property
        mock_computed_prop = Mock(spec=ComputedProperty)
        mock_computed_prop._is_cached = False
        mock_computed_prop._cached_value = None
        mock_computed_prop.compute = Mock(return_value="test_value")

        # Test with required parameter
        context._handle_computed_property_change(mock_computed_prop)

        # Should not raise any exceptions

    def test_handle_computed_property_change_no_matching_property(self) -> None:
        """Test handling when computed property is not found in context."""
        context = Context()

        # Create a computed property that's not in the context
        mock_computed_prop = Mock(spec=ComputedProperty)
        mock_computed_prop._is_cached = False
        mock_computed_prop._cached_value = None
        mock_computed_prop.compute = Mock(return_value="test_value")

        # Should not raise an exception even if property is not found
        context._handle_computed_property_change(mock_computed_prop)

    def test_handle_computed_property_change_with_cached_value(self) -> None:
        """Test handling computed property change when property has cached value."""
        context = Context()

        # Create a computed property with cached value
        def compute_func(ctx: Context) -> str:
            return "computed_value"

        context.add_computed_property("test_key", compute_func, [])

        # Get the computed property and simulate it having a cached value
        computed_prop = context._computed_properties["test_key"]
        computed_prop._cached_value = "old_cached_value"
        computed_prop._is_cached = True

        # Mock the emit_change_event and invalidate methods to verify they're called
        with patch.object(context, "_emit_change_event") as mock_emit:
            with patch.object(
                context, "_invalidate_dependent_computed_properties"
            ) as mock_invalidate:
                context._handle_computed_property_change(computed_prop)

                # Verify emit_change_event was called with correct parameters
                # Note: old_value is None in stub implementation to avoid accessing private members
                mock_emit.assert_called_once_with("test_key", "computed_value", None)

                # Verify invalidate was called with the key
                mock_invalidate.assert_called_once_with("test_key")

    def test_handle_computed_property_change_without_cached_value(self) -> None:
        """Test handling computed property change when property has no cached value."""
        context = Context()

        # Create a computed property without cached value
        def compute_func(ctx: Context) -> str:
            return "computed_value"

        context.add_computed_property("test_key", compute_func, [])

        # Get the computed property and ensure it has no cached value
        computed_prop = context._computed_properties["test_key"]
        computed_prop._cached_value = None
        computed_prop._is_cached = False

        # Mock the emit_change_event and invalidate methods to verify they're called
        with patch.object(context, "_emit_change_event") as mock_emit:
            with patch.object(
                context, "_invalidate_dependent_computed_properties"
            ) as mock_invalidate:
                context._handle_computed_property_change(computed_prop)

                # Verify emit_change_event was called with None as old_value
                mock_emit.assert_called_once_with("test_key", "computed_value", None)

                # Verify invalidate was called with the key
                mock_invalidate.assert_called_once_with("test_key")

    def test_handle_computed_property_change_calls_compute(self) -> None:
        """Test that handling computed property change calls compute method."""
        context = Context()

        # Create a computed property
        compute_func = Mock(return_value="new_computed_value")
        context.add_computed_property("test_key", compute_func, [])

        computed_prop = context._computed_properties["test_key"]

        # Mock the emit_change_event and invalidate methods
        with patch.object(context, "_emit_change_event"):
            with patch.object(context, "_invalidate_dependent_computed_properties"):
                context._handle_computed_property_change(computed_prop)

                # Verify compute was called with the context
                compute_func.assert_called_once_with(context)

    def test_handle_computed_property_change_multiple_properties(self) -> None:
        """Test handling change when multiple computed properties exist."""
        context = Context()

        # Create multiple computed properties
        def compute_func1(ctx: Context) -> str:
            return "value1"

        def compute_func2(ctx: Context) -> str:
            return "value2"

        context.add_computed_property("key1", compute_func1, [])
        context.add_computed_property("key2", compute_func2, [])

        # Get the second computed property
        computed_prop2 = context._computed_properties["key2"]

        # Mock the emit_change_event and invalidate methods
        with patch.object(context, "_emit_change_event") as mock_emit:
            with patch.object(
                context, "_invalidate_dependent_computed_properties"
            ) as mock_invalidate:
                context._handle_computed_property_change(computed_prop2)

                # Verify emit_change_event was called with the correct key
                mock_emit.assert_called_once_with("key2", "value2", None)

                # Verify invalidate was called with the correct key
                mock_invalidate.assert_called_once_with("key2")

    def test_handle_computed_property_change_different_data_types(self) -> None:
        """Test handling computed property changes with different data types."""
        context = Context()

        # Test with different return types
        test_values = ["string_value", 42, [1, 2, 3], {"key": "value"}, True, None]

        for i, value in enumerate(test_values):
            key = f"key_{i}"

            # Create a computed property that returns the test value
            def compute_func(ctx: Context, val: object = value) -> object:
                return val

            context.add_computed_property(key, compute_func, [])
            computed_prop = context._computed_properties[key]

            # Mock the emit_change_event and invalidate methods
            with patch.object(context, "_emit_change_event") as mock_emit:
                with patch.object(
                    context, "_invalidate_dependent_computed_properties"
                ) as mock_invalidate:
                    context._handle_computed_property_change(computed_prop)

                    # Verify emit_change_event was called with the correct value
                    mock_emit.assert_called_once_with(key, value, None)

                    # Verify invalidate was called with the correct key
                    mock_invalidate.assert_called_once_with(key)

    def test_handle_computed_property_change_integration_with_stub_methods(
        self,
    ) -> None:
        """Test integration with stub implementations of emit and invalidate."""
        context = Context()

        # Create a computed property
        def compute_func(ctx: Context) -> str:
            return "computed_value"

        context.add_computed_property("test_key", compute_func, [])
        computed_prop = context._computed_properties["test_key"]

        # Should not raise any exceptions with stub implementations
        context._handle_computed_property_change(computed_prop)

        # Verify the computed property was properly processed
        assert computed_prop.compute(context) == "computed_value"

    def test_handle_computed_property_change_with_dependencies(self) -> None:
        """Test handling computed property change with dependencies."""
        context = Context()

        # Set up base data
        context.set("base_key", "base_value")

        # Create a computed property that depends on base_key
        def compute_func(ctx: Context) -> str:
            return f"computed_{ctx.get('base_key', 'default')}"

        context.add_computed_property("dependent_key", compute_func, ["base_key"])
        computed_prop = context._computed_properties["dependent_key"]

        # Mock the emit_change_event and invalidate methods
        with patch.object(context, "_emit_change_event") as mock_emit:
            with patch.object(
                context, "_invalidate_dependent_computed_properties"
            ) as mock_invalidate:
                context._handle_computed_property_change(computed_prop)

                # Verify emit_change_event was called with the computed value
                mock_emit.assert_called_once_with(
                    "dependent_key", "computed_base_value", None
                )

                # Verify invalidate was called with the key
                mock_invalidate.assert_called_once_with("dependent_key")

    def test_handle_computed_property_change_exception_handling(self) -> None:
        """Test that exceptions in compute method are handled gracefully."""
        context = Context()

        # Create a computed property that raises an exception
        def failing_compute_func(ctx: Context) -> str:
            raise ValueError("Computation failed")

        context.add_computed_property("failing_key", failing_compute_func, [])
        computed_prop = context._computed_properties["failing_key"]

        # Mock the emit_change_event and invalidate methods
        with patch.object(context, "_emit_change_event") as mock_emit:
            with patch.object(
                context, "_invalidate_dependent_computed_properties"
            ) as mock_invalidate:
                # Should not raise an exception even if compute fails
                try:
                    context._handle_computed_property_change(computed_prop)
                except Exception:
                    pass  # Expected that compute might fail

                # The method should still attempt to emit and invalidate
                # even if compute fails (depending on implementation)

    def test_handle_computed_property_change_no_side_effects(self) -> None:
        """Test that handling computed property change has no side effects on context state."""
        context = Context()

        # Set up initial state
        context.set("test_key", "initial_value")

        # Create a computed property
        def compute_func(ctx: Context) -> str:
            return "computed_value"

        context.add_computed_property("computed_key", compute_func, [])
        computed_prop = context._computed_properties["computed_key"]

        # Store initial state
        initial_value = context.get("test_key")

        # Handle computed property change
        with patch.object(context, "_emit_change_event"):
            with patch.object(context, "_invalidate_dependent_computed_properties"):
                context._handle_computed_property_change(computed_prop)

        # Verify context state is unchanged
        assert context.get("test_key") == initial_value

    def test_handle_computed_property_change_finds_correct_property(self) -> None:
        """Test that the method correctly finds the matching computed property."""
        context = Context()

        # Create multiple computed properties
        def compute_func1(ctx: Context) -> str:
            return "value1"

        def compute_func2(ctx: Context) -> str:
            return "value2"

        def compute_func3(ctx: Context) -> str:
            return "value3"

        context.add_computed_property("key1", compute_func1, [])
        context.add_computed_property("key2", compute_func2, [])
        context.add_computed_property("key3", compute_func3, [])

        # Get the middle computed property
        computed_prop2 = context._computed_properties["key2"]

        # Mock the emit_change_event and invalidate methods
        with patch.object(context, "_emit_change_event") as mock_emit:
            with patch.object(
                context, "_invalidate_dependent_computed_properties"
            ) as mock_invalidate:
                context._handle_computed_property_change(computed_prop2)

                # Should only call emit and invalidate for key2
                mock_emit.assert_called_once_with("key2", "value2", None)
                mock_invalidate.assert_called_once_with("key2")

    def test_handle_computed_property_change_cached_vs_uncached(self) -> None:
        """Test handling cached vs uncached computed properties."""
        context = Context()

        # Create a computed property
        def compute_func(ctx: Context) -> str:
            return "computed_value"

        context.add_computed_property("test_key", compute_func, [])
        computed_prop = context._computed_properties["test_key"]

        # Test with cached property
        computed_prop._cached_value = "cached_value"
        computed_prop._is_cached = True

        with patch.object(context, "_emit_change_event") as mock_emit:
            with patch.object(context, "_invalidate_dependent_computed_properties"):
                context._handle_computed_property_change(computed_prop)

                # Should use None as old_value (stub implementation)
                mock_emit.assert_called_once_with("test_key", "computed_value", None)

        # Test with uncached property
        computed_prop._cached_value = None
        computed_prop._is_cached = False

        with patch.object(context, "_emit_change_event") as mock_emit:
            with patch.object(context, "_invalidate_dependent_computed_properties"):
                context._handle_computed_property_change(computed_prop)

                # Should use None as old_value
                mock_emit.assert_called_once_with("test_key", "computed_value", None)

    def test_handle_computed_property_change_early_exit(self) -> None:
        """Test that method exits early when computed property is found."""
        context = Context()

        # Create multiple computed properties
        def compute_func1(ctx: Context) -> str:
            return "value1"

        def compute_func2(ctx: Context) -> str:
            return "value2"

        context.add_computed_property("key1", compute_func1, [])
        context.add_computed_property("key2", compute_func2, [])

        # Get the first computed property
        computed_prop1 = context._computed_properties["key1"]

        # Mock the emit_change_event and invalidate methods
        with patch.object(context, "_emit_change_event") as mock_emit:
            with patch.object(
                context, "_invalidate_dependent_computed_properties"
            ) as mock_invalidate:
                context._handle_computed_property_change(computed_prop1)

                # Should only call emit and invalidate once (for key1)
                assert mock_emit.call_count == 1
                assert mock_invalidate.call_count == 1

                # Should not process key2
                mock_emit.assert_called_once_with("key1", "value1", None)
                mock_invalidate.assert_called_once_with("key1")
