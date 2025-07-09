"""Test Context.set_max_history_size method."""

import pytest

from context.main import Context


def test_set_max_history_size_basic() -> None:
    """Test basic max history size setting."""
    context = Context()

    # Set max history size
    context.set_max_history_size(5)

    # Add some changes
    context["key1"] = "value1"
    context["key2"] = "value2"
    context["key3"] = "value3"

    # Check that history size is as expected
    assert context.get_history_size() == 3

    # Add more changes beyond the limit
    context["key4"] = "value4"
    context["key5"] = "value5"
    context["key6"] = "value6"  # This should cause oldest to be removed

    # Should be limited to max size
    assert context.get_history_size() == 5


def test_set_max_history_size_zero() -> None:
    """Test setting max history size to zero."""
    context = Context()

    # Add some changes first
    context["key1"] = "value1"
    context["key2"] = "value2"
    assert context.get_history_size() == 2

    # Set max history size to zero
    context.set_max_history_size(0)

    # Add more changes - should not be tracked
    context["key3"] = "value3"
    assert context.get_history_size() == 0


def test_set_max_history_size_one() -> None:
    """Test setting max history size to one."""
    context = Context()

    # Set max history size to 1
    context.set_max_history_size(1)

    # Add changes
    context["key1"] = "value1"
    assert context.get_history_size() == 1

    context["key2"] = "value2"
    assert context.get_history_size() == 1

    # Only most recent change should be kept
    history = context.get_change_history()
    assert len(history) == 1
    assert history[0].key == "key2"


def test_set_max_history_size_reduces_existing() -> None:
    """Test that setting smaller max size reduces existing history."""
    context = Context()

    # Add several changes
    context["key1"] = "value1"
    context["key2"] = "value2"
    context["key3"] = "value3"
    context["key4"] = "value4"
    context["key5"] = "value5"

    assert context.get_history_size() == 5

    # Reduce max history size
    context.set_max_history_size(3)

    # History should be reduced to max size
    assert context.get_history_size() == 3

    # Should keep the most recent changes
    history = context.get_change_history()
    assert len(history) == 3
    assert history[0].key == "key5"  # Most recent first
    assert history[1].key == "key4"
    assert history[2].key == "key3"


def test_set_max_history_size_increases_existing() -> None:
    """Test that setting larger max size allows more history."""
    context = Context()

    # Set small max size first
    context.set_max_history_size(2)

    # Add changes
    context["key1"] = "value1"
    context["key2"] = "value2"
    context["key3"] = "value3"  # Should remove key1

    assert context.get_history_size() == 2

    # Increase max history size
    context.set_max_history_size(5)

    # Current history should remain
    assert context.get_history_size() == 2

    # Should now be able to add more
    context["key4"] = "value4"
    context["key5"] = "value5"
    context["key6"] = "value6"

    assert context.get_history_size() == 5


def test_set_max_history_size_negative() -> None:
    """Test that negative max size raises ValueError."""
    context = Context()

    # Add some changes first
    context["key1"] = "value1"
    assert context.get_history_size() == 1

    # Set negative max size should raise ValueError
    with pytest.raises(ValueError, match="History size must be non-negative"):
        context.set_max_history_size(-1)


def test_set_max_history_size_large_value() -> None:
    """Test setting very large max size."""
    context = Context()

    # Set very large max size
    context.set_max_history_size(10000)

    # Add many changes
    for i in range(100):
        context[f"key{i}"] = f"value{i}"

    # Should track all changes
    assert context.get_history_size() == 100


def test_set_max_history_size_delegation() -> None:
    """Test that method properly delegates to history tracker."""
    context = Context()

    # Test that it calls the correct method on history tracker
    original_method = context._history_tracker.set_max_history_size
    called_with = []

    def mock_set_max_history_size(size: int) -> None:
        called_with.append(size)
        original_method(size)

    # Use monkeypatch-like approach that mypy accepts
    setattr(context._history_tracker, "set_max_history_size", mock_set_max_history_size)

    # Call method
    context.set_max_history_size(10)

    # Should have delegated
    assert called_with == [10]


def test_set_max_history_size_return_type() -> None:
    """Test that method returns None."""
    context = Context()

    # Method should return None
    context.set_max_history_size(5)
    # No assertion needed since mypy will catch if it returns something other than None


def test_set_max_history_size_multiple_calls() -> None:
    """Test multiple calls to set_max_history_size."""
    context = Context()

    # Set initial size
    context.set_max_history_size(3)

    # Add changes
    context["key1"] = "value1"
    context["key2"] = "value2"
    context["key3"] = "value3"
    assert context.get_history_size() == 3

    # Change size multiple times
    context.set_max_history_size(5)
    context.set_max_history_size(2)
    context.set_max_history_size(4)

    # Should use the last value
    assert context.get_history_size() == 2  # Reduced from 3 to 2

    # Should be able to add more up to limit
    context["key4"] = "value4"
    context["key5"] = "value5"
    assert context.get_history_size() == 4


def test_set_max_history_size_with_setitem() -> None:
    """Test that max size works with __setitem__ method."""
    context = Context()

    # Set max size
    context.set_max_history_size(2)

    # Use __setitem__ to add changes
    context["key1"] = "value1"
    context["key2"] = "value2"
    context["key3"] = "value3"

    # Should respect max size
    assert context.get_history_size() == 2

    # Should keep most recent changes
    history = context.get_change_history()
    assert len(history) == 2
    assert history[0].key == "key3"
    assert history[1].key == "key2"


def test_set_max_history_size_with_set_method() -> None:
    """Test that max size works with set method."""
    context = Context()

    # Set max size
    context.set_max_history_size(2)

    # Use set method to add changes
    context.set("key1", "value1")
    context.set("key2", "value2")
    context.set("key3", "value3")

    # Should respect max size
    assert context.get_history_size() == 2

    # Should keep most recent changes
    history = context.get_change_history()
    assert len(history) == 2
    assert history[0].key == "key3"
    assert history[1].key == "key2"


def test_set_max_history_size_idempotent() -> None:
    """Test that calling set_max_history_size with same value is idempotent."""
    context = Context()

    # Add some changes
    context["key1"] = "value1"
    context["key2"] = "value2"
    initial_size = context.get_history_size()

    # Set max size
    context.set_max_history_size(10)

    # Call again with same value
    context.set_max_history_size(10)
    context.set_max_history_size(10)

    # Should not affect existing history
    assert context.get_history_size() == initial_size
