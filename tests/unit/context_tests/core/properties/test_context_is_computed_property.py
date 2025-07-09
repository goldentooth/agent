"""Test Context.is_computed_property method."""

import pytest

from context.main import Context


def test_is_computed_property_basic() -> None:
    """Test basic is_computed_property functionality."""
    context = Context()
    context["regular"] = "value"

    def computed_func(ctx: Context) -> str:
        return "computed"

    context.add_computed_property("computed", computed_func)

    # Should return True for computed property
    assert context.is_computed_property("computed") is True

    # Should return False for regular key
    assert context.is_computed_property("regular") is False


def test_is_computed_property_nonexistent() -> None:
    """Test is_computed_property with non-existent key."""
    context = Context()

    # Should return False for non-existent key
    assert context.is_computed_property("nonexistent") is False


def test_is_computed_property_multiple() -> None:
    """Test is_computed_property with multiple computed properties."""
    context = Context()
    context["regular1"] = "value1"
    context["regular2"] = "value2"

    # Add multiple computed properties
    context.add_computed_property("computed1", lambda ctx: "comp1")
    context.add_computed_property("computed2", lambda ctx: "comp2")
    context.add_computed_property("computed3", lambda ctx: "comp3")

    # Check computed properties
    assert context.is_computed_property("computed1") is True
    assert context.is_computed_property("computed2") is True
    assert context.is_computed_property("computed3") is True

    # Check regular keys
    assert context.is_computed_property("regular1") is False
    assert context.is_computed_property("regular2") is False


def test_is_computed_property_after_removal() -> None:
    """Test is_computed_property after removing computed property."""
    context = Context()

    # Add computed property
    context.add_computed_property("temp", lambda ctx: "temporary")
    assert context.is_computed_property("temp") is True

    # Remove it
    context.remove_computed_property("temp")
    assert context.is_computed_property("temp") is False


def test_is_computed_property_empty_context() -> None:
    """Test is_computed_property with empty context."""
    context = Context()

    # Should return False for any key in empty context
    assert context.is_computed_property("anything") is False
    assert context.is_computed_property("") is False


def test_is_computed_property_no_dependencies() -> None:
    """Test is_computed_property with property that has no dependencies."""
    context = Context()

    def constant_func(ctx: Context) -> str:
        return "constant"

    context.add_computed_property("const", constant_func, [])
    assert context.is_computed_property("const") is True


def test_is_computed_property_with_dependencies() -> None:
    """Test is_computed_property with property that has dependencies."""
    context = Context()
    context["base"] = 10

    def dependent_func(ctx: Context) -> int:
        return int(ctx["base"]) * 2

    context.add_computed_property("dependent", dependent_func, ["base"])
    assert context.is_computed_property("dependent") is True
    assert context.is_computed_property("base") is False


def test_is_computed_property_overridden_regular_key() -> None:
    """Test is_computed_property when computed property overrides regular key."""
    context = Context()

    # Set regular key
    context["key"] = "regular_value"
    assert context.is_computed_property("key") is False

    # Add computed property with same key (should override)
    context.add_computed_property("key", lambda ctx: "computed_value")
    assert context.is_computed_property("key") is True

    # Remove computed property (should reveal regular key again)
    context.remove_computed_property("key")
    assert context.is_computed_property("key") is False


def test_is_computed_property_case_sensitive() -> None:
    """Test that is_computed_property is case sensitive."""
    context = Context()

    context.add_computed_property("Test", lambda ctx: "computed")

    assert context.is_computed_property("Test") is True
    assert context.is_computed_property("test") is False
    assert context.is_computed_property("TEST") is False


def test_is_computed_property_special_characters() -> None:
    """Test is_computed_property with special characters in key names."""
    context = Context()

    # Add computed properties with special characters
    context.add_computed_property("key-with-dashes", lambda ctx: "dashes")
    context.add_computed_property("key_with_underscores", lambda ctx: "underscores")
    context.add_computed_property("key.with.dots", lambda ctx: "dots")
    context.add_computed_property("key with spaces", lambda ctx: "spaces")

    assert context.is_computed_property("key-with-dashes") is True
    assert context.is_computed_property("key_with_underscores") is True
    assert context.is_computed_property("key.with.dots") is True
    assert context.is_computed_property("key with spaces") is True


def test_is_computed_property_return_type() -> None:
    """Test that is_computed_property returns bool type."""
    context = Context()

    # Test with non-existent key
    result = context.is_computed_property("nonexistent")
    assert isinstance(result, bool)
    assert result is False

    # Test with computed property
    context.add_computed_property("computed", lambda ctx: "value")
    result = context.is_computed_property("computed")
    assert isinstance(result, bool)
    assert result is True


def test_is_computed_property_with_layers() -> None:
    """Test is_computed_property with multiple context layers."""
    context = Context()

    # Add to base layer
    context["base_regular"] = "base_value"
    context.add_computed_property("base_computed", lambda ctx: "base_comp")

    # Push layer
    context.push_layer()
    context["layer_regular"] = "layer_value"
    context.add_computed_property("layer_computed", lambda ctx: "layer_comp")

    # Check properties from both layers
    assert context.is_computed_property("base_computed") is True
    assert context.is_computed_property("layer_computed") is True
    assert context.is_computed_property("base_regular") is False
    assert context.is_computed_property("layer_regular") is False


def test_is_computed_property_complex_function() -> None:
    """Test is_computed_property with complex computed function."""
    context = Context()
    context["items"] = [1, 2, 3, 4, 5]

    def complex_stats(ctx: Context) -> dict[str, int]:
        items = ctx["items"]
        return {
            "sum": sum(items),
            "count": len(items),
            "max": max(items) if items else 0,
        }

    context.add_computed_property("stats", complex_stats, ["items"])
    assert context.is_computed_property("stats") is True
    assert context.is_computed_property("items") is False


def test_is_computed_property_error_function() -> None:
    """Test is_computed_property with function that would raise errors."""
    context = Context()

    def error_func(ctx: Context) -> str:
        raise ValueError("This function always errors")

    context.add_computed_property("error_prop", error_func)

    # Should still return True even if the function would error when called
    assert context.is_computed_property("error_prop") is True
