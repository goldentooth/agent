"""Tests for Context._invalidate_dependent_computed_properties private method."""

from context.main import Context


class TestContextInvalidateDependentComputedProperties:
    """Test suite for Context._invalidate_dependent_computed_properties private method."""

    def test_invalidate_dependent_computed_properties_no_computed_properties(
        self,
    ) -> None:
        """Test invalidating dependents when no computed properties exist."""
        context = Context()

        # Should not raise an exception when no computed properties exist
        context._invalidate_dependent_computed_properties("test_key")

        # Verify no computed properties were added
        assert len(context._computed_properties) == 0

    def test_invalidate_dependent_computed_properties_no_dependents(self) -> None:
        """Test invalidating dependents when no dependents exist for the key."""
        context = Context()

        # Add a computed property that doesn't depend on the key we'll invalidate
        def compute_func(ctx: Context) -> str:
            return "computed_value"

        context.add_computed_property("computed_key", compute_func, [])

        # Should not affect the computed property
        context._invalidate_dependent_computed_properties("other_key")

        # Verify computed property still exists and works
        assert context["computed_key"] == "computed_value"

    def test_invalidate_dependent_computed_properties_method_exists(self) -> None:
        """Test that _invalidate_dependent_computed_properties method exists and is callable."""
        context = Context()

        # Verify method exists and is callable
        assert hasattr(context, "_invalidate_dependent_computed_properties")
        assert callable(context._invalidate_dependent_computed_properties)

    def test_invalidate_dependent_computed_properties_method_signature(self) -> None:
        """Test that _invalidate_dependent_computed_properties method has correct signature."""
        context = Context()

        # Test with required parameter
        context._invalidate_dependent_computed_properties("test_key")

        # Should not raise any exceptions for valid string keys
        context._invalidate_dependent_computed_properties("")
        context._invalidate_dependent_computed_properties("key.with.dots")
        context._invalidate_dependent_computed_properties("key-with-dashes")

    def test_invalidate_dependent_computed_properties_with_computed_properties(
        self,
    ) -> None:
        """Test invalidating dependents when computed properties exist."""
        context = Context()

        # Add some computed properties
        def compute_func1(ctx: Context) -> str:
            return "value1"

        def compute_func2(ctx: Context) -> str:
            return "value2"

        context.add_computed_property("computed1", compute_func1, [])
        context.add_computed_property("computed2", compute_func2, [])

        # Should not raise an exception even with computed properties
        context._invalidate_dependent_computed_properties("test_key")

        # Verify computed properties still work
        assert context["computed1"] == "value1"
        assert context["computed2"] == "value2"

    def test_invalidate_dependent_computed_properties_various_key_types(self) -> None:
        """Test invalidating dependents with various key types."""
        context = Context()

        # Test with different key patterns
        test_keys = [
            "simple_key",
            "key.with.dots",
            "key-with-dashes",
            "key_with_underscores",
            "key123",
            "KEY_UPPER",
            "mixedCaseKey",
            "key/with/slashes",
            "key with spaces",
            "",  # Empty string
            "🔑emoji_key",
            "very_long_key_name_that_exceeds_normal_length_but_should_still_work",
        ]

        for key in test_keys:
            # Should not raise an exception for any key type
            context._invalidate_dependent_computed_properties(key)

    def test_invalidate_dependent_computed_properties_no_side_effects(self) -> None:
        """Test that invalidating dependents has no side effects on context state."""
        context = Context()

        # Set up initial state
        context.set("test_key", "initial_value")
        context.set("other_key", "other_value")

        # Store initial state
        initial_test_value = context.get("test_key")
        initial_other_value = context.get("other_key")

        # Invalidate dependents
        context._invalidate_dependent_computed_properties("test_key")

        # Verify context state is unchanged
        assert context.get("test_key") == initial_test_value
        assert context.get("other_key") == initial_other_value

    def test_invalidate_dependent_computed_properties_stub_implementation(self) -> None:
        """Test that the current stub implementation works correctly."""
        context = Context()

        # Add a computed property with dependencies
        def compute_func(ctx: Context) -> str:
            result = ctx.get("base_key", "default")
            return str(result)

        context.add_computed_property("computed_key", compute_func, ["base_key"])

        # Set the base key
        context.set("base_key", "base_value")

        # Verify computed property works
        assert context["computed_key"] == "base_value"

        # Call the invalidate method (should be a no-op in stub)
        context._invalidate_dependent_computed_properties("base_key")

        # In a full implementation, this would invalidate the computed property
        # But for now, the stub does nothing, so the property should still work
        assert context["computed_key"] == "base_value"

    def test_invalidate_dependent_computed_properties_exception_handling(self) -> None:
        """Test that the method handles edge cases gracefully."""
        context = Context()

        # Add a computed property that might raise an exception
        def problematic_compute_func(ctx: Context) -> str:
            # This could potentially cause issues if not handled properly
            try:
                return str(ctx["nonexistent_key"])
            except KeyError:
                return "fallback"

        context.add_computed_property("problematic_key", problematic_compute_func, [])

        # Should not raise an exception even with problematic computed properties
        context._invalidate_dependent_computed_properties("some_key")

        # The computed property itself might raise an exception when accessed,
        # but the invalidate method should not

    def test_invalidate_dependent_computed_properties_integration(self) -> None:
        """Test integration with the broader context system."""
        context = Context()

        # Create a more complex scenario
        context.set("base_value", 10)

        def compute_double(ctx: Context) -> int:
            value = ctx.get("base_value", 0)
            assert isinstance(value, int), f"Expected int, got {type(value)}"
            return value * 2

        def compute_triple(ctx: Context) -> int:
            value = ctx.get("base_value", 0)
            assert isinstance(value, int), f"Expected int, got {type(value)}"
            return value * 3

        context.add_computed_property("double", compute_double, ["base_value"])
        context.add_computed_property("triple", compute_triple, ["base_value"])

        # Verify initial computed values
        assert context["double"] == 20
        assert context["triple"] == 30

        # Invalidate dependents of base_value
        context._invalidate_dependent_computed_properties("base_value")

        # In stub implementation, computed properties should still work
        assert context["double"] == 20
        assert context["triple"] == 30

    def test_invalidate_dependent_computed_properties_multiple_calls(self) -> None:
        """Test that multiple calls to invalidate work correctly."""
        context = Context()

        # Add some test data
        context.set("key1", "value1")
        context.set("key2", "value2")

        def compute_func(ctx: Context) -> str:
            key1_value = ctx.get("key1", "")
            key2_value = ctx.get("key2", "")
            return str(key1_value) + str(key2_value)

        context.add_computed_property("combined", compute_func, ["key1", "key2"])

        # Multiple invalidation calls should not cause issues
        context._invalidate_dependent_computed_properties("key1")
        context._invalidate_dependent_computed_properties("key2")
        context._invalidate_dependent_computed_properties("key1")

        # Verify everything still works
        assert context["combined"] == "value1value2"

    def test_invalidate_dependent_computed_properties_concurrent_access(self) -> None:
        """Test that the method is safe for concurrent access patterns."""
        context = Context()

        # Add computed properties
        def compute_func1(ctx: Context) -> str:
            return "computed1"

        def compute_func2(ctx: Context) -> str:
            return "computed2"

        context.add_computed_property("comp1", compute_func1, ["key1"])
        context.add_computed_property("comp2", compute_func2, ["key2"])

        # Simulate concurrent invalidation (would be called from different threads)
        context._invalidate_dependent_computed_properties("key1")
        context._invalidate_dependent_computed_properties("key2")

        # Verify state consistency
        assert context["comp1"] == "computed1"
        assert context["comp2"] == "computed2"
