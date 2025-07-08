"""Test Context.push_layer method."""

import pytest

from context.frame import ContextFrame
from context.main import Context


def test_push_layer_basic() -> None:
    """Test basic push_layer functionality."""
    context = Context()
    initial_frame_count = len(context.frames)

    # Push a new layer
    context.push_layer()

    # Verify frame count increased
    assert len(context.frames) == initial_frame_count + 1

    # Verify the new frame is a ContextFrame
    assert isinstance(context.frames[-1], ContextFrame)


def test_push_layer_multiple() -> None:
    """Test pushing multiple layers."""
    context = Context()
    initial_frame_count = len(context.frames)

    # Push multiple layers
    context.push_layer()
    context.push_layer()
    context.push_layer()

    # Verify frame count increased by 3
    assert len(context.frames) == initial_frame_count + 3

    # Verify all frames are ContextFrame instances
    for frame in context.frames:
        assert isinstance(frame, ContextFrame)


def test_push_layer_isolation() -> None:
    """Test that new layers isolate changes."""
    context = Context()
    context["base_key"] = "base_value"

    # Push a new layer
    context.push_layer()

    # Set a value in the new layer
    context["new_key"] = "new_value"

    # Both keys should be accessible
    assert context["base_key"] == "base_value"
    assert context["new_key"] == "new_value"

    # The new key should only exist in the top frame
    assert "new_key" not in context.frames[0]  # base frame
    assert "new_key" in context.frames[1]  # new frame


def test_push_layer_shadowing() -> None:
    """Test that new layers can shadow values from lower layers."""
    context = Context()
    context["shared_key"] = "original_value"

    # Push a new layer
    context.push_layer()

    # Override the value in the new layer
    context["shared_key"] = "new_value"

    # The context should return the new value
    assert context["shared_key"] == "new_value"

    # The original value should still exist in the base frame
    assert context.frames[0]["shared_key"] == "original_value"

    # The new value should exist in the top frame
    assert context.frames[1]["shared_key"] == "new_value"


def test_push_layer_preserves_existing_data() -> None:
    """Test that pushing layers preserves existing data."""
    context = Context()
    context["key1"] = "value1"
    context["key2"] = "value2"

    # Push a new layer
    context.push_layer()

    # Original data should still be accessible
    assert context["key1"] == "value1"
    assert context["key2"] == "value2"

    # Original data should still exist in the base frame
    assert context.frames[0]["key1"] == "value1"
    assert context.frames[0]["key2"] == "value2"


def test_push_layer_with_empty_context() -> None:
    """Test pushing layers on an empty context."""
    context = Context()

    # Verify initial state
    assert len(context.frames) == 1  # Should have root frame

    # Push a layer
    context.push_layer()

    # Verify new layer was added
    assert len(context.frames) == 2

    # Both frames should be empty
    assert len(context.frames[0].data) == 0
    assert len(context.frames[1].data) == 0


def test_push_layer_returns_none() -> None:
    """Test that push_layer returns None."""
    context = Context()

    # Method should return None
    result = context.push_layer()
    assert result is None
