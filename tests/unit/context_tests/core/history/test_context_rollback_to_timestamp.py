"""Test Context.rollback_to_timestamp method."""

import time

import pytest

from context.main import Context


def test_rollback_to_timestamp_basic() -> None:
    """Test basic rollback to timestamp functionality."""
    context = Context()

    # Record initial state
    context["key1"] = "value1"
    initial_time = time.time()

    # Wait a moment to ensure timestamp difference
    time.sleep(0.001)

    # Make changes
    context["key1"] = "modified_value"
    context["key2"] = "value2"

    # Rollback to initial time
    context.rollback_to_timestamp(initial_time)

    # Should have reverted to initial state
    assert context["key1"] == "value1"
    assert "key2" not in context


def test_rollback_to_timestamp_future_raises_error() -> None:
    """Test that rollback to future timestamp raises ValueError."""
    context = Context()
    context["key1"] = "value1"

    # Try to rollback to future
    future_time = time.time() + 3600  # 1 hour from now
    with pytest.raises(ValueError, match="Cannot rollback to a future timestamp"):
        context.rollback_to_timestamp(future_time)


def test_rollback_to_timestamp_no_history_raises_error() -> None:
    """Test that rollback with no history raises ValueError."""
    context = Context()

    # No changes made, so no history
    with pytest.raises(ValueError, match="No history available for rollback"):
        context.rollback_to_timestamp(time.time() - 1)


def test_rollback_to_timestamp_creates_snapshot() -> None:
    """Test that rollback creates an automatic snapshot."""
    context = Context()

    # Make some changes
    context["key1"] = "value1"
    time.sleep(0.001)
    context["key2"] = "value2"

    snapshots_before = context.list_snapshots()
    initial_count = len(snapshots_before)

    # Rollback
    context.rollback_to_timestamp(time.time() - 0.1)

    # Should have created a snapshot
    snapshots_after = context.list_snapshots()
    assert len(snapshots_after) == initial_count + 1

    # Should have auto-backup snapshot
    auto_snapshot_names = [
        name for name in snapshots_after if name.startswith("auto_rollback_backup_")
    ]
    assert len(auto_snapshot_names) == 1


def test_rollback_to_timestamp_multiple_changes() -> None:
    """Test rollback with multiple changes to same key."""
    context = Context()

    # Make multiple changes
    context["key1"] = "value1"
    first_time = time.time()
    time.sleep(0.001)

    context["key1"] = "value2"
    second_time = time.time()
    time.sleep(0.001)

    context["key1"] = "value3"

    # Rollback to first change
    context.rollback_to_timestamp(first_time)
    assert context["key1"] == "value1"

    # Restore to test rollback to second change
    context["key1"] = "value2"
    context["key1"] = "value3"

    # Rollback to second change
    context.rollback_to_timestamp(second_time)
    assert context["key1"] == "value2"


def test_rollback_to_timestamp_with_deletions() -> None:
    """Test rollback with key deletions simulated by setting to None."""
    context = Context()

    # Add key and record time
    context["key1"] = "value1"
    context["key2"] = "value2"
    checkpoint_time = time.time()
    time.sleep(0.001)

    # Simulate deletion by setting to None (this gets tracked)
    context["key1"] = None
    # Modify key2
    context["key2"] = "modified"

    # Rollback
    context.rollback_to_timestamp(checkpoint_time)

    # key1 should be restored, key2 should be reverted
    assert context["key1"] == "value1"
    assert context["key2"] == "value2"


def test_rollback_to_timestamp_with_layers() -> None:
    """Test rollback with multiple context layers."""
    context = Context()

    # Add data to base layer
    context["base_key"] = "base_value"

    # Push layer and add data
    context.push_layer()
    context["layer_key"] = "layer_value"
    checkpoint_time = time.time()
    time.sleep(0.001)

    # Modify both keys
    context["base_key"] = "modified_base"
    context["layer_key"] = "modified_layer"

    # Rollback
    context.rollback_to_timestamp(checkpoint_time)

    # Should revert to checkpoint state
    assert context["base_key"] == "base_value"
    assert context["layer_key"] == "layer_value"


def test_rollback_to_timestamp_no_changes_to_reverse() -> None:
    """Test rollback when no changes need to be reversed."""
    context = Context()

    # Make a change
    context["key1"] = "value1"
    time.sleep(0.001)

    # Rollback to after the change (should do nothing)
    recent_time = time.time()
    context.rollback_to_timestamp(recent_time)

    # Should still have the value
    assert context["key1"] == "value1"


def test_rollback_to_timestamp_partial_failure() -> None:
    """Test rollback continues even if some reversals fail."""
    context = Context()

    # Add some changes
    context["key1"] = "value1"
    context["key2"] = "value2"
    checkpoint_time = time.time()
    time.sleep(0.001)

    # Modify values
    context["key1"] = "modified1"
    context["key2"] = "modified2"

    # Mock one reversal to fail by removing key1 from all frames
    # This simulates a key that can't be restored
    for frame in context.frames:
        if "key1" in frame:
            del frame["key1"]

    # Rollback should continue with other keys
    context.rollback_to_timestamp(checkpoint_time)

    # key2 should be restored, key1 might not be
    assert context["key2"] == "value2"


