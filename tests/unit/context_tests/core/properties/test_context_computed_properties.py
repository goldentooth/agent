"""Test Context.computed_properties property."""

from typing import Any

import pytest

from context.computed import ComputedProperty
from context.main import Context


def test_computed_properties_basic() -> None:
    """Test basic computed_properties functionality."""
    context = Context()

    # Initially should be empty
    props = context.computed_properties()
    assert isinstance(props, dict)
    assert len(props) == 0

    # Add computed property
    def test_func(ctx: Context) -> str:
        return "test"

    context.add_computed_property("test", test_func)

    # Should contain the property
    props = context.computed_properties()
    assert len(props) == 1
    assert "test" in props
    assert isinstance(props["test"], ComputedProperty)


def test_computed_properties_multiple() -> None:
    """Test computed_properties with multiple properties."""
    context = Context()
    context["a"] = 1
    context["b"] = 2

    # Add multiple computed properties
    context.add_computed_property("sum", lambda ctx: ctx["a"] + ctx["b"], ["a", "b"])
    context.add_computed_property(
        "product", lambda ctx: ctx["a"] * ctx["b"], ["a", "b"]
    )
    context.add_computed_property(
        "difference", lambda ctx: ctx["b"] - ctx["a"], ["a", "b"]
    )

    props = context.computed_properties()
    assert len(props) == 3
    assert "sum" in props
    assert "product" in props
    assert "difference" in props

    # All should be ComputedProperty instances
    for prop in props.values():
        assert isinstance(prop, ComputedProperty)


def test_computed_properties_returns_copy() -> None:
    """Test that computed_properties returns a copy, not reference."""
    context = Context()

    context.add_computed_property("original", lambda ctx: "original")

    # Get the properties
    props1 = context.computed_properties()
    props2 = context.computed_properties()

    # Should be different objects (copies)
    assert props1 is not props2

    # But should have same content
    assert props1.keys() == props2.keys()

    # Modifying returned dict shouldn't affect context
    # Create a fake ComputedProperty for testing
    fake_property = ComputedProperty(lambda ctx: "fake", [])
    props1["new_key"] = fake_property
    assert "new_key" not in context.computed_properties()


def test_computed_properties_after_removal() -> None:
    """Test computed_properties after removing properties."""
    context = Context()

    # Add and verify initial properties
    _add_three_properties(context)
    props = context.computed_properties()
    assert len(props) == 3

    # Test partial removal
    _test_partial_removal(context)

    # Test complete removal
    _test_complete_removal(context)


def _add_three_properties(context: Context) -> None:
    """Helper to add three test properties."""
    context.add_computed_property("prop1", lambda ctx: "value1")
    context.add_computed_property("prop2", lambda ctx: "value2")
    context.add_computed_property("prop3", lambda ctx: "value3")


def _test_partial_removal(context: Context) -> None:
    """Helper to test removing one property."""
    context.remove_computed_property("prop2")
    props = context.computed_properties()
    assert len(props) == 2
    assert "prop1" in props
    assert "prop2" not in props
    assert "prop3" in props


def _test_complete_removal(context: Context) -> None:
    """Helper to test removing all remaining properties."""
    context.remove_computed_property("prop1")
    context.remove_computed_property("prop3")
    props = context.computed_properties()
    assert len(props) == 0


def test_computed_properties_empty_context() -> None:
    """Test computed_properties with empty context."""
    context = Context()

    props = context.computed_properties()
    assert isinstance(props, dict)
    assert len(props) == 0
    assert props == {}


def test_computed_properties_no_dependencies() -> None:
    """Test computed_properties with properties that have no dependencies."""
    context = Context()

    def constant_func(ctx: Context) -> str:
        return "constant"

    context.add_computed_property("const", constant_func, [])

    props = context.computed_properties()
    assert len(props) == 1
    assert "const" in props
    assert isinstance(props["const"], ComputedProperty)


def test_computed_properties_with_dependencies() -> None:
    """Test computed_properties with properties that have dependencies."""
    context = Context()
    context["base"] = 10

    def dependent_func(ctx: Context) -> int:
        return int(ctx["base"]) * 2

    context.add_computed_property("dependent", dependent_func, ["base"])

    props = context.computed_properties()
    assert len(props) == 1
    assert "dependent" in props

    # Check that the ComputedProperty has correct dependencies
    computed_prop = props["dependent"]
    assert computed_prop.dependencies == ["base"]


