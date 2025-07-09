"""Test Context.clear_history method."""

from context.main import Context


def test_clear_history_empty() -> None:
    """Test clear_history with no history does nothing."""
    context = Context()

    # Clear empty history
    context.clear_history()

    # Should still be empty
    history = context.get_change_history()
    assert history == []


def test_clear_history_with_changes() -> None:
    """Test clear_history removes all change events."""
    context = Context()

    # Make some changes
    context["key1"] = "value1"
    context["key2"] = "value2"
    context["key1"] = "updated_value1"

    # Verify history exists
    history_before = context.get_change_history()
    assert len(history_before) == 3

    # Clear history
    context.clear_history()

    # Verify history is empty
    history_after = context.get_change_history()
    assert history_after == []
    assert len(history_after) == 0


def test_clear_history_preserves_current_values() -> None:
    """Test that clear_history doesn't affect current context values."""
    context = Context()

    # Make some changes
    context["key1"] = "value1"
    context["key2"] = "value2"
    context["key1"] = "updated_value1"

    # Clear history
    context.clear_history()

    # Current values should be preserved
    assert context["key1"] == "updated_value1"
    assert context["key2"] == "value2"
    assert "key1" in context
    assert "key2" in context


def test_clear_history_allows_new_tracking() -> None:
    """Test that clear_history allows new changes to be tracked."""
    context = Context()

    # Make initial changes
    context["key1"] = "value1"
    context["key2"] = "value2"

    # Clear history
    context.clear_history()

    # Make new changes
    context["key3"] = "value3"
    context["key1"] = "new_value1"

    # New changes should be tracked
    history = context.get_change_history()
    assert len(history) == 2

    # Check that new changes are properly recorded
    assert history[0].key == "key1"
    assert history[0].old_value == "value1"
    assert history[0].new_value == "new_value1"

    assert history[1].key == "key3"
    assert history[1].old_value is None
    assert history[1].new_value == "value3"


def test_clear_history_multiple_calls() -> None:
    """Test multiple calls to clear_history."""
    context = Context()

    # Make changes
    context["key1"] = "value1"
    context["key2"] = "value2"

    # Clear history multiple times
    context.clear_history()
    context.clear_history()
    context.clear_history()

    # Should still be empty
    history = context.get_change_history()
    assert history == []


def test_clear_history_with_different_data_types() -> None:
    """Test clear_history with various data types."""
    context = Context()

    # Make changes with different types
    context["string"] = "test"
    context["number"] = 42
    context["list"] = [1, 2, 3]
    context["dict"] = {"nested": "value"}
    context["none"] = None

    # Clear history
    context.clear_history()

    # History should be empty
    history = context.get_change_history()
    assert history == []

    # Values should be preserved
    assert context["string"] == "test"
    assert context["number"] == 42
    assert context["list"] == [1, 2, 3]
    assert context["dict"] == {"nested": "value"}
    assert context["none"] is None


def test_clear_history_with_layers() -> None:
    """Test clear_history with multiple context layers."""
    context = Context()

    # Add data to base layer
    context["base"] = "base_value"

    # Push layer and add more data
    context.push_layer()
    context["layer1"] = "layer1_value"

    # Push another layer
    context.push_layer()
    context["layer2"] = "layer2_value"

    # Clear history
    context.clear_history()

    # History should be empty
    history = context.get_change_history()
    assert history == []

    # All values should be preserved
    assert context["base"] == "base_value"
    assert context["layer1"] == "layer1_value"
    assert context["layer2"] == "layer2_value"


def test_clear_history_context_isolation() -> None:
    """Test that clear_history only affects the specific context."""
    context1 = Context()
    context2 = Context()

    # Make changes to both contexts
    context1["key"] = "value1"
    context2["key"] = "value2"

    # Clear history for context1 only
    context1.clear_history()

    # Context1 history should be empty
    history1 = context1.get_change_history()
    assert history1 == []

    # Context2 history should be intact
    history2 = context2.get_change_history()
    assert len(history2) == 1
    assert history2[0].new_value == "value2"


def test_clear_history_return_type() -> None:
    """Test that clear_history returns None."""
    context = Context()
    context["key"] = "value"

    # Clear history - should return None
    context.clear_history()

    # Verify history is cleared
    history = context.get_change_history()
    assert history == []


def test_clear_history_after_limit_reached() -> None:
    """Test clear_history after history limit is reached."""
    context = Context()

    # Make many changes (more than default limit of 1000)
    for i in range(1100):
        context[f"key{i}"] = f"value{i}"

    # History should be limited
    history_before = context.get_change_history()
    assert len(history_before) <= 1000

    # Clear history
    context.clear_history()

    # History should be empty
    history_after = context.get_change_history()
    assert history_after == []


def test_clear_history_with_update_sequence() -> None:
    """Test clear_history with sequence of updates to same key."""
    context = Context()

    # Update same key multiple times
    context["key"] = "value1"
    context["key"] = "value2"
    context["key"] = "value3"
    context["key"] = "value4"

    # Clear history
    context.clear_history()

    # History should be empty
    history = context.get_change_history()
    assert history == []

    # Current value should be preserved
    assert context["key"] == "value4"


def test_clear_history_then_get_with_parameters() -> None:
    """Test get_change_history with parameters after clear_history."""
    context = Context()

    # Make changes
    context["key1"] = "value1"
    context["key2"] = "value2"

    # Clear history
    context.clear_history()

    # Get history with various parameters
    history_all = context.get_change_history()
    history_limit = context.get_change_history(limit=10)
    history_since = context.get_change_history(since=0.0)

    assert history_all == []
    assert history_limit == []
    assert history_since == []


def test_clear_history_integration_with_setitem() -> None:
    """Test clear_history integration with __setitem__ method."""
    context = Context()

    # Make changes using __setitem__
    context["key1"] = "value1"
    context["key2"] = "value2"

    # Clear history
    context.clear_history()

    # Make more changes
    context["key3"] = "value3"

    # Only new changes should be tracked
    history = context.get_change_history()
    assert len(history) == 1
    assert history[0].key == "key3"
    assert history[0].new_value == "value3"


def test_clear_history_preserves_context_state() -> None:
    """Test that clear_history preserves all context state except history."""
    context = Context()

    # Set up complex context state
    context["key1"] = "value1"
    context.push_layer()
    context["key2"] = "value2"

    # Get initial state
    initial_frames = len(context.frames)
    initial_keys = set(context.keys())

    # Clear history
    context.clear_history()

    # Context state should be preserved
    assert len(context.frames) == initial_frames
    assert context["key1"] == "value1"
    assert context["key2"] == "value2"
    assert set(context.keys()) == initial_keys

    # Only history should be cleared
    history = context.get_change_history()
    assert history == []
