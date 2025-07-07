"""Tests for HistoryTracker.set_max_history_size method."""

import pytest

from context.history_tracker import HistoryTracker


class TestHistoryTrackerSetMaxSize:
    """Test suite for HistoryTracker.set_max_history_size method."""

    def test_set_max_history_size_basic(self) -> None:
        """Test basic set_max_history_size functionality."""
        tracker = HistoryTracker(max_size=10)

        # Change to smaller size
        tracker.set_max_history_size(5)

        assert tracker._max_history_size == 5  # type: ignore[reportPrivateUsage]

    def test_set_max_history_size_trims_existing_history(self) -> None:
        """Test set_max_history_size trims existing history when reduced."""
        tracker = HistoryTracker()

        # Add 10 events
        for i in range(10):
            tracker.record_change(f"key{i}", f"old{i}", f"new{i}", i)

        assert tracker.get_history_size() == 10

        # Reduce max size to 3
        tracker.set_max_history_size(3)

        assert tracker.get_history_size() == 3
        # Should keep the most recent 3 events (key7, key8, key9)
        history = tracker.get_history()
        assert history[0].key == "key9"  # Most recent
        assert history[1].key == "key8"
        assert history[2].key == "key7"  # Oldest kept

    def test_set_max_history_size_zero(self) -> None:
        """Test set_max_history_size with zero clears all history."""
        tracker = HistoryTracker()

        # Add events
        for i in range(5):
            tracker.record_change(f"key{i}", f"old{i}", f"new{i}", i)

        assert tracker.get_history_size() == 5

        # Set max size to 0
        tracker.set_max_history_size(0)

        assert tracker.get_history_size() == 0
        assert tracker._max_history_size == 0  # type: ignore[reportPrivateUsage]

    def test_set_max_history_size_larger_than_current(self) -> None:
        """Test set_max_history_size larger than current history preserves all."""
        tracker = HistoryTracker()

        # Add 3 events
        for i in range(3):
            tracker.record_change(f"key{i}", f"old{i}", f"new{i}", i)

        assert tracker.get_history_size() == 3

        # Set max size to 10
        tracker.set_max_history_size(10)

        # Should preserve all existing events
        assert tracker.get_history_size() == 3
        assert tracker._max_history_size == 10  # type: ignore[reportPrivateUsage]

        # Should still accept new events up to the new limit
        for i in range(3, 7):
            tracker.record_change(f"key{i}", f"old{i}", f"new{i}", i)

        assert tracker.get_history_size() == 7

    def test_set_max_history_size_negative_raises_error(self) -> None:
        """Test set_max_history_size raises ValueError for negative values."""
        tracker = HistoryTracker()

        with pytest.raises(ValueError, match="History size must be non-negative"):
            tracker.set_max_history_size(-1)

        with pytest.raises(ValueError, match="History size must be non-negative"):
            tracker.set_max_history_size(-10)

    def test_set_max_history_size_affects_future_records(self) -> None:
        """Test set_max_history_size affects future record_change calls."""
        tracker = HistoryTracker()

        # Set small max size
        tracker.set_max_history_size(2)

        # Add more events than max size
        for i in range(5):
            tracker.record_change(f"key{i}", f"old{i}", f"new{i}", i)

        # Should only keep the 2 most recent
        assert tracker.get_history_size() == 2
        history = tracker.get_history()
        assert history[0].key == "key4"
        assert history[1].key == "key3"

    def test_set_max_history_size_multiple_calls(self) -> None:
        """Test multiple calls to set_max_history_size."""
        tracker = HistoryTracker()

        # Add events
        for i in range(10):
            tracker.record_change(f"key{i}", f"old{i}", f"new{i}", i)

        # First reduction to 5
        tracker.set_max_history_size(5)
        assert tracker.get_history_size() == 5

        # Second reduction to 2
        tracker.set_max_history_size(2)
        assert tracker.get_history_size() == 2

        # Increase back to 7
        tracker.set_max_history_size(7)
        assert tracker.get_history_size() == 2  # Still only 2 events

        # Add more events
        for i in range(10, 15):
            tracker.record_change(f"key{i}", f"old{i}", f"new{i}", i)

        assert tracker.get_history_size() == 7  # Now up to new limit

    def test_set_max_history_size_with_empty_history(self) -> None:
        """Test set_max_history_size with empty history."""
        tracker = HistoryTracker()

        assert tracker.get_history_size() == 0

        # Set max size on empty tracker
        tracker.set_max_history_size(5)

        assert tracker.get_history_size() == 0
        assert tracker._max_history_size == 5  # type: ignore[reportPrivateUsage]

    def test_set_max_history_size_preserves_event_order(self) -> None:
        """Test set_max_history_size preserves chronological order of kept events."""
        tracker = HistoryTracker()

        # Add events with delays to ensure different timestamps
        for i in range(5):
            tracker.record_change(f"key{i}", f"old{i}", f"new{i}", i)

        # Reduce to 3 events
        tracker.set_max_history_size(3)

        # Get history (most recent first)
        history = tracker.get_history()
        assert len(history) == 3

        # Verify chronological order is preserved (most recent first)
        assert history[0].key == "key4"  # Most recent
        assert history[1].key == "key3"
        assert history[2].key == "key2"  # Oldest kept

        # Verify timestamps are in descending order
        assert history[0].timestamp > history[1].timestamp
        assert history[1].timestamp > history[2].timestamp

    def test_set_max_history_size_zero_then_nonzero(self) -> None:
        """Test setting max size to zero then back to non-zero."""
        tracker = HistoryTracker()

        # Add events
        for i in range(3):
            tracker.record_change(f"key{i}", f"old{i}", f"new{i}", i)

        assert tracker.get_history_size() == 3

        # Set to zero (clears history)
        tracker.set_max_history_size(0)
        assert tracker.get_history_size() == 0

        # Set back to non-zero
        tracker.set_max_history_size(5)
        assert tracker.get_history_size() == 0  # History is still empty

        # Add new events
        for i in range(3, 6):
            tracker.record_change(f"key{i}", f"old{i}", f"new{i}", i)

        assert tracker.get_history_size() == 3

    def test_set_max_history_size_same_value(self) -> None:
        """Test setting max size to the same value."""
        tracker = HistoryTracker(max_size=5)

        # Add events
        for i in range(3):
            tracker.record_change(f"key{i}", f"old{i}", f"new{i}", i)

        # Set to same value
        tracker.set_max_history_size(5)

        # Should not affect existing history
        assert tracker.get_history_size() == 3
        assert tracker._max_history_size == 5  # type: ignore[reportPrivateUsage]
