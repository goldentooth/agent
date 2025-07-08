"""Tests for HistoryTracker.clear_history and get_history_size methods."""

import pytest

from context.history_tracker import HistoryTracker


class TestHistoryTrackerClearAndSize:
    """Test suite for HistoryTracker clear_history and get_history_size methods."""

    # clear_history tests
    def test_clear_history_basic(self) -> None:
        """Test basic clear_history functionality."""
        tracker = HistoryTracker()

        # Add some events
        tracker.record_change("key1", "old1", "new1", 1)
        tracker.record_change("key2", "old2", "new2", 2)
        tracker.record_change("key3", "old3", "new3", 3)

        # Verify events exist
        assert len(tracker._change_history) == 3

        # Clear history
        tracker.clear_history()

        # Verify history is empty
        assert len(tracker._change_history) == 0
        assert tracker.get_history() == []

    def test_clear_history_empty(self) -> None:
        """Test clearing already empty history."""
        tracker = HistoryTracker()

        # Verify history is initially empty
        assert len(tracker._change_history) == 0

        # Clear empty history (should not raise error)
        tracker.clear_history()

        # Verify history is still empty
        assert len(tracker._change_history) == 0
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
        assert len(tracker._change_history) == 2
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
        assert len(tracker._change_history) == 0

        # Add more events and clear again
        tracker.record_change("key2", "old2", "new2", 2)
        tracker.record_change("key3", "old3", "new3", 3)
        tracker.clear_history()
        assert len(tracker._change_history) == 0

        # Clear again (empty history)
        tracker.clear_history()
        assert len(tracker._change_history) == 0

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
        assert tracker._max_history_size == max_size

        # Add new events to verify max_size still works
        for i in range(7):  # More than max_size
            tracker.record_change(f"new_key{i}", f"old{i}", f"new{i}", i)

        # Should only keep the last max_size events
        assert len(tracker._change_history) == max_size

    def test_clear_history_with_zero_max_size(self) -> None:
        """Test clear_history with zero max_size tracker."""
        tracker = HistoryTracker(max_size=0)

        # Try to add an event (should not be kept due to max_size=0)
        tracker.record_change("key1", "old1", "new1", 1)
        assert len(tracker._change_history) == 0

        # Clear history (should work even though already empty)
        tracker.clear_history()
        assert len(tracker._change_history) == 0

    # get_history_size tests
    def test_get_history_size_empty(self) -> None:
        """Test get_history_size with empty history."""
        tracker = HistoryTracker()

        assert tracker.get_history_size() == 0

    def test_get_history_size_single_event(self) -> None:
        """Test get_history_size with single event."""
        tracker = HistoryTracker()

        tracker.record_change("key1", "old1", "new1", 1)

        assert tracker.get_history_size() == 1

    def test_get_history_size_multiple_events(self) -> None:
        """Test get_history_size with multiple events."""
        tracker = HistoryTracker()

        # Add 5 events
        for i in range(5):
            tracker.record_change(f"key{i}", f"old{i}", f"new{i}", i)

        assert tracker.get_history_size() == 5

    def test_get_history_size_with_max_size_limit(self) -> None:
        """Test get_history_size respects max_size limit."""
        tracker = HistoryTracker(max_size=3)

        # Add 5 events (more than max_size)
        for i in range(5):
            tracker.record_change(f"key{i}", f"old{i}", f"new{i}", i)

        # Should only report the limited size
        assert tracker.get_history_size() == 3

    def test_get_history_size_zero_max_size(self) -> None:
        """Test get_history_size with zero max_size."""
        tracker = HistoryTracker(max_size=0)

        # Try to add events (should not be kept)
        tracker.record_change("key1", "old1", "new1", 1)
        tracker.record_change("key2", "old2", "new2", 2)

        assert tracker.get_history_size() == 0

    def test_get_history_size_after_clear(self) -> None:
        """Test get_history_size after clearing history."""
        tracker = HistoryTracker()

        # Add events
        for i in range(3):
            tracker.record_change(f"key{i}", f"old{i}", f"new{i}", i)

        assert tracker.get_history_size() == 3

        # Clear history
        tracker.clear_history()

        assert tracker.get_history_size() == 0

    def test_get_history_size_incremental(self) -> None:
        """Test get_history_size increases incrementally."""
        tracker = HistoryTracker()

        # Start with empty
        assert tracker.get_history_size() == 0

        # Add events one by one and verify size increases
        for i in range(1, 6):
            tracker.record_change(f"key{i}", f"old{i}", f"new{i}", i)
            assert tracker.get_history_size() == i

    def test_get_history_size_with_max_size_one(self) -> None:
        """Test get_history_size with max_size of 1."""
        tracker = HistoryTracker(max_size=1)

        # Add multiple events
        tracker.record_change("key1", "old1", "new1", 1)
        assert tracker.get_history_size() == 1

        tracker.record_change("key2", "old2", "new2", 2)
        assert tracker.get_history_size() == 1  # Still only 1 due to limit

        tracker.record_change("key3", "old3", "new3", 3)
        assert tracker.get_history_size() == 1  # Still only 1 due to limit

    def test_get_history_size_consistent_with_len(self) -> None:
        """Test get_history_size is consistent with len(_change_history)."""
        tracker = HistoryTracker()

        # Test with various numbers of events
        for num_events in [0, 1, 5, 10]:
            tracker.clear_history()

            for i in range(num_events):
                tracker.record_change(f"key{i}", f"old{i}", f"new{i}", i)

            assert tracker.get_history_size() == len(tracker._change_history)

    def test_get_history_size_return_type(self) -> None:
        """Test get_history_size returns an integer."""
        tracker = HistoryTracker()

        size = tracker.get_history_size()
        assert isinstance(size, int)

        # Add an event and test again
        tracker.record_change("key1", "old1", "new1", 1)
        size = tracker.get_history_size()
        assert isinstance(size, int)
