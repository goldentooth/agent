"""Tests for history_tracker module."""

import time
from unittest.mock import patch

import pytest

from context.history_tracker import ContextChangeEvent, HistoryTracker


class TestContextChangeEvent:
    """Test suite for ContextChangeEvent class."""

    def test_init_basic(self) -> None:
        """Test basic initialization of ContextChangeEvent."""
        key = "test_key"
        old_value = "old"
        new_value = "new"
        context_id = 123

        # Mock time.time() to ensure consistent timestamp
        with patch("time.time", return_value=1000.0):
            event = ContextChangeEvent(key, old_value, new_value, context_id)

        assert event.key == key
        assert event.old_value == old_value
        assert event.new_value == new_value
        assert event.context_id == context_id
        assert event.timestamp == 1000.0

    def test_init_with_none_values(self) -> None:
        """Test initialization with None values."""
        event = ContextChangeEvent("key", None, None, 0)

        assert event.key == "key"
        assert event.old_value is None
        assert event.new_value is None
        assert event.context_id == 0
        assert isinstance(event.timestamp, float)

    def test_init_with_complex_values(self) -> None:
        """Test initialization with complex data types."""
        key = "complex_key"
        old_value = {"nested": {"data": [1, 2, 3]}}
        new_value = [{"item": 1}, {"item": 2}]
        context_id = 456

        event = ContextChangeEvent(key, old_value, new_value, context_id)

        assert event.key == key
        assert event.old_value == old_value
        assert event.new_value == new_value
        assert event.context_id == context_id

    def test_init_with_empty_string_key(self) -> None:
        """Test initialization with empty string key."""
        event = ContextChangeEvent("", "old", "new", 789)

        assert event.key == ""
        assert event.old_value == "old"
        assert event.new_value == "new"
        assert event.context_id == 789

    def test_init_with_negative_context_id(self) -> None:
        """Test initialization with negative context ID."""
        event = ContextChangeEvent("key", "old", "new", -1)

        assert event.context_id == -1
        assert event.key == "key"

    def test_timestamp_is_current_time(self) -> None:
        """Test that timestamp is set to current time."""
        before_creation = time.time()
        event = ContextChangeEvent("key", "old", "new", 1)
        after_creation = time.time()

        assert before_creation <= event.timestamp <= after_creation

    def test_init_multiple_events_have_different_timestamps(self) -> None:
        """Test that multiple events created in sequence have different timestamps."""
        event1 = ContextChangeEvent("key1", "old1", "new1", 1)
        time.sleep(0.001)  # Small delay to ensure different timestamps
        event2 = ContextChangeEvent("key2", "old2", "new2", 2)

        assert event1.timestamp < event2.timestamp

    def test_init_with_various_types(self) -> None:
        """Test initialization with various Python types."""
        test_cases = [
            ("string_key", "str_old", "str_new"),
            ("int_key", 42, 43),
            ("float_key", 3.14, 2.71),
            ("bool_key", True, False),
            ("list_key", [1, 2], [3, 4]),
            ("tuple_key", (1, 2), (3, 4)),
            ("dict_key", {"a": 1}, {"b": 2}),
            ("set_key", {1, 2}, {3, 4}),
        ]

        for key, old_val, new_val in test_cases:
            event = ContextChangeEvent(key, old_val, new_val, 100)
            assert event.key == key
            assert event.old_value == old_val
            assert event.new_value == new_val
            assert event.context_id == 100

    def test_repr_basic(self) -> None:
        """Test basic string representation of ContextChangeEvent."""
        event = ContextChangeEvent("test_key", "old_val", "new_val", 123)
        repr_str = repr(event)

        assert "ContextChangeEvent" in repr_str
        assert "key='test_key'" in repr_str
        assert "old_val -> new_val" in repr_str
        assert f"t={event.timestamp}" in repr_str

    def test_repr_with_none_values(self) -> None:
        """Test string representation with None values."""
        event = ContextChangeEvent("key", None, None, 0)
        repr_str = repr(event)

        assert "ContextChangeEvent" in repr_str
        assert "key='key'" in repr_str
        assert "None -> None" in repr_str

    def test_repr_with_complex_values(self) -> None:
        """Test string representation with complex data types."""
        old_value = {"nested": {"data": [1, 2, 3]}}
        new_value = [{"item": 1}, {"item": 2}]
        event = ContextChangeEvent("complex", old_value, new_value, 456)
        repr_str = repr(event)

        assert "ContextChangeEvent" in repr_str
        assert "key='complex'" in repr_str
        assert str(old_value) in repr_str
        assert str(new_value) in repr_str

    def test_repr_with_string_containing_quotes(self) -> None:
        """Test string representation with values containing quotes."""
        event = ContextChangeEvent("key", "old'value", 'new"value', 789)
        repr_str = repr(event)

        assert "ContextChangeEvent" in repr_str
        assert "key='key'" in repr_str
        assert "old'value" in repr_str
        assert 'new"value' in repr_str

    def test_repr_format_consistency(self) -> None:
        """Test that repr format is consistent and parseable."""
        event = ContextChangeEvent("test", 42, 43, 100)
        repr_str = repr(event)

        # Check the expected format
        expected_pattern = r"ContextChangeEvent\(key='test', 42 -> 43, t=\d+\.\d+\)"
        import re

        assert re.match(expected_pattern, repr_str)

    def test_repr_with_empty_string_key(self) -> None:
        """Test string representation with empty string key."""
        event = ContextChangeEvent("", "old", "new", 1)
        repr_str = repr(event)

        assert "key=''" in repr_str
        assert "old -> new" in repr_str

    def test_repr_with_numeric_values(self) -> None:
        """Test string representation with various numeric types."""
        test_cases = [
            (42, 43, "42 -> 43"),
            (3.14, 2.71, "3.14 -> 2.71"),
            (True, False, "True -> False"),
        ]

        for old_val, new_val, expected_transition in test_cases:
            event = ContextChangeEvent("key", old_val, new_val, 1)
            repr_str = repr(event)
            assert expected_transition in repr_str


