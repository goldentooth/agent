"""Test Context.pop_layer method."""

import pytest

from context.main import Context


def test_pop_layer_basic() -> None:
    """Test basic pop_layer functionality."""
    context = Context()
    initial_frame_count = len(context.frames)

    # Push a layer then pop it
    context.push_layer()
    assert len(context.frames) == initial_frame_count + 1

    context.pop_layer()
    assert len(context.frames) == initial_frame_count


def test_pop_layer_multiple() -> None:
    """Test popping multiple layers."""
    context = Context()
    initial_frame_count = len(context.frames)

    # Push multiple layers
    context.push_layer()
    context.push_layer()
    context.push_layer()
    assert len(context.frames) == initial_frame_count + 3

    # Pop them one by one
    context.pop_layer()
    assert len(context.frames) == initial_frame_count + 2

    context.pop_layer()
    assert len(context.frames) == initial_frame_count + 1

    context.pop_layer()
    assert len(context.frames) == initial_frame_count


def test_pop_layer_restores_shadowed_values() -> None:
    """Test that popping layers restores shadowed values."""
    context = Context()
    context["shared_key"] = "original_value"

    # Push a layer and shadow the value
    context.push_layer()
    context["shared_key"] = "shadowed_value"
    assert context["shared_key"] == "shadowed_value"

    # Pop the layer - should restore original value
    context.pop_layer()
    assert context["shared_key"] == "original_value"


def test_pop_layer_removes_layer_specific_values() -> None:
    """Test that popping layers removes values specific to that layer."""
    context = Context()
    context["base_key"] = "base_value"

    # Push a layer and add a layer-specific value
    context.push_layer()
    context["layer_key"] = "layer_value"

    # Both keys should be accessible
    assert context["base_key"] == "base_value"
    assert context["layer_key"] == "layer_value"

    # Pop the layer - layer_key should no longer exist
    context.pop_layer()
    assert context["base_key"] == "base_value"

    with pytest.raises(KeyError):
        _ = context["layer_key"]


def test_pop_layer_cannot_pop_root_frame() -> None:
    """Test that popping the root frame raises IndexError."""
    context = Context()

    # Should have root frame
    assert len(context.frames) == 1

    # Attempting to pop the root frame should raise IndexError
    with pytest.raises(IndexError, match="Cannot pop root context frame"):
        context.pop_layer()

    # Frame count should remain unchanged
    assert len(context.frames) == 1


def test_pop_layer_with_one_pushed_layer() -> None:
    """Test popping when there's only one pushed layer above root."""
    context = Context()
    context["root_key"] = "root_value"

    # Push one layer
    context.push_layer()
    context["layer_key"] = "layer_value"

    # Both keys should be accessible
    assert context["root_key"] == "root_value"
    assert context["layer_key"] == "layer_value"

    # Pop the layer
    context.pop_layer()

    # Only root key should remain
    assert context["root_key"] == "root_value"
    with pytest.raises(KeyError):
        _ = context["layer_key"]

    # Should not be able to pop again (root protection)
    with pytest.raises(IndexError, match="Cannot pop root context frame"):
        context.pop_layer()


def _create_complex_layered_context() -> Context:
    """Helper function to create a complex layered context for testing."""
    context = Context()

    # Set base values
    context["a"] = "base_a"
    context["b"] = "base_b"

    # Layer 1
    context.push_layer()
    context["b"] = "layer1_b"  # Shadow base_b
    context["c"] = "layer1_c"  # New value

    # Layer 2
    context.push_layer()
    context["a"] = "layer2_a"  # Shadow base_a
    context["c"] = "layer2_c"  # Shadow layer1_c
    context["d"] = "layer2_d"  # New value

    return context


def test_pop_layer_complex_layering_setup() -> None:
    """Test complex layering setup and verification."""
    context = _create_complex_layered_context()

    # Verify current state
    assert context["a"] == "layer2_a"
    assert context["b"] == "layer1_b"
    assert context["c"] == "layer2_c"
    assert context["d"] == "layer2_d"


def test_pop_layer_complex_layering_pop_sequence() -> None:
    """Test complex layering pop sequence and value restoration."""
    context = _create_complex_layered_context()

    # Pop layer 2
    context.pop_layer()
    assert context["a"] == "base_a"  # Restored to base
    assert context["b"] == "layer1_b"  # Still from layer 1
    assert context["c"] == "layer1_c"  # Restored to layer 1

    with pytest.raises(KeyError):
        _ = context["d"]  # Gone with layer 2

    # Pop layer 1
    context.pop_layer()
    assert context["a"] == "base_a"  # Still base
    assert context["b"] == "base_b"  # Restored to base

    with pytest.raises(KeyError):
        _ = context["c"]  # Gone with layer 1


def test_pop_layer_returns_none() -> None:
    """Test that pop_layer returns None."""
    context = Context()
    context.push_layer()

    # Method should return None
    result = context.pop_layer()  # type: ignore[func-returns-value]
    assert result is None


def test_pop_layer_preserves_base_data_integrity() -> None:
    """Test that popping layers doesn't affect base data integrity."""
    context = Context()

    # Set complex base data
    base_data = {
        "string": "test",
        "number": 42,
        "list": [1, 2, 3],
        "dict": {"nested": "value"},
    }

    for key, value in base_data.items():
        context[key] = value

    # Push and pop multiple layers with various operations
    context.push_layer()
    context["temp"] = "temporary"
    context["string"] = "modified"

    context.push_layer()
    context["temp2"] = "temporary2"

    # Pop all pushed layers
    context.pop_layer()
    context.pop_layer()

    # Verify base data is intact
    for key, expected_value in base_data.items():
        assert context[key] == expected_value

    # Verify temporary values are gone
    with pytest.raises(KeyError):
        _ = context["temp"]
    with pytest.raises(KeyError):
        _ = context["temp2"]
