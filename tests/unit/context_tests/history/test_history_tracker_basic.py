"""Tests for basic HistoryTracker functionality."""

import time

from context.history_tracker import HistoryTracker


class TestHistoryTrackerBasic:
    """Test suite for basic HistoryTracker functionality."""

    def test_init_default_max_size(self) -> None:
        """Test initialization with default max_size."""
        tracker = HistoryTracker()

        assert tracker._max_history_size == 1000
        assert tracker._change_history == []
        assert len(tracker._change_history) == 0

    def test_init_custom_max_size(self) -> None:
        """Test initialization with custom max_size."""
        max_size = 500
        tracker = HistoryTracker(max_size=max_size)

        assert tracker._max_history_size == max_size
        assert tracker._change_history == []
        assert len(tracker._change_history) == 0

    def test_init_zero_max_size(self) -> None:
        """Test initialization with zero max_size."""
        tracker = HistoryTracker(max_size=0)

        assert tracker._max_history_size == 0
        assert tracker._change_history == []

    def test_init_small_max_size(self) -> None:
        """Test initialization with small max_size."""
        tracker = HistoryTracker(max_size=1)

        assert tracker._max_history_size == 1
        assert tracker._change_history == []

    def test_init_large_max_size(self) -> None:
        """Test initialization with large max_size."""
        tracker = HistoryTracker(max_size=10000)

        assert tracker._max_history_size == 10000
        assert tracker._change_history == []

    def test_init_negative_max_size(self) -> None:
        """Test initialization with negative max_size (should accept it)."""
        tracker = HistoryTracker(max_size=-1)

        assert tracker._max_history_size == -1
        assert tracker._change_history == []

    def test_init_attributes_types(self) -> None:
        """Test that initialized attributes have correct types."""
        tracker = HistoryTracker()

        assert isinstance(tracker._change_history, list)
        assert isinstance(tracker._max_history_size, int)

        # Verify the list can contain ContextChangeEvent objects
        assert all(isinstance(item, type) for item in tracker._change_history)

    def test_init_isolated_instances(self) -> None:
        """Test that different instances have isolated state."""
        tracker1 = HistoryTracker(max_size=100)
        tracker2 = HistoryTracker(max_size=200)

        assert tracker1._max_history_size != tracker2._max_history_size
        assert tracker1._change_history is not tracker2._change_history

        # Verify modifying one doesn't affect the other
        tracker1._max_history_size = 150
        assert tracker2._max_history_size == 200

    def test_record_change_basic(self) -> None:
        """Test basic recording of a change event."""
        tracker = HistoryTracker()

        tracker.record_change("key1", "old_val", "new_val", 123)

        assert len(tracker._change_history) == 1
        event = tracker._change_history[0]
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

        assert len(tracker._change_history) == 3

        # Verify events are in chronological order
        events = tracker._change_history
        assert events[0].key == "key1"
        assert events[1].key == "key2"
        assert events[2].key == "key3"

    def test_record_change_with_none_values(self) -> None:
        """Test recording change events with None values."""
        tracker = HistoryTracker()

        tracker.record_change("key", None, "new", 1)
        tracker.record_change("key", "old", None, 2)
        tracker.record_change("key", None, None, 3)

        assert len(tracker._change_history) == 3
        events = tracker._change_history
        assert events[0].old_value is None
        assert events[1].new_value is None
        assert events[2].old_value is None and events[2].new_value is None

    def test_record_change_with_complex_values(self) -> None:
        """Test recording change events with complex data types."""
        tracker = HistoryTracker()

        old_dict = {"nested": {"data": [1, 2, 3]}}
        new_list = [{"item": 1}, {"item": 2}]

        tracker.record_change("complex_key", old_dict, new_list, 456)

        assert len(tracker._change_history) == 1
        event = tracker._change_history[0]
        assert event.old_value == old_dict
        assert event.new_value == new_list

    def test_record_change_history_size_limit(self) -> None:
        """Test that history size is limited according to max_size."""
        tracker = HistoryTracker(max_size=3)

        # Add 5 events (more than max_size)
        for i in range(5):
            tracker.record_change(f"key{i}", f"old{i}", f"new{i}", i)

        # Should only keep the most recent 3
        assert len(tracker._change_history) == 3
        events = tracker._change_history

        # Should have kept events 2, 3, 4 (most recent)
        assert events[0].key == "key2"
        assert events[1].key == "key3"
        assert events[2].key == "key4"

    def test_record_change_zero_max_size(self) -> None:
        """Test recording changes with zero max_size."""
        tracker = HistoryTracker(max_size=0)

        tracker.record_change("key", "old", "new", 1)

        # Should keep no history
        assert len(tracker._change_history) == 0

    def test_record_change_max_size_one(self) -> None:
        """Test recording changes with max_size of 1."""
        tracker = HistoryTracker(max_size=1)

        tracker.record_change("key1", "old1", "new1", 1)
        tracker.record_change("key2", "old2", "new2", 2)

        # Should only keep the most recent event
        assert len(tracker._change_history) == 1
        event = tracker._change_history[0]
        assert event.key == "key2"

    def test_record_change_timestamps_increase(self) -> None:
        """Test that timestamps increase for sequential events."""
        tracker = HistoryTracker()

        tracker.record_change("key1", "old1", "new1", 1)
        time.sleep(0.001)  # Small delay to ensure different timestamps
        tracker.record_change("key2", "old2", "new2", 2)

        events = tracker._change_history
        assert events[0].timestamp < events[1].timestamp

    def test_record_change_same_key_multiple_times(self) -> None:
        """Test recording multiple changes to the same key."""
        tracker = HistoryTracker()

        tracker.record_change("same_key", "val1", "val2", 1)
        tracker.record_change("same_key", "val2", "val3", 1)
        tracker.record_change("same_key", "val3", "val4", 1)

        assert len(tracker._change_history) == 3
        events = tracker._change_history

        # All should be for the same key but with different values
        assert all(event.key == "same_key" for event in events)
        assert events[0].new_value == "val2"
        assert events[1].new_value == "val3"
        assert events[2].new_value == "val4"


