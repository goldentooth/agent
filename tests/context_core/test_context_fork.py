"""Test Context.fork method."""

import pytest

from context.main import Context


def test_fork_basic() -> None:
    """Test basic fork functionality."""
    context = Context()
    context["key1"] = "value1"
    context["key2"] = "value2"

    # Fork the context
    forked = context.fork()

    # Verify fork is a different instance
    assert forked is not context
    assert isinstance(forked, Context)

    # Verify fork has the same data
    assert forked["key1"] == "value1"
    assert forked["key2"] == "value2"


def test_fork_independence() -> None:
    """Test that fork creates independent contexts."""
    context = Context()
    context["shared_key"] = "original_value"

    # Fork the context
    forked = context.fork()

    # Modify original context
    context["shared_key"] = "modified_original"
    context["new_key"] = "new_value"

    # Fork should remain unchanged
    assert forked["shared_key"] == "original_value"

    with pytest.raises(KeyError):
        _ = forked["new_key"]

    # Modify forked context
    forked["shared_key"] = "modified_fork"
    forked["fork_key"] = "fork_value"

    # Original should remain with its changes
    assert context["shared_key"] == "modified_original"
    assert context["new_key"] == "new_value"

    with pytest.raises(KeyError):
        _ = context["fork_key"]


def test_fork_with_multiple_frames() -> None:
    """Test forking with multiple frames (layers)."""
    context = Context()
    context["base_key"] = "base_value"

    # Add layers
    context.push_layer()
    context["layer1_key"] = "layer1_value"
    context["base_key"] = "shadowed_by_layer1"

    context.push_layer()
    context["layer2_key"] = "layer2_value"
    context["base_key"] = "shadowed_by_layer2"

    # Fork the context
    forked = context.fork()

    # Verify fork preserves layered structure
    assert len(forked.frames) == len(context.frames)
    assert forked["base_key"] == "shadowed_by_layer2"
    assert forked["layer1_key"] == "layer1_value"
    assert forked["layer2_key"] == "layer2_value"


def test_fork_with_multiple_frames_independence() -> None:
    """Test fork independence with multiple frames after modifications."""
    context = Context()
    context["base_key"] = "base_value"

    context.push_layer()
    context["layer1_key"] = "layer1_value"
    context["base_key"] = "shadowed_by_layer1"

    context.push_layer()
    context["layer2_key"] = "layer2_value"
    context["base_key"] = "shadowed_by_layer2"

    forked = context.fork()

    # Modify original - should not affect fork
    context.pop_layer()
    assert context["base_key"] == "shadowed_by_layer1"

    # Fork should remain unchanged
    assert forked["base_key"] == "shadowed_by_layer2"
    assert forked["layer2_key"] == "layer2_value"


def test_fork_frame_independence() -> None:
    """Test that forked frames are independent copies."""
    context = Context()
    context["key"] = ["original", "list"]

    # Fork the context
    forked = context.fork()

    # Modify the list in the original context
    context["key"].append("modified")

    # Fork should have the original list unchanged
    assert context["key"] == ["original", "list", "modified"]
    assert forked["key"] == ["original", "list"]


def test_fork_empty_context() -> None:
    """Test forking an empty context."""
    context = Context()

    # Fork empty context
    forked = context.fork()

    # Should be different instances
    assert forked is not context

    # Should have same frame structure
    assert len(forked.frames) == len(context.frames)

    # Should be able to add data independently
    context["original_key"] = "original_value"
    forked["fork_key"] = "fork_value"

    assert context["original_key"] == "original_value"
    assert forked["fork_key"] == "fork_value"

    with pytest.raises(KeyError):
        _ = context["fork_key"]
    with pytest.raises(KeyError):
        _ = forked["original_key"]


def _create_complex_layered_context_for_fork() -> None:
    """Helper function to create a complex layered context for fork testing."""
    context = Context()

    # Set up complex layering
    context["a"] = "base_a"
    context["b"] = "base_b"

    context.push_layer()
    context["b"] = "layer1_b"
    context["c"] = "layer1_c"

    context.push_layer()
    context["a"] = "layer2_a"
    context["d"] = "layer2_d"

    return context


def test_fork_preserves_frame_layering() -> None:
    """Test that fork preserves the exact frame layering behavior."""
    context = _create_complex_layered_context_for_fork()

    # Fork the context
    forked = context.fork()

    # Both should have identical access patterns
    assert context["a"] == forked["a"] == "layer2_a"
    assert context["b"] == forked["b"] == "layer1_b"
    assert context["c"] == forked["c"] == "layer1_c"
    assert context["d"] == forked["d"] == "layer2_d"


def test_fork_independence_after_layer_changes() -> None:
    """Test fork independence when original context layers are modified."""
    context = _create_complex_layered_context_for_fork()
    forked = context.fork()

    # Pop layer from original - should not affect fork
    context.pop_layer()

    # Original should show layer1 values
    assert context["a"] == "base_a"
    assert context["b"] == "layer1_b"
    assert context["c"] == "layer1_c"

    with pytest.raises(KeyError):
        _ = context["d"]

    # Fork should still show layer2 values
    assert forked["a"] == "layer2_a"
    assert forked["b"] == "layer1_b"
    assert forked["c"] == "layer1_c"
    assert forked["d"] == "layer2_d"


def test_fork_with_none_values() -> None:
    """Test forking with None values."""
    context = Context()
    context["none_key"] = None
    context["value_key"] = "value"

    # Fork the context
    forked = context.fork()

    # Both should have None value
    assert context["none_key"] is None
    assert forked["none_key"] is None

    # Both should have regular value
    assert context["value_key"] == "value"
    assert forked["value_key"] == "value"

    # Modify original to non-None
    context["none_key"] = "no_longer_none"

    # Fork should remain None
    assert forked["none_key"] is None
    assert context["none_key"] == "no_longer_none"


def test_fork_returns_context_instance() -> None:
    """Test that fork returns a proper Context instance."""
    context = Context()
    context["test_key"] = "test_value"

    # Fork the context
    forked = context.fork()

    # Should be Context instance with all methods available
    assert isinstance(forked, Context)
    assert hasattr(forked, "get")
    assert hasattr(forked, "set")
    assert hasattr(forked, "push_layer")
    assert hasattr(forked, "pop_layer")
    assert hasattr(forked, "fork")

    # Should work with all basic operations
    forked.push_layer()
    forked["new_key"] = "new_value"
    assert forked["new_key"] == "new_value"

    forked.pop_layer()
    with pytest.raises(KeyError):
        _ = forked["new_key"]
