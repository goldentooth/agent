"""Tests for HistoryTracker.get_history method."""

import time

import pytest

from context.history_tracker import HistoryTracker


class TestHistoryTrackerGetHistory:
    """Test suite for HistoryTracker.get_history method."""

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
