"""Tests for basic HistoryTracker functionality."""

import time
from unittest.mock import patch

import pytest

from context.history_tracker import HistoryTracker


class TestHistoryTrackerBasic:
    """Test suite for basic HistoryTracker functionality."""

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
            isinstance(item, type) for item in tracker._change_history  # type: ignore[reportPrivateUsage]
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
