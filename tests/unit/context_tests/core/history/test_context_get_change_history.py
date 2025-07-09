"""Test Context.get_change_history method."""

import time

from context.history_tracker import ContextChangeEvent
from context.main import Context


def test_get_change_history_empty() -> None:
    """Test get_change_history with no changes returns empty list."""
    context = Context()

    history = context.get_change_history()

    assert history == []
    assert isinstance(history, list)


def test_get_change_history_single_change() -> None:
    """Test get_change_history with single change."""
    context = Context()

    # Make a change
    context["key1"] = "value1"

    # Get change history
    history = context.get_change_history()

    assert len(history) == 1
    assert isinstance(history[0], ContextChangeEvent)
    assert history[0].key == "key1"
    assert history[0].old_value is None
    assert history[0].new_value == "value1"
    assert history[0].context_id == id(context)
    assert isinstance(history[0].timestamp, float)


def test_get_change_history_multiple_changes() -> None:
    """Test get_change_history with multiple changes."""
    context = Context()

    # Make multiple changes
    context["key1"] = "value1"
    context["key2"] = "value2"
    context["key1"] = "updated_value1"

    # Get change history
    history = context.get_change_history()

    assert len(history) == 3

    # Check that history is in reverse chronological order (most recent first)
    assert history[0].key == "key1" and history[0].old_value == "value1"
    assert history[0].new_value == "updated_value1"

    assert history[1].key == "key2" and history[1].old_value is None
    assert history[1].new_value == "value2"

    assert history[2].key == "key1" and history[2].old_value is None
    assert history[2].new_value == "value1"


def test_get_change_history_with_limit() -> None:
    """Test get_change_history with limit parameter."""
    context = Context()

    # Make multiple changes
    context["key1"] = "value1"
    context["key2"] = "value2"
    context["key3"] = "value3"
    context["key4"] = "value4"

    # Get limited history
    history = context.get_change_history(limit=2)

    assert len(history) == 2
    assert history[0].key == "key4"
    assert history[1].key == "key3"


def test_get_change_history_with_since() -> None:
    """Test get_change_history with since parameter."""
    context = Context()

    # Make initial changes
    context["key1"] = "value1"
    context["key2"] = "value2"

    # Get checkpoint timestamp
    checkpoint = time.time()

    # Small delay to ensure different timestamps
    time.sleep(0.01)

    # Make more changes
    context["key3"] = "value3"
    context["key4"] = "value4"

    # Get history since checkpoint
    history = context.get_change_history(since=checkpoint)

    assert len(history) == 2
    assert history[0].key == "key4"
    assert history[1].key == "key3"

    # All timestamps should be after checkpoint
    for event in history:
        assert event.timestamp > checkpoint


def test_get_change_history_with_limit_and_since() -> None:
    """Test get_change_history with both limit and since parameters."""
    context = Context()

    # Make initial changes
    context["key1"] = "value1"
    context["key2"] = "value2"

    # Get checkpoint timestamp
    checkpoint = time.time()

    # Small delay to ensure different timestamps
    time.sleep(0.01)

    # Make more changes
    context["key3"] = "value3"
    context["key4"] = "value4"
    context["key5"] = "value5"

    # Get limited history since checkpoint
    history = context.get_change_history(limit=1, since=checkpoint)

    assert len(history) == 1
    assert history[0].key == "key5"
    assert history[0].timestamp > checkpoint


def test_get_change_history_tracks_value_updates() -> None:
    """Test that get_change_history properly tracks value updates."""
    context = Context()

    # Set initial value
    context["key"] = "initial"

    # Update value multiple times
    context["key"] = "updated1"
    context["key"] = "updated2"

    # Get change history
    history = context.get_change_history()

    assert len(history) == 3

    # Check progression of values
    assert history[0].old_value == "updated1"
    assert history[0].new_value == "updated2"

    assert history[1].old_value == "initial"
    assert history[1].new_value == "updated1"

    assert history[2].old_value is None
    assert history[2].new_value == "initial"


