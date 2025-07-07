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


def _setup_test_values(frame: ContextFrame) -> None:
    """Helper to set up test values in frame."""
    frame["string_key"] = "hello"
    frame["int_key"] = 123
    frame["float_key"] = 3.14
    frame["bool_key"] = True
    frame["list_key"] = [1, 2, 3]
    frame["dict_key"] = {"nested": "object"}
    frame["none_key"] = None


def _verify_test_values(frame: ContextFrame) -> None:
    """Helper to verify test values were set correctly."""
    assert frame.data["string_key"] == "hello"
    assert frame.data["int_key"] == 123
    assert frame.data["float_key"] == 3.14
    assert frame.data["bool_key"] is True
    assert frame.data["list_key"] == [1, 2, 3]
    assert frame.data["dict_key"] == {"nested": "object"}
    assert frame.data["none_key"] is None


def test_context_frame_setitem():
    """Test that ContextFrame.__setitem__ sets values correctly."""
    frame = ContextFrame()

    # Test setting various types of values
    _setup_test_values(frame)
    _verify_test_values(frame)

    # Test overwriting existing values
    frame["string_key"] = "updated"
    assert frame.data["string_key"] == "updated"

    # Test that values are accessible via __getitem__
    assert frame["int_key"] == 123
    assert frame["dict_key"] == {"nested": "object"}


def test_context_frame_delitem():
    """Test that ContextFrame.__delitem__ deletes keys correctly."""
    frame = ContextFrame()

    # Set up test data
    frame.data["key1"] = "value1"
    frame.data["key2"] = "value2"
    frame.data["key3"] = "value3"

    # Test deleting existing keys
    del frame["key1"]
    assert "key1" not in frame.data
    assert frame.data == {"key2": "value2", "key3": "value3"}

    del frame["key2"]
    assert "key2" not in frame.data
    assert frame.data == {"key3": "value3"}

    # Test KeyError for missing key
    try:
        del frame["missing_key"]
        assert False, "Should have raised KeyError"
    except KeyError:
        pass  # Expected behavior
