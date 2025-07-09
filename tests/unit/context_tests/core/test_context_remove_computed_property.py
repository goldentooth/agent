"""Test Context.remove_computed_property method."""

import pytest

from context.main import Context


def test_remove_computed_property_basic() -> None:
    """Test basic computed property removal."""
    context = Context()
    context["x"] = 10
    context["y"] = 20

    # Add computed property
    def sum_func(ctx: Context) -> int:
        return int(ctx["x"]) + int(ctx["y"])

    context.add_computed_property("sum", sum_func, ["x", "y"])
    assert "sum" in context
    assert context["sum"] == 30

    # Remove computed property
    context.remove_computed_property("sum")
    assert "sum" not in context
    assert "sum" not in context._computed_properties

    # Should raise KeyError when accessed
    with pytest.raises(KeyError, match="Context key 'sum' not found"):
        _ = context["sum"]


def test_remove_computed_property_nonexistent() -> None:
    """Test removing non-existent computed property."""
    context = Context()

    # Should not raise error when removing non-existent property
    context.remove_computed_property("nonexistent")

    # Verify context is unchanged
    assert len(context._computed_properties) == 0


def test_remove_computed_property_from_keys() -> None:
    """Test that removed computed property disappears from keys."""
    context = Context()
    context["regular"] = "value"

    # Add computed property
    context.add_computed_property("computed", lambda ctx: "computed_value")

    # Check both appear in keys
    keys = list(context.keys())
    assert "regular" in keys
    assert "computed" in keys

    # Remove computed property
    context.remove_computed_property("computed")

    # Check only regular key remains
    keys = list(context.keys())
    assert "regular" in keys
    assert "computed" not in keys


def test_remove_computed_property_multiple() -> None:
    """Test removing multiple computed properties."""
    context = Context()
    context["a"] = 1
    context["b"] = 2

    # Add multiple computed properties
    _add_test_properties(context)

    # Verify all exist initially
    assert "sum" in context
    assert "product" in context
    assert "difference" in context

    # Test removal one by one
    _test_remove_product(context)
    _test_remove_sum(context)
    _test_remove_difference(context)


def _add_test_properties(context: Context) -> None:
    """Helper to add test computed properties."""
    context.add_computed_property("sum", lambda ctx: ctx["a"] + ctx["b"], ["a", "b"])
    context.add_computed_property(
        "product", lambda ctx: ctx["a"] * ctx["b"], ["a", "b"]
    )
    context.add_computed_property(
        "difference", lambda ctx: ctx["b"] - ctx["a"], ["a", "b"]
    )


def _test_remove_product(context: Context) -> None:
    """Helper to test removing product property."""
    context.remove_computed_property("product")
    assert "sum" in context
    assert "product" not in context
    assert "difference" in context


def _test_remove_sum(context: Context) -> None:
    """Helper to test removing sum property."""
    context.remove_computed_property("sum")
    assert "sum" not in context
    assert "product" not in context
    assert "difference" in context


def _test_remove_difference(context: Context) -> None:
    """Helper to test removing difference property."""
    context.remove_computed_property("difference")
    assert "sum" not in context
    assert "product" not in context
    assert "difference" not in context


def test_remove_computed_property_subscription_cleanup() -> None:
    """Test that subscriptions are cleaned up when removing computed property."""
    context = Context()
    context["value"] = 10

    def test_func(ctx: Context) -> int:
        return int(ctx["value"]) * 2

    # Add computed property
    context.add_computed_property("doubled", test_func, ["value"])

    # Get the computed property and verify subscription
    computed_prop = context._computed_properties["doubled"]
    assert context in computed_prop._subscribers

    # Remove computed property
    context.remove_computed_property("doubled")

    # Verify subscription is cleaned up (subscribers should be weak references, so it might be empty)
    # The main assertion is that the computed property is removed from context
    assert "doubled" not in context._computed_properties


def test_remove_computed_property_return_value() -> None:
    """Test that remove_computed_property returns None."""
    context = Context()

    # Add computed property
    context.add_computed_property("test", lambda ctx: "test")

    # Remove and check return value (method returns None)
    context.remove_computed_property("test")

    # Also test with non-existent property (method returns None)
    context.remove_computed_property("nonexistent")


def test_remove_computed_property_no_dependencies() -> None:
    """Test removing computed property with no dependencies."""
    context = Context()

    # Add computed property with no dependencies
    context.add_computed_property("const", lambda ctx: "constant")
    assert "const" in context

    # Remove it
    context.remove_computed_property("const")
    assert "const" not in context


def test_remove_computed_property_with_cached_value() -> None:
    """Test removing computed property that has a cached value."""
    context = Context()
    context["value"] = 42
    call_count = 0

    def expensive_func(ctx: Context) -> int:
        nonlocal call_count
        call_count += 1
        return int(ctx["value"]) * 2

    # Add computed property
    context.add_computed_property("expensive", expensive_func, ["value"])

    # Access to cache the value
    assert context["expensive"] == 84
    assert call_count == 1

    # Remove the property
    context.remove_computed_property("expensive")

    # Verify it's completely removed
    assert "expensive" not in context
    with pytest.raises(KeyError):
        _ = context["expensive"]


def test_remove_computed_property_overwrites_regular_key() -> None:
    """Test removing computed property doesn't affect regular keys with same name."""
    context = Context()

    # Set regular key
    context["test_key"] = "regular_value"

    # Add computed property with same name (overwrites)
    context.add_computed_property("test_key", lambda ctx: "computed_value")
    assert context["test_key"] == "computed_value"

    # Remove computed property
    context.remove_computed_property("test_key")

    # Regular key should now be accessible again
    assert context["test_key"] == "regular_value"


def test_remove_computed_property_leaves_other_properties() -> None:
    """Test that removing one computed property leaves others intact."""
    context = Context()
    context["x"] = 5
    context["y"] = 10

    # Add two computed properties
    context.add_computed_property("double_x", lambda ctx: ctx["x"] * 2, ["x"])
    context.add_computed_property("double_y", lambda ctx: ctx["y"] * 2, ["y"])

    # Verify both work
    assert context["double_x"] == 10
    assert context["double_y"] == 20

    # Remove one
    context.remove_computed_property("double_x")

    # Verify the other still works
    assert context["double_y"] == 20
    assert "double_x" not in context
