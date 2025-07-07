"""Tests for the ContextFrame class."""

from context.frame import ContextFrame


def test_context_frame_init():
    """Test that ContextFrame.__init__ initializes an empty frame."""
    frame = ContextFrame()

    # The frame should have an empty data dictionary
    assert hasattr(frame, "data")
    assert frame.data == {}
    assert isinstance(frame.data, dict)
