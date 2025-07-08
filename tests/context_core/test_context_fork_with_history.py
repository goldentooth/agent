"""Test Context.fork_with_history method."""

import pytest

from context.main import Context


def test_fork_with_history_basic():
    """Test basic fork_with_history functionality."""
    context = Context()
    context["key1"] = "value1"
    context["key2"] = "value2"

    # Fork the context with history
    forked = context.fork_with_history()

    # Verify fork is a different instance
    assert forked is not context
    assert isinstance(forked, Context)

    # Verify fork has the same data
    assert forked["key1"] == "value1"
    assert forked["key2"] == "value2"


def test_fork_with_history_independence():
    """Test that fork_with_history creates independent contexts."""
    context = Context()
    context["shared_key"] = "original_value"

    # Fork the context with history
    forked = context.fork_with_history()

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


def test_fork_with_history_vs_regular_fork():
    """Test that fork_with_history preserves more than regular fork."""
    context = Context()
    context["test_key"] = "test_value"

    # Both fork types should work
    regular_fork = context.fork()
    history_fork = context.fork_with_history()

    # All should be different instances
    assert regular_fork is not context
    assert history_fork is not context
    assert regular_fork is not history_fork

    # All should have the same basic data
    assert regular_fork["test_key"] == "test_value"
    assert history_fork["test_key"] == "test_value"
    assert context["test_key"] == "test_value"


def _create_layered_context_for_history_fork():
    """Helper function to create a layered context for history fork testing."""
    context = Context()
    context["base_key"] = "base_value"

    # Add layers
    context.push_layer()
    context["layer1_key"] = "layer1_value"
    context["base_key"] = "shadowed_by_layer1"

    context.push_layer()
    context["layer2_key"] = "layer2_value"
    context["base_key"] = "shadowed_by_layer2"

    return context


def test_fork_with_history_with_multiple_frames():
    """Test fork_with_history with multiple frames (layers)."""
    context = _create_layered_context_for_history_fork()

    # Fork the context with history
    forked = context.fork_with_history()

    # Verify fork preserves layered structure
    assert len(forked.frames) == len(context.frames)
    assert forked["base_key"] == "shadowed_by_layer2"
    assert forked["layer1_key"] == "layer1_value"
    assert forked["layer2_key"] == "layer2_value"


def test_fork_with_history_layer_independence():
    """Test fork_with_history independence when layers are modified."""
    context = _create_layered_context_for_history_fork()
    forked = context.fork_with_history()

    # Modify original - should not affect fork
    context.pop_layer()
    assert context["base_key"] == "shadowed_by_layer1"

    # Fork should remain unchanged
    assert forked["base_key"] == "shadowed_by_layer2"
    assert forked["layer2_key"] == "layer2_value"


def test_fork_with_history_empty_context():
    """Test fork_with_history on an empty context."""
    context = Context()

    # Fork empty context with history
    forked = context.fork_with_history()

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


def test_fork_with_history_preserves_frame_layering():
    """Test that fork_with_history preserves exact frame layering behavior."""
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

    # Fork the context with history
    forked = context.fork_with_history()

    # Both should have identical access patterns
    assert context["a"] == forked["a"] == "layer2_a"
    assert context["b"] == forked["b"] == "layer1_b"
    assert context["c"] == forked["c"] == "layer1_c"
    assert context["d"] == forked["d"] == "layer2_d"


def _verify_context_instance_methods(context: Context) -> None:
    """Helper function to verify Context instance has all required methods."""
    assert isinstance(context, Context)
    assert hasattr(context, "get")
    assert hasattr(context, "set")
    assert hasattr(context, "push_layer")
    assert hasattr(context, "pop_layer")
    assert hasattr(context, "fork")
    assert hasattr(context, "fork_with_history")


def test_fork_with_history_returns_context_instance():
    """Test that fork_with_history returns a proper Context instance."""
    context = Context()
    context["test_key"] = "test_value"

    # Fork the context with history
    forked = context.fork_with_history()

    # Should be Context instance with all methods available
    _verify_context_instance_methods(forked)

    # Should work with all basic operations
    forked.push_layer()
    forked["new_key"] = "new_value"
    assert forked["new_key"] == "new_value"

    forked.pop_layer()
    with pytest.raises(KeyError):
        _ = forked["new_key"]


def _verify_nested_fork_independence(
    context: Context, first_fork: Context, second_fork: Context
) -> None:
    """Helper function to verify independence of nested forks."""
    # All should be independent
    assert context["original_key"] == "original_value"
    assert first_fork["original_key"] == "original_value"
    assert second_fork["original_key"] == "original_value"

    assert first_fork["first_fork_key"] == "first_fork_value"
    assert second_fork["first_fork_key"] == "first_fork_value"
    assert second_fork["second_fork_key"] == "second_fork_value"

    # Changes should not propagate
    with pytest.raises(KeyError):
        _ = context["first_fork_key"]
    with pytest.raises(KeyError):
        _ = context["second_fork_key"]
    with pytest.raises(KeyError):
        _ = first_fork["second_fork_key"]


def test_fork_with_history_can_be_forked_again():
    """Test that a fork_with_history result can be forked again."""
    context = Context()
    context["original_key"] = "original_value"

    # First fork with history
    first_fork = context.fork_with_history()
    first_fork["first_fork_key"] = "first_fork_value"

    # Second fork from the first fork
    second_fork = first_fork.fork_with_history()
    second_fork["second_fork_key"] = "second_fork_value"

    # Verify independence
    _verify_nested_fork_independence(context, first_fork, second_fork)


def test_fork_with_history_with_none_values():
    """Test fork_with_history with None values."""
    context = Context()
    context["none_key"] = None
    context["value_key"] = "value"

    # Fork the context with history
    forked = context.fork_with_history()

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