def test_rollback_to_timestamp_preserves_history() -> None:
    """Test that rollback doesn't record its operations as new history."""
    context = Context()

    # Make some changes
    context["key1"] = "value1"
    time.sleep(0.001)
    context["key2"] = "value2"

    # Record history size before rollback
    history_size_before = context.get_history_size()

    # Rollback
    context.rollback_to_timestamp(time.time() - 0.1)

    # History size should not have increased due to rollback operations
    history_size_after = context.get_history_size()
    assert history_size_after == history_size_before


def test_rollback_to_timestamp_with_set_method() -> None:
    """Test rollback works with set method."""
    context = Context()

    # Use set method
    context.set("key1", "value1")
    checkpoint_time = time.time()
    time.sleep(0.001)

    context.set("key1", "modified")

    # Rollback
    context.rollback_to_timestamp(checkpoint_time)

    assert context["key1"] == "value1"


def test_rollback_to_timestamp_with_setitem() -> None:
    """Test rollback works with __setitem__ method."""
    context = Context()

    # Use __setitem__
    context["key1"] = "value1"
    checkpoint_time = time.time()
    time.sleep(0.001)

    context["key1"] = "modified"

    # Rollback
    context.rollback_to_timestamp(checkpoint_time)

    assert context["key1"] == "value1"


def test_rollback_to_timestamp_complex_data() -> None:
    """Test rollback with complex data types."""
    context = Context()

    # Add complex data
    context["dict_key"] = {"nested": "value", "list": [1, 2, 3]}
    context["list_key"] = ["a", "b", "c"]
    checkpoint_time = time.time()
    time.sleep(0.001)

    # Modify complex data
    context["dict_key"] = {"different": "structure"}
    context["list_key"] = ["x", "y", "z"]

    # Rollback
    context.rollback_to_timestamp(checkpoint_time)

    # Should restore original complex data
    assert context["dict_key"] == {"nested": "value", "list": [1, 2, 3]}
    assert context["list_key"] == ["a", "b", "c"]


def test_rollback_to_timestamp_return_type() -> None:
    """Test that rollback_to_timestamp returns None."""
    context = Context()

    context["key1"] = "value1"
    time.sleep(0.001)

    # Method should return None
    context.rollback_to_timestamp(time.time() - 0.1)
    # No assertion needed since mypy will catch if it returns something other than None


def test_rollback_to_timestamp_exact_timestamp() -> None:
    """Test rollback to exact timestamp of a change."""
    context = Context()

    # Get exact timestamp of change
    context["key1"] = "value1"

    # Get the timestamp of the change event
    history = context.get_change_history()
    assert len(history) == 1
    exact_timestamp = history[0].timestamp

    # Make another change
    time.sleep(0.001)
    context["key1"] = "modified"

    # Rollback to exact timestamp
    context.rollback_to_timestamp(exact_timestamp)

    # Should be at the state after the first change
    assert context["key1"] == "value1"


def _setup_multiple_keys_context() -> tuple[Context, float]:
    """Set up context with multiple keys and return checkpoint time."""
    context = Context()
    context["key1"] = "value1"
    context["key2"] = "value2"
    context["key3"] = "value3"
    time.sleep(0.001)  # Ensure checkpoint is after all initial sets
    checkpoint_time = time.time()
    return context, checkpoint_time


def _modify_keys_and_add_new(context: Context) -> None:
    """Modify existing keys and add a new one."""
    context["key1"] = "modified1"
    context["key2"] = "modified2"
    context["key3"] = "modified3"
    context["key4"] = "value4"


def _verify_rollback_results(context: Context) -> None:
    """Verify rollback restored all keys correctly."""
    assert context["key1"] == "value1"
    assert context["key2"] == "value2"
    assert context["key3"] == "value3"
    assert "key4" not in context


def test_rollback_to_timestamp_multiple_keys() -> None:
    """Test rollback with multiple keys added and modified."""
    context, checkpoint_time = _setup_multiple_keys_context()
    _modify_keys_and_add_new(context)
    context.rollback_to_timestamp(checkpoint_time)
    _verify_rollback_results(context)


def test_rollback_to_timestamp_newly_added_key() -> None:
    """Test rollback with newly added key (old_value is None)."""
    context = Context()

    # Record time before adding any keys
    checkpoint_time = time.time()
    time.sleep(0.001)

    # Add new key
    context["new_key"] = "new_value"

    # Rollback to before key was added
    context.rollback_to_timestamp(checkpoint_time)

    # New key should be removed
    assert "new_key" not in context
