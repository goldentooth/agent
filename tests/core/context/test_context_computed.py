"""Tests for Context computed properties and transformations."""

from __future__ import annotations

import pytest

from goldentooth_agent.core.context import Context


class TestContextComputedProperties:
    """Test suite for Context computed properties."""

    def test_add_computed_property_basic(self) -> None:
        """Test adding a basic computed property."""
        context = Context()

        # Add a simple computed property
        def double_x(ctx: Context) -> int:
            return ctx.get("x", 0) * 2

        context.add_computed_property("double_x", double_x, ["x"])

        # Set the dependency and check computed value
        context["x"] = 5
        assert context["double_x"] == 10
        assert context.get("double_x") == 10
        assert context.is_computed_property("double_x")
        assert not context.is_computed_property("x")

    def test_computed_property_dependencies(self) -> None:
        """Test that computed properties update when dependencies change."""
        context = Context()

        # Add computed property with multiple dependencies
        def sum_ab(ctx: Context) -> int:
            return ctx.get("a", 0) + ctx.get("b", 0)

        context.add_computed_property("sum", sum_ab, ["a", "b"])

        # Initially zero
        assert context["sum"] == 0

        # Update one dependency
        context["a"] = 10
        assert context["sum"] == 10

        # Update another dependency
        context["b"] = 5
        assert context["sum"] == 15

        # Update both
        context["a"] = 20
        context["b"] = 30
        assert context["sum"] == 50

    def test_computed_property_caching(self) -> None:
        """Test that computed properties are cached and invalidated correctly."""
        context = Context()

        call_count = 0

        def expensive_computation(ctx: Context) -> int:
            nonlocal call_count
            call_count += 1
            return ctx.get("x", 0) ** 2

        context.add_computed_property("x_squared", expensive_computation, ["x"])

        # First access should compute
        context["x"] = 4
        result1 = context["x_squared"]
        assert result1 == 16
        assert call_count == 1

        # Second access should use cache
        result2 = context["x_squared"]
        assert result2 == 16
        assert call_count == 1  # Still 1, not computed again

        # Change dependency should invalidate cache
        context["x"] = 5
        result3 = context["x_squared"]
        assert result3 == 25
        assert call_count == 2  # Computed again

    def test_computed_property_in_keys(self) -> None:
        """Test that computed properties appear in keys() iteration."""
        context = Context()

        context["regular_key"] = "value"
        context.add_computed_property("computed_key", lambda ctx: "computed", [])

        keys = list(context.keys())
        assert "regular_key" in keys
        assert "computed_key" in keys
        assert len(keys) == 2

    def test_computed_property_in_contains(self) -> None:
        """Test that computed properties work with 'in' operator."""
        context = Context()

        context.add_computed_property("computed_key", lambda ctx: "computed", [])

        assert "computed_key" in context
        assert "nonexistent_key" not in context

    def test_remove_computed_property(self) -> None:
        """Test removing computed properties."""
        context = Context()

        context.add_computed_property("computed_key", lambda ctx: "computed", ["x"])
        assert "computed_key" in context
        assert context.is_computed_property("computed_key")

        context.remove_computed_property("computed_key")
        assert "computed_key" not in context
        assert not context.is_computed_property("computed_key")

        # Should not raise when removing non-existent property
        context.remove_computed_property("nonexistent")

    def test_computed_property_error_handling(self) -> None:
        """Test error handling in computed properties."""
        context = Context()

        def failing_computation(ctx: Context) -> int:
            raise ValueError("Computation failed")

        context.add_computed_property("failing_prop", failing_computation, [])

        # Should raise the error from the computation
        with pytest.raises(ValueError, match="Computation failed"):
            _ = context["failing_prop"]

    def test_get_computed_value_method(self) -> None:
        """Test the get_computed_value method."""
        context = Context()

        context.add_computed_property("test_prop", lambda ctx: "test_value", [])

        assert context.get_computed_value("test_prop") == "test_value"

        with pytest.raises(KeyError):
            context.get_computed_value("nonexistent_prop")

    def test_computed_properties_method(self) -> None:
        """Test the computed_properties method returns a copy."""
        context = Context()

        context.add_computed_property("prop1", lambda ctx: "value1", [])
        context.add_computed_property("prop2", lambda ctx: "value2", [])

        props = context.computed_properties()
        assert len(props) == 2
        assert "prop1" in props
        assert "prop2" in props

        # Modifying returned dict shouldn't affect original
        props.clear()
        assert len(context.computed_properties()) == 2


