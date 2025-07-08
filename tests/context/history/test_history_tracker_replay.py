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
        event1_timestamp = tracker._change_history[0].timestamp

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

    def test_get_changes_to_reverse_basic(self) -> None:
        """Test basic get_changes_to_reverse functionality."""
        tracker = HistoryTracker()

        # Record changes with delays to ensure different timestamps
        tracker.record_change("key1", "old1", "new1", 1)
        time.sleep(0.001)

        timestamp = time.time()
        time.sleep(0.001)

        tracker.record_change("key2", "old2", "new2", 2)
        tracker.record_change("key3", "old3", "new3", 3)

        # Get changes to reverse (should get key3, key2 in reverse order)
        changes = tracker.get_changes_to_reverse(timestamp)

        assert len(changes) == 2
        assert changes[0].key == "key3"  # Most recent first for reversal
        assert changes[1].key == "key2"  # Second most recent

    def test_get_changes_to_reverse_no_changes_after_timestamp(self) -> None:
        """Test get_changes_to_reverse when no changes occurred after timestamp."""
        tracker = HistoryTracker()

        # Record all changes
        tracker.record_change("key1", "old1", "new1", 1)
        tracker.record_change("key2", "old2", "new2", 2)
        tracker.record_change("key3", "old3", "new3", 3)

        # Use timestamp after all changes
        future_timestamp = time.time() + 100

        changes = tracker.get_changes_to_reverse(future_timestamp)

        assert changes == []

    def test_get_changes_to_reverse_all_changes_after_timestamp(self) -> None:
        """Test get_changes_to_reverse when all changes occurred after timestamp."""
        tracker = HistoryTracker()

        # Use timestamp before any changes
        past_timestamp = time.time() - 100

        # Record changes
        tracker.record_change("key1", "old1", "new1", 1)
        tracker.record_change("key2", "old2", "new2", 2)
        tracker.record_change("key3", "old3", "new3", 3)

        changes = tracker.get_changes_to_reverse(past_timestamp)

        # Should get all changes in reverse order (most recent first)
        assert len(changes) == 3
        assert changes[0].key == "key3"  # Most recent
        assert changes[1].key == "key2"
        assert changes[2].key == "key1"  # Oldest

    def test_get_changes_to_reverse_empty_history(self) -> None:
        """Test get_changes_to_reverse with empty history."""
        tracker = HistoryTracker()

        changes = tracker.get_changes_to_reverse(time.time())

        assert changes == []

    def test_get_changes_to_reverse_reverse_chronological_order(self) -> None:
        """Test that get_changes_to_reverse returns events in reverse chronological order."""
        tracker = HistoryTracker()

        # Record changes with delays
        tracker.record_change("key1", "old1", "new1", 1)
        time.sleep(0.001)

        timestamp = time.time()
        time.sleep(0.001)

        # Add multiple events after timestamp
        for i in range(2, 6):
            tracker.record_change(f"key{i}", f"old{i}", f"new{i}", i)
            time.sleep(0.001)

        changes = tracker.get_changes_to_reverse(timestamp)

        # Verify reverse chronological order (most recent first)
        assert len(changes) == 4
        assert changes[0].key == "key5"  # Most recent
        assert changes[1].key == "key4"
        assert changes[2].key == "key3"
        assert changes[3].key == "key2"  # Oldest after timestamp

        # Verify timestamps are in descending order
        for i in range(1, len(changes)):
            assert changes[i - 1].timestamp > changes[i].timestamp

    def test_get_changes_to_reverse_exact_timestamp_match(self) -> None:
        """Test get_changes_to_reverse with exact timestamp match (should not include)."""
        tracker = HistoryTracker()

        # Record a change and capture its exact timestamp
        tracker.record_change("key1", "old1", "new1", 1)
        event1_timestamp = tracker._change_history[0].timestamp

        time.sleep(0.001)
        tracker.record_change("key2", "old2", "new2", 2)

        # Use exact timestamp of first event
        changes = tracker.get_changes_to_reverse(event1_timestamp)

        # Should only get key2 (events AFTER the timestamp)
        assert len(changes) == 1
        assert changes[0].key == "key2"

    def test_get_changes_to_reverse_returns_independent_list(self) -> None:
        """Test that get_changes_to_reverse returns a new list, not a reference."""
        tracker = HistoryTracker()

        tracker.record_change("key1", "old1", "new1", 1)
        time.sleep(0.001)

        timestamp = time.time()
        time.sleep(0.001)

        tracker.record_change("key2", "old2", "new2", 2)

        # Get changes
        changes1 = tracker.get_changes_to_reverse(timestamp)
        changes2 = tracker.get_changes_to_reverse(timestamp)

        # Should be different list instances
        assert changes1 is not changes2

        # But with same content
        assert len(changes1) == len(changes2)
        assert all(c1.key == c2.key for c1, c2 in zip(changes1, changes2))

    def test_get_changes_to_reverse_with_max_size_limitation(self) -> None:
        """Test get_changes_to_reverse when history is limited by max_size."""
        tracker = HistoryTracker(max_size=3)

        # Record 5 changes (only last 3 will be kept)
        for i in range(5):
            tracker.record_change(f"key{i}", f"old{i}", f"new{i}", i)
            time.sleep(0.001)

        # Use timestamp from before all changes
        past_timestamp = time.time() - 100

        changes = tracker.get_changes_to_reverse(past_timestamp)

        # Should only get the 3 kept events in reverse order (key4, key3, key2)
        assert len(changes) == 3
        assert changes[0].key == "key4"  # Most recent
        assert changes[1].key == "key3"
        assert changes[2].key == "key2"  # Oldest kept

    def test_get_changes_to_reverse_with_zero_timestamp(self) -> None:
        """Test get_changes_to_reverse with zero timestamp (should return all in reverse)."""
        tracker = HistoryTracker()

        tracker.record_change("key1", "old1", "new1", 1)
        tracker.record_change("key2", "old2", "new2", 2)
        tracker.record_change("key3", "old3", "new3", 3)

        # Zero timestamp means all events are after it
        changes = tracker.get_changes_to_reverse(0.0)

        assert len(changes) == 3
        assert changes[0].key == "key3"  # Most recent first
        assert changes[1].key == "key2"
        assert changes[2].key == "key1"  # Oldest last

    def test_get_changes_to_reverse_with_negative_timestamp(self) -> None:
        """Test get_changes_to_reverse with negative timestamp."""
        tracker = HistoryTracker()

        tracker.record_change("key1", "old1", "new1", 1)
        tracker.record_change("key2", "old2", "new2", 2)

        # Negative timestamp should work (all events are after it)
        changes = tracker.get_changes_to_reverse(-100.0)

        assert len(changes) == 2
        assert changes[0].key == "key2"  # Most recent first
        assert changes[1].key == "key1"

    def test_get_changes_to_reverse_preserves_event_data(self) -> None:
        """Test that get_changes_to_reverse preserves all event data."""
        tracker = HistoryTracker()

        # Complex data in events
        old_data = {"nested": {"value": 123}}
        new_data = [1, 2, 3]

        tracker.record_change("complex_key", old_data, new_data, 999)

        timestamp = time.time() - 100  # Before the event

        changes = tracker.get_changes_to_reverse(timestamp)

        assert len(changes) == 1
        event = changes[0]
        assert event.key == "complex_key"
        assert event.old_value == old_data
        assert event.new_value == new_data
        assert event.context_id == 999
        assert isinstance(event.timestamp, float)

    def test_get_changes_to_reverse_vs_replay_changes_since(self) -> None:
        """Test that get_changes_to_reverse and replay_changes_since are complementary."""
        tracker = HistoryTracker()

        # Record changes with delays
        tracker.record_change("key1", "old1", "new1", 1)
        time.sleep(0.001)

        timestamp = time.time()
        time.sleep(0.001)

        tracker.record_change("key2", "old2", "new2", 2)
        tracker.record_change("key3", "old3", "new3", 3)

        # Get both sets of changes
        replay_changes = tracker.replay_changes_since(timestamp)
        reverse_changes = tracker.get_changes_to_reverse(timestamp)

        # Should have same events but in opposite order
        assert len(replay_changes) == len(reverse_changes)
        assert len(replay_changes) == 2

        # Verify they are reversed versions of each other
        assert replay_changes[0].key == reverse_changes[1].key  # key2
        assert replay_changes[1].key == reverse_changes[0].key  # key3