class TestHistoryTracker:
    """Test suite for HistoryTracker class."""

    def test_init_default_max_size(self) -> None:
        """Test initialization with default max_size."""
        tracker = HistoryTracker()

        assert tracker._max_history_size == 1000  # type: ignore[reportPrivateUsage]
        assert tracker._change_history == []  # type: ignore[reportPrivateUsage]
        assert len(tracker._change_history) == 0  # type: ignore[reportPrivateUsage]

    def test_init_custom_max_size(self) -> None:
        """Test initialization with custom max_size."""
        max_size = 500
        tracker = HistoryTracker(max_size=max_size)

        assert tracker._max_history_size == max_size  # type: ignore[reportPrivateUsage]
        assert tracker._change_history == []  # type: ignore[reportPrivateUsage]
        assert len(tracker._change_history) == 0  # type: ignore[reportPrivateUsage]

    def test_init_zero_max_size(self) -> None:
        """Test initialization with zero max_size."""
        tracker = HistoryTracker(max_size=0)

        assert tracker._max_history_size == 0  # type: ignore[reportPrivateUsage]
        assert tracker._change_history == []  # type: ignore[reportPrivateUsage]

    def test_init_small_max_size(self) -> None:
        """Test initialization with small max_size."""
        tracker = HistoryTracker(max_size=1)

        assert tracker._max_history_size == 1  # type: ignore[reportPrivateUsage]
        assert tracker._change_history == []  # type: ignore[reportPrivateUsage]

    def test_init_large_max_size(self) -> None:
        """Test initialization with large max_size."""
        tracker = HistoryTracker(max_size=10000)

        assert tracker._max_history_size == 10000  # type: ignore[reportPrivateUsage]
        assert tracker._change_history == []  # type: ignore[reportPrivateUsage]

    def test_init_negative_max_size(self) -> None:
        """Test initialization with negative max_size (should accept it)."""
        tracker = HistoryTracker(max_size=-1)

        assert tracker._max_history_size == -1  # type: ignore[reportPrivateUsage]
        assert tracker._change_history == []  # type: ignore[reportPrivateUsage]

    def test_init_attributes_types(self) -> None:
        """Test that initialized attributes have correct types."""
        tracker = HistoryTracker()

        assert isinstance(tracker._change_history, list)  # type: ignore[reportPrivateUsage]
        assert isinstance(tracker._max_history_size, int)  # type: ignore[reportPrivateUsage]

        # Verify the list can contain ContextChangeEvent objects
        assert all(
            isinstance(item, ContextChangeEvent) for item in tracker._change_history  # type: ignore[reportPrivateUsage]
        )

    def test_init_isolated_instances(self) -> None:
        """Test that different instances have isolated state."""
        tracker1 = HistoryTracker(max_size=100)
        tracker2 = HistoryTracker(max_size=200)

        assert tracker1._max_history_size != tracker2._max_history_size  # type: ignore[reportPrivateUsage]
        assert tracker1._change_history is not tracker2._change_history  # type: ignore[reportPrivateUsage]

        # Verify modifying one doesn't affect the other
        tracker1._max_history_size = 150  # type: ignore[reportPrivateUsage]
        assert tracker2._max_history_size == 200  # type: ignore[reportPrivateUsage]

    def test_record_change_basic(self) -> None:
        """Test basic recording of a change event."""
        tracker = HistoryTracker()

        tracker.record_change("key1", "old_val", "new_val", 123)

        assert len(tracker._change_history) == 1  # type: ignore[reportPrivateUsage]
        event = tracker._change_history[0]  # type: ignore[reportPrivateUsage]
        assert event.key == "key1"
        assert event.old_value == "old_val"
        assert event.new_value == "new_val"
        assert event.context_id == 123

    def test_record_change_multiple_events(self) -> None:
        """Test recording multiple change events."""
        tracker = HistoryTracker()

        tracker.record_change("key1", "old1", "new1", 1)
        tracker.record_change("key2", "old2", "new2", 2)
        tracker.record_change("key3", "old3", "new3", 3)

        assert len(tracker._change_history) == 3  # type: ignore[reportPrivateUsage]

        # Verify events are in chronological order
        events = tracker._change_history  # type: ignore[reportPrivateUsage]
        assert events[0].key == "key1"
        assert events[1].key == "key2"
        assert events[2].key == "key3"

    def test_record_change_with_none_values(self) -> None:
        """Test recording change events with None values."""
        tracker = HistoryTracker()

        tracker.record_change("key", None, "new", 1)
        tracker.record_change("key", "old", None, 2)
        tracker.record_change("key", None, None, 3)

        assert len(tracker._change_history) == 3  # type: ignore[reportPrivateUsage]
        events = tracker._change_history  # type: ignore[reportPrivateUsage]
        assert events[0].old_value is None
        assert events[1].new_value is None
        assert events[2].old_value is None and events[2].new_value is None

    def test_record_change_with_complex_values(self) -> None:
        """Test recording change events with complex data types."""
        tracker = HistoryTracker()

        old_dict = {"nested": {"data": [1, 2, 3]}}
        new_list = [{"item": 1}, {"item": 2}]

        tracker.record_change("complex_key", old_dict, new_list, 456)

        assert len(tracker._change_history) == 1  # type: ignore[reportPrivateUsage]
        event = tracker._change_history[0]  # type: ignore[reportPrivateUsage]
        assert event.old_value == old_dict
        assert event.new_value == new_list

    def test_record_change_history_size_limit(self) -> None:
        """Test that history size is limited according to max_size."""
        tracker = HistoryTracker(max_size=3)

        # Add 5 events (more than max_size)
        for i in range(5):
            tracker.record_change(f"key{i}", f"old{i}", f"new{i}", i)

        # Should only keep the most recent 3
        assert len(tracker._change_history) == 3  # type: ignore[reportPrivateUsage]
        events = tracker._change_history  # type: ignore[reportPrivateUsage]

        # Should have kept events 2, 3, 4 (most recent)
        assert events[0].key == "key2"
        assert events[1].key == "key3"
        assert events[2].key == "key4"

    def test_record_change_zero_max_size(self) -> None:
        """Test recording changes with zero max_size."""
        tracker = HistoryTracker(max_size=0)

        tracker.record_change("key", "old", "new", 1)

        # Should keep no history
        assert len(tracker._change_history) == 0  # type: ignore[reportPrivateUsage]

    def test_record_change_max_size_one(self) -> None:
        """Test recording changes with max_size of 1."""
        tracker = HistoryTracker(max_size=1)

        tracker.record_change("key1", "old1", "new1", 1)
        tracker.record_change("key2", "old2", "new2", 2)

        # Should only keep the most recent event
        assert len(tracker._change_history) == 1  # type: ignore[reportPrivateUsage]
        event = tracker._change_history[0]  # type: ignore[reportPrivateUsage]
        assert event.key == "key2"

    def test_record_change_timestamps_increase(self) -> None:
        """Test that timestamps increase for sequential events."""
        tracker = HistoryTracker()

        tracker.record_change("key1", "old1", "new1", 1)
        time.sleep(0.001)  # Small delay to ensure different timestamps
        tracker.record_change("key2", "old2", "new2", 2)

        events = tracker._change_history  # type: ignore[reportPrivateUsage]
        assert events[0].timestamp < events[1].timestamp

    def test_record_change_same_key_multiple_times(self) -> None:
        """Test recording multiple changes to the same key."""
        tracker = HistoryTracker()

        tracker.record_change("same_key", "val1", "val2", 1)
        tracker.record_change("same_key", "val2", "val3", 1)
        tracker.record_change("same_key", "val3", "val4", 1)

        assert len(tracker._change_history) == 3  # type: ignore[reportPrivateUsage]
        events = tracker._change_history  # type: ignore[reportPrivateUsage]

        # All should be for the same key but with different values
        assert all(event.key == "same_key" for event in events)
        assert events[0].new_value == "val2"
        assert events[1].new_value == "val3"
        assert events[2].new_value == "val4"

    def test_get_history_basic(self) -> None:
        """Test basic get_history functionality."""
        tracker = HistoryTracker()

        tracker.record_change("key1", "old1", "new1", 1)
        tracker.record_change("key2", "old2", "new2", 2)
        tracker.record_change("key3", "old3", "new3", 3)

        history = tracker.get_history()

        # Should return all events in reverse order (most recent first)
        assert len(history) == 3
        assert history[0].key == "key3"  # Most recent
        assert history[1].key == "key2"
        assert history[2].key == "key1"  # Oldest

    def test_get_history_empty(self) -> None:
        """Test get_history with empty history."""
        tracker = HistoryTracker()

        history = tracker.get_history()

        assert history == []

    def test_get_history_with_limit(self) -> None:
        """Test get_history with limit parameter."""
        tracker = HistoryTracker()

        for i in range(5):
            tracker.record_change(f"key{i}", f"old{i}", f"new{i}", i)

        # Get only the 2 most recent events
        history = tracker.get_history(limit=2)

        assert len(history) == 2
        assert history[0].key == "key4"  # Most recent
        assert history[1].key == "key3"

    def test_get_history_with_since_timestamp(self) -> None:
        """Test get_history with since parameter."""
        tracker = HistoryTracker()

        # Record first event
        tracker.record_change("key1", "old1", "new1", 1)
        first_timestamp = tracker._change_history[0].timestamp  # type: ignore[reportPrivateUsage]

        time.sleep(0.01)  # Ensure different timestamps

        # Record more events
        tracker.record_change("key2", "old2", "new2", 2)
        tracker.record_change("key3", "old3", "new3", 3)

        # Get events since first timestamp
        history = tracker.get_history(since=first_timestamp)

        # Should only get the 2 newer events
        assert len(history) == 2
        assert history[0].key == "key3"  # Most recent
        assert history[1].key == "key2"

    def test_get_history_with_limit_and_since(self) -> None:
        """Test get_history with both limit and since parameters."""
        tracker = HistoryTracker()

        # Record several events with delays
        for i in range(1, 6):
            tracker.record_change(f"key{i}", f"old{i}", f"new{i}", i)
            time.sleep(0.001)

        # Get timestamp after key2
        since_timestamp = tracker._change_history[1].timestamp  # type: ignore[reportPrivateUsage]

        # Get max 2 events since key2's timestamp
        history = tracker.get_history(limit=2, since=since_timestamp)

        # Should get key5 and key4 (most recent 2 after key2)
        assert len(history) == 2
        assert history[0].key == "key5"
        assert history[1].key == "key4"

    def test_get_history_zero_limit(self) -> None:
        """Test get_history with zero limit."""
        tracker = HistoryTracker()

        tracker.record_change("key1", "old1", "new1", 1)
        tracker.record_change("key2", "old2", "new2", 2)

        history = tracker.get_history(limit=0)

        # Should return empty list
        assert history == []

    def test_get_history_large_limit(self) -> None:
        """Test get_history with limit larger than history size."""
        tracker = HistoryTracker()

        tracker.record_change("key1", "old1", "new1", 1)
        tracker.record_change("key2", "old2", "new2", 2)

        # Request more events than available
        history = tracker.get_history(limit=10)

        # Should return all available events
        assert len(history) == 2
        assert history[0].key == "key2"
        assert history[1].key == "key1"

    def test_get_history_since_future_timestamp(self) -> None:
        """Test get_history with since timestamp in the future."""
        tracker = HistoryTracker()

        tracker.record_change("key1", "old1", "new1", 1)
        tracker.record_change("key2", "old2", "new2", 2)

        # Use timestamp in the future
        future_timestamp = time.time() + 100
        history = tracker.get_history(since=future_timestamp)

        # Should return empty list
        assert history == []

    def test_get_history_since_past_timestamp(self) -> None:
        """Test get_history with since timestamp before all events."""
        tracker = HistoryTracker()

        tracker.record_change("key1", "old1", "new1", 1)
        tracker.record_change("key2", "old2", "new2", 2)

        # Use timestamp before all events
        past_timestamp = time.time() - 100
        history = tracker.get_history(since=past_timestamp)

        # Should return all events
        assert len(history) == 2
        assert history[0].key == "key2"
        assert history[1].key == "key1"

    def test_get_history_preserves_original(self) -> None:
        """Test that get_history doesn't modify the original history."""
        tracker = HistoryTracker()

        tracker.record_change("key1", "old1", "new1", 1)
        tracker.record_change("key2", "old2", "new2", 2)

        # Get history and modify the returned list
        history = tracker.get_history()
        original_length = len(tracker._change_history)  # type: ignore[reportPrivateUsage]

        history.clear()  # Modify the returned list

        # Original history should be unchanged
        assert len(tracker._change_history) == original_length  # type: ignore[reportPrivateUsage]

        # Getting history again should return the same data
        new_history = tracker.get_history()
        assert len(new_history) == 2

    def test_clear_history_basic(self) -> None:
        """Test basic clear_history functionality."""
        tracker = HistoryTracker()

        # Add some events
        tracker.record_change("key1", "old1", "new1", 1)
        tracker.record_change("key2", "old2", "new2", 2)
        tracker.record_change("key3", "old3", "new3", 3)

        # Verify events exist
        assert len(tracker._change_history) == 3  # type: ignore[reportPrivateUsage]

        # Clear history
        tracker.clear_history()

        # Verify history is empty
        assert len(tracker._change_history) == 0  # type: ignore[reportPrivateUsage]
        assert tracker.get_history() == []

    def test_clear_history_empty(self) -> None:
        """Test clearing already empty history."""
        tracker = HistoryTracker()

        # Verify history is initially empty
        assert len(tracker._change_history) == 0  # type: ignore[reportPrivateUsage]

        # Clear empty history (should not raise error)
        tracker.clear_history()

        # Verify history is still empty
        assert len(tracker._change_history) == 0  # type: ignore[reportPrivateUsage]
        assert tracker.get_history() == []

    def test_clear_history_then_add_new(self) -> None:
        """Test adding events after clearing history."""
        tracker = HistoryTracker()

        # Add initial events
        tracker.record_change("key1", "old1", "new1", 1)
        tracker.record_change("key2", "old2", "new2", 2)

        # Clear history
        tracker.clear_history()

        # Add new events
        tracker.record_change("key3", "old3", "new3", 3)
        tracker.record_change("key4", "old4", "new4", 4)

        # Verify only new events exist
        assert len(tracker._change_history) == 2  # type: ignore[reportPrivateUsage]
        history = tracker.get_history()
        assert len(history) == 2
        assert history[0].key == "key4"  # Most recent
        assert history[1].key == "key3"

    def test_clear_history_multiple_times(self) -> None:
        """Test clearing history multiple times."""
        tracker = HistoryTracker()

        # Add events and clear
        tracker.record_change("key1", "old1", "new1", 1)
        tracker.clear_history()
        assert len(tracker._change_history) == 0  # type: ignore[reportPrivateUsage]

        # Add more events and clear again
        tracker.record_change("key2", "old2", "new2", 2)
        tracker.record_change("key3", "old3", "new3", 3)
        tracker.clear_history()
        assert len(tracker._change_history) == 0  # type: ignore[reportPrivateUsage]

        # Clear again (empty history)
        tracker.clear_history()
        assert len(tracker._change_history) == 0  # type: ignore[reportPrivateUsage]

    def test_clear_history_preserves_max_size(self) -> None:
        """Test that clear_history preserves the max_size setting."""
        max_size = 5
        tracker = HistoryTracker(max_size=max_size)

        # Add events
        for i in range(3):
            tracker.record_change(f"key{i}", f"old{i}", f"new{i}", i)

        # Clear history
        tracker.clear_history()

        # Verify max_size is preserved
        assert tracker._max_history_size == max_size  # type: ignore[reportPrivateUsage]

        # Add new events to verify max_size still works
        for i in range(7):  # More than max_size
            tracker.record_change(f"new_key{i}", f"old{i}", f"new{i}", i)

        # Should only keep the last max_size events
        assert len(tracker._change_history) == max_size  # type: ignore[reportPrivateUsage]

    def test_clear_history_with_zero_max_size(self) -> None:
        """Test clear_history with zero max_size tracker."""
        tracker = HistoryTracker(max_size=0)

        # Try to add an event (should not be kept due to max_size=0)
        tracker.record_change("key1", "old1", "new1", 1)
        assert len(tracker._change_history) == 0  # type: ignore[reportPrivateUsage]

        # Clear history (should work even though already empty)
        tracker.clear_history()
        assert len(tracker._change_history) == 0  # type: ignore[reportPrivateUsage]