class TestContextTransformations:
    """Test suite for Context value transformations."""

    def test_add_transformation_basic(self) -> None:
        """Test adding a basic transformation."""
        context = Context()

        # Add transformation that converts to uppercase
        context.add_transformation("name", str.upper)

        context["name"] = "alice"
        assert context["name"] == "ALICE"

    def test_multiple_transformations(self) -> None:
        """Test chaining multiple transformations."""
        context = Context()

        # Add multiple transformations
        context.add_transformation("value", lambda x: x * 2)  # Double
        context.add_transformation("value", lambda x: x + 1)  # Add 1

        context["value"] = 5
        # Should apply in order: 5 * 2 = 10, then 10 + 1 = 11
        assert context["value"] == 11

    def test_transformation_error_handling(self) -> None:
        """Test that transformation errors don't break the system."""
        context = Context()

        # Add transformation that might fail
        def risky_transform(x):
            if isinstance(x, str):
                raise ValueError("Cannot transform string")
            return x * 2

        context.add_transformation("risky_key", risky_transform)

        # Should use original value when transformation fails
        context["risky_key"] = "hello"
        assert context["risky_key"] == "hello"  # Original value preserved

        # Should work when transformation succeeds
        context["risky_key"] = 5
        assert context["risky_key"] == 10

    def test_remove_transformations(self) -> None:
        """Test removing transformations."""
        context = Context()

        context.add_transformation("key", str.upper)
        context["key"] = "hello"
        assert context["key"] == "HELLO"

        context.remove_transformations("key")
        context["key"] = "world"
        assert context["key"] == "world"  # No transformation applied

    def test_transformations_method(self) -> None:
        """Test the transformations method returns a copy."""
        context = Context()

        context.add_transformation("key1", str.upper)
        context.add_transformation("key2", str.lower)

        transforms = context.transformations()
        assert len(transforms) == 2
        assert "key1" in transforms
        assert "key2" in transforms

        # Modifying returned dict shouldn't affect original
        transforms.clear()
        assert len(context.transformations()) == 2


class TestContextComputedPropertiesWithTransformations:
    """Test computed properties and transformations working together."""

    def test_computed_property_with_transformed_dependency(self) -> None:
        """Test computed property that depends on transformed values."""
        context = Context()

        # Add transformation for input
        context.add_transformation("input", lambda x: x * 2)

        # Add computed property that depends on transformed input
        def compute_result(ctx: Context) -> int:
            return ctx.get("input", 0) + 10

        context.add_computed_property("result", compute_result, ["input"])

        # Set value - should be transformed first, then computed property updated
        context["input"] = 5  # Transformed to 10
        assert context["input"] == 10
        assert context["result"] == 20  # 10 + 10

    def test_transformation_affects_computed_property_invalidation(self) -> None:
        """Test that transformations properly trigger computed property invalidation."""
        context = Context()

        call_count = 0

        def count_calls(ctx: Context) -> int:
            nonlocal call_count
            call_count += 1
            return ctx.get("x", 0) ** 2

        context.add_transformation("x", lambda val: val * 2)
        context.add_computed_property("x_squared", count_calls, ["x"])

        # First computation
        context["x"] = 3  # Transformed to 6
        result1 = context["x_squared"]  # 6^2 = 36
        assert result1 == 36
        assert call_count == 1

        # Second access should use cache
        result2 = context["x_squared"]
        assert result2 == 36
        assert call_count == 1

        # Change should invalidate
        context["x"] = 4  # Transformed to 8
        result3 = context["x_squared"]  # 8^2 = 64
        assert result3 == 64
        assert call_count == 2


class TestContextForking:
    """Test forking behavior with computed properties and transformations."""

    def test_fork_preserves_computed_properties(self) -> None:
        """Test that forking preserves computed properties."""
        original = Context()

        original.add_computed_property(
            "double_x", lambda ctx: ctx.get("x", 0) * 2, ["x"]
        )
        original["x"] = 5

        forked = original.fork()

        # Both should have the computed property
        assert original["double_x"] == 10
        assert forked["double_x"] == 10

        # Changes should be isolated
        forked["x"] = 10
        assert original["double_x"] == 10  # Unchanged
        assert forked["double_x"] == 20  # Updated

    def test_fork_preserves_transformations(self) -> None:
        """Test that forking preserves transformations."""
        original = Context()

        original.add_transformation("name", str.upper)
        original["name"] = "alice"
        assert original["name"] == "ALICE"

        forked = original.fork()

        # Both should have the transformation
        forked["name"] = "bob"
        assert forked["name"] == "BOB"

        # Changes should be isolated
        original["name"] = "charlie"
        assert original["name"] == "CHARLIE"
        assert forked["name"] == "BOB"  # Unchanged

    def test_fork_with_complex_setup(self) -> None:
        """Test forking with both computed properties and transformations."""
        original = Context()

        # Add transformation and computed property
        original.add_transformation("input", lambda x: x * 3)
        original.add_computed_property(
            "output", lambda ctx: ctx.get("input", 0) + 100, ["input"]
        )

        original["input"] = 5  # Transformed to 15
        assert original["input"] == 15
        assert original["output"] == 115  # 15 + 100

        forked = original.fork()

        # Forked should have same setup
        forked["input"] = 10  # Transformed to 30
        assert forked["input"] == 30
        assert forked["output"] == 130  # 30 + 100

        # Original should be unchanged
        assert original["input"] == 15
        assert original["output"] == 115
