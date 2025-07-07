"""Tests for the ContextFrame class."""

from context.frame import ContextFrame


def test_context_frame_init():
    """Test that ContextFrame.__init__ initializes an empty frame."""
    frame = ContextFrame()

    # The frame should have an empty data dictionary
    assert hasattr(frame, "data")
    assert frame.data == {}
    assert isinstance(frame.data, dict)


def test_context_frame_getitem():
    """Test that ContextFrame.__getitem__ retrieves values correctly."""
    frame = ContextFrame()

    # Set up test data directly in the data dict
    frame.data["test_key"] = "test_value"
    frame.data["number"] = 42
    frame.data["nested"] = {"inner": "value"}

    # Test basic value retrieval
    assert frame["test_key"] == "test_value"
    assert frame["number"] == 42
    assert frame["nested"] == {"inner": "value"}

    # Test KeyError for missing key
    try:
        _ = frame["missing_key"]
        assert False, "Should have raised KeyError"
    except KeyError:
        pass  # Expected behavior