class TestHistoryTrackerGetAllHistory:
    """Test suite for HistoryTracker.get_all_history method."""

    def test_get_all_history_empty(self) -> None:
        """Test get_all_history with empty history."""
        tracker = HistoryTracker()

        all_history = tracker.get_all_history()

        assert all_history == []
        assert isinstance(all_history, list)

    def test_get_all_history_single_event(self) -> None:
        """Test get_all_history with a single event."""
        tracker = HistoryTracker()

        tracker.record_change("key1", "old1", "new1", 1)

        all_history = tracker.get_all_history()

        assert len(all_history) == 1
        assert all_history[0].key == "key1"
        assert all_history[0].old_value == "old1"
        assert all_history[0].new_value == "new1"
        assert all_history[0].context_id == 1

    def test_get_all_history_multiple_events(self) -> None:
        """Test get_all_history with multiple events."""
        tracker = HistoryTracker()

        tracker.record_change("key1", "old1", "new1", 1)
        tracker.record_change("key2", "old2", "new2", 2)
        tracker.record_change("key3", "old3", "new3", 3)

        all_history = tracker.get_all_history()

        assert len(all_history) == 3
        assert all_history[0].key == "key1"  # First event in chronological order
        assert all_history[1].key == "key2"
        assert all_history[2].key == "key3"  # Last event in chronological order

    def test_get_all_history_chronological_order(self) -> None:
        """Test that get_all_history returns events in chronological order."""
        tracker = HistoryTracker()

        # Add events with small delays to ensure different timestamps
        tracker.record_change("key1", "old1", "new1", 1)
        time.sleep(0.001)
        tracker.record_change("key2", "old2", "new2", 2)
        time.sleep(0.001)
        tracker.record_change("key3", "old3", "new3", 3)

        all_history = tracker.get_all_history()

        # Verify timestamps are in ascending order (chronological)
        assert len(all_history) == 3
        assert all_history[0].timestamp < all_history[1].timestamp
        assert all_history[1].timestamp < all_history[2].timestamp

    def test_get_all_history_returns_copy(self) -> None:
        """Test that get_all_history returns a copy, not reference."""
        tracker = HistoryTracker()

        tracker.record_change("key1", "old1", "new1", 1)
        tracker.record_change("key2", "old2", "new2", 2)

        # Get history twice
        all_history1 = tracker.get_all_history()
        all_history2 = tracker.get_all_history()

        # Should be different list instances
        assert all_history1 is not all_history2

        # But with same content
        assert len(all_history1) == len(all_history2)
        assert all(e1.key == e2.key for e1, e2 in zip(all_history1, all_history2))

        # Modifying the returned list should not affect internal state
        all_history1.clear()
        assert len(tracker.get_all_history()) == 2  # Internal state unchanged

    def test_get_all_history_with_max_size_limitation(self) -> None:
        """Test get_all_history when history is limited by max_size."""
        tracker = HistoryTracker(max_size=3)

        # Record 5 changes (only last 3 will be kept)
        for i in range(5):
            tracker.record_change(f"key{i}", f"old{i}", f"new{i}", i)

        all_history = tracker.get_all_history()

        # Should only get the 3 kept events (key2, key3, key4)
        assert len(all_history) == 3
        assert all_history[0].key == "key2"  # Oldest kept
        assert all_history[1].key == "key3"
        assert all_history[2].key == "key4"  # Most recent

    def test_get_all_history_zero_max_size(self) -> None:
        """Test get_all_history with zero max_size."""
        tracker = HistoryTracker(max_size=0)

        tracker.record_change("key1", "old1", "new1", 1)

        # Should return empty list since no history is kept
        all_history = tracker.get_all_history()
        assert all_history == []

    def test_get_all_history_preserves_event_data(self) -> None:
        """Test that get_all_history preserves all event data."""
        tracker = HistoryTracker()

        # Complex data in events
        old_data = {"nested": {"value": 123}}
        new_data = [1, 2, 3]

        tracker.record_change("complex_key", old_data, new_data, 999)

        all_history = tracker.get_all_history()

        assert len(all_history) == 1
        event = all_history[0]
        assert event.key == "complex_key"
        assert event.old_value == old_data
        assert event.new_value == new_data
        assert event.context_id == 999
        assert isinstance(event.timestamp, float)

    def test_get_all_history_vs_get_history_order(self) -> None:
        """Test that get_all_history and get_history return opposite orders."""
        tracker = HistoryTracker()

        tracker.record_change("key1", "old1", "new1", 1)
        tracker.record_change("key2", "old2", "new2", 2)
        tracker.record_change("key3", "old3", "new3", 3)

        all_history = tracker.get_all_history()  # Chronological order
        recent_history = tracker.get_history()  # Most recent first

        # Same events but opposite order
        assert len(all_history) == len(recent_history)
        assert len(all_history) == 3

        # Verify opposite ordering
        assert all_history[0].key == recent_history[2].key  # key1
        assert all_history[1].key == recent_history[1].key  # key2
        assert all_history[2].key == recent_history[0].key  # key3

    def test_get_all_history_after_clear(self) -> None:
        """Test get_all_history after clearing history."""
        tracker = HistoryTracker()

        tracker.record_change("key1", "old1", "new1", 1)
        tracker.record_change("key2", "old2", "new2", 2)

        # Clear history and verify get_all_history returns empty
        tracker.clear_history()
        all_history = tracker.get_all_history()

        assert all_history == []

    def test_get_all_history_consistency_with_size(self) -> None:
        """Test that get_all_history length matches get_history_size."""
        tracker = HistoryTracker()

        # Add various numbers of events
        for i in range(10):
            tracker.record_change(f"key{i}", f"old{i}", f"new{i}", i)
            all_history = tracker.get_all_history()
            assert len(all_history) == tracker.get_history_size()

    def test_get_all_history_idempotent(self) -> None:
        """Test that get_all_history is idempotent (no side effects)."""
        tracker = HistoryTracker()

        tracker.record_change("key1", "old1", "new1", 1)

        # Multiple calls should return identical results
        history1 = tracker.get_all_history()
        history2 = tracker.get_all_history()
        history3 = tracker.get_all_history()

        assert len(history1) == len(history2) == len(history3) == 1
        assert history1[0].key == history2[0].key == history3[0].key == "key1"

        # Internal state should remain unchanged
        assert tracker.get_history_size() == 1
