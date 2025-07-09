"""Test Context.add_computed_property method."""

from typing import Any

import pytest

from context.main import Context


def test_add_computed_property_basic() -> None:
    """Test basic computed property addition."""
    context = Context()
    context["x"] = 10
    context["y"] = 20

    # Add computed property
    def sum_func(ctx: Context) -> int:
        return int(ctx["x"]) + int(ctx["y"])

    context.add_computed_property("sum", sum_func, ["x", "y"])

    # Should be able to access computed value
    assert context["sum"] == 30
    assert context.get("sum") == 30
    assert "sum" in context


def test_add_computed_property_no_dependencies() -> None:
    """Test computed property with no explicit dependencies."""
    context = Context()

    # Add computed property with no dependencies
    def constant_func(ctx: Context) -> str:
        return "constant"

    context.add_computed_property("const", constant_func)

    # Should work
    assert context["const"] == "constant"


def test_add_computed_property_caching() -> None:
    """Test that computed properties are cached."""
    context = Context()
    context["value"] = 42
    call_count = 0

    def expensive_func(ctx: Context) -> int:
        nonlocal call_count
        call_count += 1
        return int(ctx["value"]) * 2

    context.add_computed_property("expensive", expensive_func, ["value"])

    # First access should compute
    assert context["expensive"] == 84
    assert call_count == 1

    # Second access should use cached value
    assert context["expensive"] == 84
    assert call_count == 1


def test_add_computed_property_multiple() -> None:
    """Test adding multiple computed properties."""
    context = Context()
    context["a"] = 1
    context["b"] = 2
    context["c"] = 3

    # Add multiple computed properties
    context.add_computed_property("sum", lambda ctx: ctx["a"] + ctx["b"], ["a", "b"])
    context.add_computed_property(
        "product", lambda ctx: ctx["b"] * ctx["c"], ["b", "c"]
    )
    context.add_computed_property(
        "all_sum", lambda ctx: ctx["a"] + ctx["b"] + ctx["c"], ["a", "b", "c"]
    )

    # All should work
    assert context["sum"] == 3
    assert context["product"] == 6
    assert context["all_sum"] == 6


def test_add_computed_property_overwrites_existing() -> None:
    """Test that adding computed property overwrites existing one."""
    context = Context()
    context["x"] = 5

    # Add first computed property
    context.add_computed_property("computed", lambda ctx: ctx["x"] * 2, ["x"])
    assert context["computed"] == 10

    # Add second computed property with same key
    context.add_computed_property("computed", lambda ctx: ctx["x"] * 3, ["x"])
    assert context["computed"] == 15


def test_add_computed_property_complex_function() -> None:
    """Test computed property with complex function."""
    context = Context()
    context["items"] = [1, 2, 3, 4, 5]

    def complex_func(ctx: Context) -> dict[str, Any]:
        items = ctx["items"]
        return {
            "sum": sum(items),
            "count": len(items),
            "average": sum(items) / len(items) if items else 0,
            "max": max(items) if items else None,
            "min": min(items) if items else None,
        }

    context.add_computed_property("stats", complex_func, ["items"])

    stats = context["stats"]
    assert stats["sum"] == 15
    assert stats["count"] == 5
    assert stats["average"] == 3.0
    assert stats["max"] == 5
    assert stats["min"] == 1


def test_add_computed_property_with_nested_access() -> None:
    """Test computed property that accesses nested data."""
    context = Context()
    context["data"] = {"nested": {"value": 100}}

    def nested_func(ctx: Context) -> int:
        return int(ctx["data"]["nested"]["value"]) * 2

    context.add_computed_property("doubled", nested_func, ["data"])
    assert context["doubled"] == 200


def test_add_computed_property_appears_in_keys() -> None:
    """Test that computed properties appear in keys iterator."""
    context = Context()
    context["regular"] = "value"

    context.add_computed_property("computed", lambda ctx: "computed_value")

    keys = list(context.keys())
    assert "regular" in keys
    assert "computed" in keys


def test_add_computed_property_subscription() -> None:
    """Test that context is subscribed to computed property."""
    context = Context()
    context["value"] = 10

    def test_func(ctx: Context) -> int:
        return int(ctx["value"]) * 2

    context.add_computed_property("doubled", test_func, ["value"])

    # Get the computed property
    computed_prop = context._computed_properties["doubled"]

    # Check that context is subscribed
    assert context in computed_prop._subscribers


def test_add_computed_property_empty_dependencies() -> None:
    """Test computed property with empty dependencies list."""
    context = Context()

    def no_deps_func(ctx: Context) -> str:
        return "no dependencies"

    context.add_computed_property("no_deps", no_deps_func, [])
    assert context["no_deps"] == "no dependencies"


def test_add_computed_property_function_with_side_effects() -> None:
    """Test computed property function with side effects (should still work)."""
    context = Context()
    context["counter"] = 0
    external_state = {"calls": 0}

    def side_effect_func(ctx: Context) -> int:
        external_state["calls"] += 1
        return int(ctx["counter"]) + external_state["calls"]

    context.add_computed_property("with_effects", side_effect_func, ["counter"])

    # First call
    result1 = context["with_effects"]
    assert result1 == 1  # 0 + 1

    # Second call should use cached value (no side effect)
    result2 = context["with_effects"]
    assert result2 == 1  # Same cached value
    assert external_state["calls"] == 1  # Only called once


def test_add_computed_property_return_type() -> None:
    """Test that add_computed_property returns None."""
    context = Context()

    def test_func(ctx: Context) -> str:
        return "test"

    # Method should return None (testing this implicitly)
    context.add_computed_property("test", test_func)


def test_add_computed_property_error_handling() -> None:
    """Test computed property with function that raises an error."""
    context = Context()
    context["value"] = 10

    def error_func(ctx: Context) -> int:
        raise ValueError("Test error")

    context.add_computed_property("error_prop", error_func, ["value"])

    # Should raise the error when accessed
    with pytest.raises(ValueError, match="Test error"):
        _ = context["error_prop"]


def test_add_computed_property_missing_dependency() -> None:
    """Test computed property that accesses missing key."""
    context = Context()

    def missing_key_func(ctx: Context) -> int:
        return int(ctx["nonexistent"]) * 2

    context.add_computed_property("missing", missing_key_func, ["nonexistent"])

    # Should raise KeyError when accessed
    with pytest.raises(KeyError, match="Context key 'nonexistent' not found"):
        _ = context["missing"]


def test_add_computed_property_with_context_layers() -> None:
    """Test computed property with multiple context layers."""
    context = Context()

    # Set value in base layer
    context["base_value"] = 10

    # Push layer and set value
    context.push_layer()
    context["layer_value"] = 20

    def layer_func(ctx: Context) -> int:
        return int(ctx["base_value"]) + int(ctx["layer_value"])

    context.add_computed_property(
        "layer_sum", layer_func, ["base_value", "layer_value"]
    )
    assert context["layer_sum"] == 30