def test_get_change_history_different_data_types() -> None:
    """Test get_change_history with different data types."""
    context = Context()

    # Test different data types
    context["string"] = "test"
    context["number"] = 42
    context["list"] = [1, 2, 3]
    context["dict"] = {"nested": "value"}
    context["none"] = None

    # Get change history
    history = context.get_change_history()

    assert len(history) == 5

    # Check that different types are properly tracked
    values = {event.key: event.new_value for event in history}
    assert values["string"] == "test"
    assert values["number"] == 42
    assert values["list"] == [1, 2, 3]
    assert values["dict"] == {"nested": "value"}
    assert values["none"] is None


def test_get_change_history_with_layers() -> None:
    """Test get_change_history with multiple context layers."""
    context = Context()

    # Add data to base layer
    context["base"] = "base_value"

    # Push layer and add more data
    context.push_layer()
    context["layer1"] = "layer1_value"

    # Push another layer
    context.push_layer()
    context["layer2"] = "layer2_value"

    # Get change history
    history = context.get_change_history()

    assert len(history) == 3

    # All changes should be tracked regardless of layer
    keys = [event.key for event in history]
    assert "layer2" in keys
    assert "layer1" in keys
    assert "base" in keys


def test_get_change_history_context_isolation() -> None:
    """Test that different contexts have separate change histories."""
    context1 = Context()
    context2 = Context()

    # Make changes to both contexts
    context1["key"] = "value1"
    context2["key"] = "value2"

    # Get separate histories
    history1 = context1.get_change_history()
    history2 = context2.get_change_history()

    assert len(history1) == 1
    assert len(history2) == 1

    assert history1[0].new_value == "value1"
    assert history2[0].new_value == "value2"

    # Context IDs should be different
    assert history1[0].context_id == id(context1)
    assert history2[0].context_id == id(context2)
    assert history1[0].context_id != history2[0].context_id


def test_get_change_history_timestamp_ordering() -> None:
    """Test that change history is ordered by timestamp."""
    context = Context()

    # Make changes with small delays
    context["key1"] = "value1"
    time.sleep(0.01)
    context["key2"] = "value2"
    time.sleep(0.01)
    context["key3"] = "value3"

    # Get change history
    history = context.get_change_history()

    assert len(history) == 3

    # Should be in reverse chronological order
    assert history[0].timestamp > history[1].timestamp
    assert history[1].timestamp > history[2].timestamp

    # Check keys are in expected order
    assert history[0].key == "key3"
    assert history[1].key == "key2"
    assert history[2].key == "key1"


def test_get_change_history_return_type() -> None:
    """Test that get_change_history returns proper types."""
    context = Context()
    context["key"] = "value"

    # Get change history
    history = context.get_change_history()

    assert isinstance(history, list)
    assert len(history) == 1
    assert isinstance(history[0], ContextChangeEvent)

    # Check event attributes
    event = history[0]
    assert isinstance(event.key, str)
    assert isinstance(event.timestamp, float)
    assert hasattr(event, "old_value")
    assert hasattr(event, "new_value")
    assert isinstance(event.context_id, int)


def test_get_change_history_with_setitem() -> None:
    """Test that get_change_history tracks changes made with __setitem__."""
    context = Context()

    # Use __setitem__ syntax
    context["key1"] = "value1"
    context["key2"] = "value2"

    # Get change history
    history = context.get_change_history()

    assert len(history) == 2
    assert history[0].key == "key2"
    assert history[1].key == "key1"


def test_get_change_history_independence() -> None:
    """Test that get_change_history returns independent lists."""
    context = Context()
    context["key"] = "value"

    # Get history multiple times
    history1 = context.get_change_history()
    history2 = context.get_change_history()

    # Should be independent objects
    assert history1 is not history2
    assert len(history1) == len(history2)

    # Modifying one should not affect the other
    # Create a dummy ContextChangeEvent for testing independence
    dummy_event = ContextChangeEvent("dummy", None, "dummy", id(context))
    history1.append(dummy_event)
    assert len(history2) == 1
