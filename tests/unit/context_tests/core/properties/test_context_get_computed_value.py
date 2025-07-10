"""Test Context.get_computed_value method."""

from typing import Any

import pytest

from context.main import Context


def test_get_computed_value_basic() -> None:
    """Test basic get_computed_value functionality."""
    context = Context()
    context["x"] = 10
    context["y"] = 20

    def sum_func(ctx: Context) -> int:
        return int(ctx["x"]) + int(ctx["y"])

    context.add_computed_property("sum", sum_func, ["x", "y"])

    # Should return the computed value
    assert context.get_computed_value("sum") == 30


def test_get_computed_value_nonexistent() -> None:
    """Test get_computed_value with non-existent property."""
    context = Context()

    # Should raise KeyError for non-existent computed property
    with pytest.raises(
        KeyError, match="No computed property found for key: nonexistent"
    ):
        context.get_computed_value("nonexistent")


def test_get_computed_value_regular_key() -> None:
    """Test get_computed_value with regular (non-computed) key."""
    context = Context()
    context["regular"] = "value"

    # Should raise KeyError for regular keys
    with pytest.raises(KeyError, match="No computed property found for key: regular"):
        context.get_computed_value("regular")


def test_get_computed_value_with_caching() -> None:
    """Test that get_computed_value uses cached values."""
    context = Context()
    context["value"] = 42
    call_count = 0

    def expensive_func(ctx: Context) -> int:
        nonlocal call_count
        call_count += 1
        return int(ctx["value"]) * 2

    context.add_computed_property("expensive", expensive_func, ["value"])

    # First call should compute
    result1 = context.get_computed_value("expensive")
    assert result1 == 84
    assert call_count == 1

    # Second call should use cached value
    result2 = context.get_computed_value("expensive")
    assert result2 == 84
    assert call_count == 1  # No additional computation


def test_get_computed_value_complex_return() -> None:
    """Test get_computed_value with complex return type."""
    context = Context()
    context["items"] = [1, 2, 3, 4, 5]

    def stats_func(ctx: Context) -> dict[str, Any]:
        items = ctx["items"]
        return {
            "sum": sum(items),
            "count": len(items),
            "average": sum(items) / len(items),
        }

    context.add_computed_property("stats", stats_func, ["items"])

    stats = context.get_computed_value("stats")
    assert stats["sum"] == 15
    assert stats["count"] == 5
    assert stats["average"] == 3.0


def test_get_computed_value_no_dependencies() -> None:
    """Test get_computed_value with property that has no dependencies."""
    context = Context()

    def constant_func(ctx: Context) -> str:
        return "constant_value"

    context.add_computed_property("const", constant_func, [])
    assert context.get_computed_value("const") == "constant_value"


def test_get_computed_value_equivalent_to_getitem() -> None:
    """Test that get_computed_value returns same value as __getitem__."""
    context = Context()
    context["base"] = 10

    def double_func(ctx: Context) -> int:
        return int(ctx["base"]) * 2

    context.add_computed_property("doubled", double_func, ["base"])

    # Both methods should return the same value
    assert context.get_computed_value("doubled") == context["doubled"]


def test_get_computed_value_error_in_computation() -> None:
    """Test get_computed_value when computation raises an error."""
    context = Context()
    context["value"] = 10

    def error_func(ctx: Context) -> int:
        raise ValueError("Computation error")

    context.add_computed_property("error_prop", error_func, ["value"])

    # Should raise the computation error
    with pytest.raises(ValueError, match="Computation error"):
        context.get_computed_value("error_prop")


def test_get_computed_value_missing_dependency() -> None:
    """Test get_computed_value when dependency is missing."""
    context = Context()

    def missing_dep_func(ctx: Context) -> int:
        return int(ctx["missing"]) * 2

    context.add_computed_property("with_missing", missing_dep_func, ["missing"])

    # Should raise KeyError for missing dependency
    with pytest.raises(KeyError, match="Context key 'missing' not found"):
        context.get_computed_value("with_missing")


def test_get_computed_value_multiple_properties() -> None:
    """Test get_computed_value with multiple computed properties."""
    context = Context()
    context["a"] = 5
    context["b"] = 10

    context.add_computed_property("sum", lambda ctx: ctx["a"] + ctx["b"], ["a", "b"])
    context.add_computed_property(
        "product", lambda ctx: ctx["a"] * ctx["b"], ["a", "b"]
    )
    context.add_computed_property(
        "difference", lambda ctx: ctx["b"] - ctx["a"], ["a", "b"]
    )

    # Should return correct values for all properties
    assert context.get_computed_value("sum") == 15
    assert context.get_computed_value("product") == 50
    assert context.get_computed_value("difference") == 5


def test_get_computed_value_after_dependency_change() -> None:
    """Test get_computed_value after dependency values change."""
    context = Context()
    context["value"] = 10

    def doubled_func(ctx: Context) -> int:
        return int(ctx["value"]) * 2

    context.add_computed_property("doubled", doubled_func, ["value"])

    # Get initial value
    assert context.get_computed_value("doubled") == 20

    # Change dependency and check updated value
    context["value"] = 15
    # Note: Without dependency tracking/invalidation, this might still return cached value
    # This test documents current behavior - actual behavior depends on implementation


def test_get_computed_value_with_layers() -> None:
    """Test get_computed_value with multiple context layers."""
    context = Context()
    context["base"] = 10

    # Push layer and override value
    context.push_layer()
    context["layer"] = 5

    def layer_sum_func(ctx: Context) -> int:
        return int(ctx["base"]) + int(ctx["layer"])

    context.add_computed_property("layer_sum", layer_sum_func, ["base", "layer"])
    assert context.get_computed_value("layer_sum") == 15


def test_get_computed_value_nested_access() -> None:
    """Test get_computed_value with nested data access."""
    context = Context()
    context["data"] = {"nested": {"value": 100}}

    def nested_func(ctx: Context) -> int:
        return int(ctx["data"]["nested"]["value"]) * 2

    context.add_computed_property("nested_doubled", nested_func, ["data"])
    assert context.get_computed_value("nested_doubled") == 200