def test_computed_properties_mixed_with_regular_keys() -> None:
    """Test computed_properties doesn't include regular context keys."""
    context = Context()

    # Add regular keys
    context["regular1"] = "value1"
    context["regular2"] = "value2"

    # Add computed properties
    context.add_computed_property("computed1", lambda ctx: "comp1")
    context.add_computed_property("computed2", lambda ctx: "comp2")

    props = context.computed_properties()

    # Should only contain computed properties
    assert len(props) == 2
    assert "computed1" in props
    assert "computed2" in props
    assert "regular1" not in props
    assert "regular2" not in props


def test_computed_properties_with_layers() -> None:
    """Test computed_properties with multiple context layers."""
    context = Context()

    # Add to base layer
    context.add_computed_property("base_computed", lambda ctx: "base_comp")

    # Push layer and add more
    context.push_layer()
    context.add_computed_property("layer_computed", lambda ctx: "layer_comp")

    props = context.computed_properties()

    # Should contain properties from all layers
    assert len(props) == 2
    assert "base_computed" in props
    assert "layer_computed" in props


def test_computed_properties_function_access() -> None:
    """Test that returned ComputedProperty objects contain correct functions."""
    context = Context()

    def test_function(ctx: Context) -> str:
        return "test_result"

    context.add_computed_property("test", test_function, ["dep"])

    props = context.computed_properties()
    computed_prop = props["test"]

    # Should have the same function
    assert computed_prop.func is test_function
    assert computed_prop.dependencies == ["dep"]


def test_computed_properties_after_override() -> None:
    """Test computed_properties after overriding a computed property."""
    context = Context()

    # Add initial property
    def func1(ctx: Context) -> str:
        return "first"

    context.add_computed_property("test", func1)

    props = context.computed_properties()
    assert len(props) == 1
    original_prop = props["test"]

    # Override with new property
    def func2(ctx: Context) -> str:
        return "second"

    context.add_computed_property("test", func2)

    props = context.computed_properties()
    assert len(props) == 1
    new_prop = props["test"]

    # Should be different ComputedProperty object
    assert new_prop is not original_prop
    assert new_prop.func is func2


def test_computed_properties_complex_functions() -> None:
    """Test computed_properties with complex computed functions."""
    context = Context()
    context["items"] = [1, 2, 3, 4, 5]

    def stats_func(ctx: Context) -> dict[str, Any]:
        items = ctx["items"]
        return {
            "sum": sum(items),
            "count": len(items),
            "average": sum(items) / len(items),
        }

    def filter_func(ctx: Context) -> list[int]:
        items = ctx["items"]
        return [x for x in items if x % 2 == 0]

    context.add_computed_property("stats", stats_func, ["items"])
    context.add_computed_property("evens", filter_func, ["items"])

    props = context.computed_properties()
    assert len(props) == 2
    assert "stats" in props
    assert "evens" in props

    # Functions should be preserved
    assert props["stats"].func is stats_func
    assert props["evens"].func is filter_func


def test_computed_properties_special_key_names() -> None:
    """Test computed_properties with special characters in key names."""
    context = Context()

    # Add properties with special characters
    context.add_computed_property("key-with-dashes", lambda ctx: "dashes")
    context.add_computed_property("key_with_underscores", lambda ctx: "underscores")
    context.add_computed_property("key.with.dots", lambda ctx: "dots")

    props = context.computed_properties()
    assert len(props) == 3
    assert "key-with-dashes" in props
    assert "key_with_underscores" in props
    assert "key.with.dots" in props


def test_computed_properties_error_functions() -> None:
    """Test computed_properties with functions that would raise errors."""
    context = Context()

    def error_func(ctx: Context) -> str:
        raise ValueError("This function always errors")

    context.add_computed_property("error_prop", error_func)

    props = context.computed_properties()
    assert len(props) == 1
    assert "error_prop" in props
    assert props["error_prop"].func is error_func
