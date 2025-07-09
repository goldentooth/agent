"""Test Context.merge method."""

import pytest

from context.main import Context


def test_merge_basic() -> None:
    """Test basic merge functionality."""
    context = Context()
    context["base_key"] = "base_value"

    other_context = Context()
    other_context["other_key"] = "other_value"

    # Merge other context into current context
    context.merge(other_context)

    # Both keys should be accessible
    assert context["base_key"] == "base_value"
    assert context["other_key"] == "other_value"


def test_merge_key_overwrite() -> None:
    """Test that merge overwrites existing keys."""
    context = Context()
    context["shared_key"] = "original_value"
    context["context_key"] = "context_value"

    other_context = Context()
    other_context["shared_key"] = "new_value"
    other_context["other_key"] = "other_value"

    # Merge other context into current context
    context.merge(other_context)

    # Shared key should be overwritten
    assert context["shared_key"] == "new_value"
    assert context["context_key"] == "context_value"
    assert context["other_key"] == "other_value"


def test_merge_empty_context() -> None:
    """Test merging with an empty context."""
    context = Context()
    context["existing_key"] = "existing_value"

    empty_context = Context()

    # Merge empty context - should not change anything
    context.merge(empty_context)

    assert context["existing_key"] == "existing_value"
    assert len(context.frames) == 1


def test_merge_into_empty_context() -> None:
    """Test merging into an empty context."""
    context = Context()

    other_context = Context()
    other_context["test_key"] = "test_value"

    # Merge into empty context
    context.merge(other_context)

    assert context["test_key"] == "test_value"


def test_merge_with_multiple_frames() -> None:
    """Test merging contexts with multiple frames."""
    context = Context()
    context["base_key"] = "base_value"
    context.push_layer()
    context["layer_key"] = "layer_value"

    other_context = Context()
    other_context["other_base"] = "other_base_value"
    other_context.push_layer()
    other_context["other_layer"] = "other_layer_value"

    # Merge other context
    context.merge(other_context)

    # Should have all keys accessible
    assert context["base_key"] == "base_value"
    assert context["layer_key"] == "layer_value"
    assert context["other_base"] == "other_base_value"
    assert context["other_layer"] == "other_layer_value"


def test_merge_preserves_original_context() -> None:
    """Test that merge does not modify the source context."""
    context = Context()
    context["context_key"] = "context_value"

    other_context = Context()
    other_context["other_key"] = "other_value"

    # Store original state
    original_other_keys = list(other_context.frames[0].keys())

    # Merge
    context.merge(other_context)

    # Other context should be unchanged
    assert list(other_context.frames[0].keys()) == original_other_keys
    assert other_context["other_key"] == "other_value"

    # Original context should not have been affected
    with pytest.raises(KeyError):
        _ = other_context["context_key"]


def test_merge_with_none_values() -> None:
    """Test merging contexts with None values."""
    context = Context()
    context["existing_key"] = "existing_value"

    other_context = Context()
    other_context["none_key"] = None
    other_context["value_key"] = "value"

    # Merge
    context.merge(other_context)

    assert context["existing_key"] == "existing_value"
    assert context["none_key"] is None
    assert context["value_key"] == "value"


def test_merge_returns_self() -> None:
    """Test that merge returns the context for chaining."""
    context = Context()
    context["key1"] = "value1"

    other_context = Context()
    other_context["key2"] = "value2"

    # Merge should return self
    result = context.merge(other_context)

    assert result is context
    assert result["key1"] == "value1"
    assert result["key2"] == "value2"


def test_merge_with_layered_shadowing() -> None:
    """Test merge behavior with layered key shadowing."""
    context = Context()
    context["base_key"] = "base_value"
    context.push_layer()
    context["base_key"] = "shadowed_value"

    other_context = Context()
    other_context["base_key"] = "other_base_value"
    other_context.push_layer()
    other_context["base_key"] = "other_shadowed_value"

    # Merge
    context.merge(other_context)

    # Should access the top-level (merged) values
    assert context["base_key"] == "other_shadowed_value"


def test_merge_complex_data_types() -> None:
    """Test merging with complex data types."""
    context = Context()
    context["list_key"] = ["original", "list"]
    context["dict_key"] = {"original": "dict"}

    other_context = Context()
    other_context["list_key"] = ["new", "list"]
    other_context["dict_key"] = {"new": "dict"}

    # Merge
    context.merge(other_context)

    # Should overwrite with new values
    assert context["list_key"] == ["new", "list"]
    assert context["dict_key"] == {"new": "dict"}
