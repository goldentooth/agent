"""Tests for HistoryTracker.replay_changes_since method."""

import time

import pytest

from context.history_tracker import HistoryTracker


class TestHistoryTrackerReplay:
    """Test suite for HistoryTracker.replay_changes_since method."""

    def test_replay_changes_since_basic(self) -> None:
        """Test basic replay_changes_since functionality."""
        tracker = HistoryTracker()

        # Record changes with delays to ensure different timestamps
        tracker.record_change("key1", "old1", "new1", 1)
        time.sleep(0.001)

        timestamp = time.time()
        time.sleep(0.001)

        tracker.record_change("key2", "old2", "new2", 2)
        tracker.record_change("key3", "old3", "new3", 3)

        # Replay changes since timestamp (should get key2 and key3 in chronological order)
        changes = tracker.replay_changes_since(timestamp)

        assert len(changes) == 2
        assert changes[0].key == "key2"  # First after timestamp
        assert changes[1].key == "key3"  # Second after timestamp

    def test_replay_changes_since_no_changes_after_timestamp(self) -> None:
        """Test replay_changes_since when no changes occurred after timestamp."""
        tracker = HistoryTracker()

        # Record all changes
        tracker.record_change("key1", "old1", "new1", 1)
        tracker.record_change("key2", "old2", "new2", 2)
        tracker.record_change("key3", "old3", "new3", 3)

        # Use timestamp after all changes
        future_timestamp = time.time() + 100

        changes = tracker.replay_changes_since(future_timestamp)

        assert changes == []

    def test_replay_changes_since_all_changes_after_timestamp(self) -> None:
        """Test replay_changes_since when all changes occurred after timestamp."""
        tracker = HistoryTracker()

        # Use timestamp before any changes
        past_timestamp = time.time() - 100

        # Record changes
        tracker.record_change("key1", "old1", "new1", 1)
        tracker.record_change("key2", "old2", "new2", 2)
        tracker.record_change("key3", "old3", "new3", 3)

        changes = tracker.replay_changes_since(past_timestamp)

        assert len(changes) == 3
        assert changes[0].key == "key1"
        assert changes[1].key == "key2"
        assert changes[2].key == "key3"

    def test_replay_changes_since_empty_history(self) -> None:
        """Test replay_changes_since with empty history."""
        tracker = HistoryTracker()

        changes = tracker.replay_changes_since(time.time())

        assert changes == []

    def test_replay_changes_since_chronological_order(self) -> None:
        """Test that replay_changes_since returns events in chronological order."""
        tracker = HistoryTracker()

        # Setup: Add event before timestamp
        tracker.record_change("key1", "old1", "new1", 1)
        time.sleep(0.001)
        timestamp = time.time()
        time.sleep(0.001)

        # Add multiple events after timestamp
        for i in range(2, 5):
            tracker.record_change(f"key{i}", f"old{i}", f"new{i}", i)
            time.sleep(0.001)

        # Get and verify changes
        changes = tracker.replay_changes_since(timestamp)
        assert len(changes) == 3

        # Verify order and timestamps
        for i in range(3):
            assert changes[i].key == f"key{i+2}"
            if i > 0:
                assert changes[i - 1].timestamp < changes[i].timestamp

    def test_replay_changes_since_exact_timestamp_match(self) -> None:
        """Test replay_changes_since with exact timestamp match (should not include)."""
        tracker = HistoryTracker()

        # Record a change and capture its exact timestamp
        tracker.record_change("key1", "old1", "new1", 1)
        event1_timestamp = tracker._change_history[0].timestamp  # type: ignore[reportPrivateUsage]

        time.sleep(0.001)
        tracker.record_change("key2", "old2", "new2", 2)

        # Use exact timestamp of first event
        changes = tracker.replay_changes_since(event1_timestamp)

        # Should only get key2 (events AFTER the timestamp)
        assert len(changes) == 1
        assert changes[0].key == "key2"

    def test_replay_changes_since_returns_independent_list(self) -> None:
        """Test that replay_changes_since returns a new list, not a reference."""
        tracker = HistoryTracker()

        tracker.record_change("key1", "old1", "new1", 1)
        time.sleep(0.001)

        timestamp = time.time()
        time.sleep(0.001)

        tracker.record_change("key2", "old2", "new2", 2)

        # Get changes
        changes1 = tracker.replay_changes_since(timestamp)
        changes2 = tracker.replay_changes_since(timestamp)

        # Should be different list instances
        assert changes1 is not changes2

        # But with same content
        assert len(changes1) == len(changes2)
        assert all(c1.key == c2.key for c1, c2 in zip(changes1, changes2))

    def test_replay_changes_since_with_max_size_limitation(self) -> None:
        """Test replay_changes_since when history is limited by max_size."""
        tracker = HistoryTracker(max_size=3)

        # Record 5 changes (only last 3 will be kept)
        for i in range(5):
            tracker.record_change(f"key{i}", f"old{i}", f"new{i}", i)
            time.sleep(0.001)

        # Use timestamp from before all changes
        past_timestamp = time.time() - 100

        changes = tracker.replay_changes_since(past_timestamp)

        # Should only get the 3 kept events (key2, key3, key4)
        assert len(changes) == 3
        assert changes[0].key == "key2"
        assert changes[1].key == "key3"
        assert changes[2].key == "key4"

    def test_replay_changes_since_with_zero_timestamp(self) -> None:
        """Test replay_changes_since with zero timestamp (should return all)."""
        tracker = HistoryTracker()

        tracker.record_change("key1", "old1", "new1", 1)
        tracker.record_change("key2", "old2", "new2", 2)
        tracker.record_change("key3", "old3", "new3", 3)

        # Zero timestamp means all events are after it
        changes = tracker.replay_changes_since(0.0)

        assert len(changes) == 3
        assert changes[0].key == "key1"
        assert changes[1].key == "key2"
        assert changes[2].key == "key3"

    def test_replay_changes_since_with_negative_timestamp(self) -> None:
        """Test replay_changes_since with negative timestamp."""
        tracker = HistoryTracker()

        tracker.record_change("key1", "old1", "new1", 1)
        tracker.record_change("key2", "old2", "new2", 2)

        # Negative timestamp should work (all events are after it)
        changes = tracker.replay_changes_since(-100.0)

        assert len(changes) == 2
        assert changes[0].key == "key1"
        assert changes[1].key == "key2"

    def test_replay_changes_since_preserves_event_data(self) -> None:
        """Test that replay_changes_since preserves all event data."""
        tracker = HistoryTracker()

        # Complex data in events
        old_data = {"nested": {"value": 123}}
        new_data = [1, 2, 3]

        tracker.record_change("complex_key", old_data, new_data, 999)

        timestamp = time.time() - 100  # Before the event

        changes = tracker.replay_changes_since(timestamp)

        assert len(changes) == 1
        event = changes[0]
        assert event.key == "complex_key"
        assert event.old_value == old_data
        assert event.new_value == new_data
        assert event.context_id == 999
        assert isinstance(event.timestamp, float)
