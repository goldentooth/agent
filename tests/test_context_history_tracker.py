"""Tests for the ContextHistoryTracker class."""

import time

import pytest

from goldentooth_agent.core.context import Context
from goldentooth_agent.core.context.history_tracker import (
    ContextChangeEvent,
    HistoryTracker,
)


class TestHistoryTracker:
    """Test suite for HistoryTracker."""

    def test_record_change(self):
        """Test recording a change event."""
        tracker = HistoryTracker()
        context_id = 123

        tracker.record_change("key1", "old_value", "new_value", context_id)

        history = tracker.get_history()
        assert len(history) == 1
        assert history[0].key == "key1"
        assert history[0].old_value == "old_value"
        assert history[0].new_value == "new_value"
        assert history[0].context_id == context_id

    def test_get_history_with_limit(self):
        """Test getting history with a limit."""
        tracker = HistoryTracker()
        context_id = 123

        # Record multiple changes
        for i in range(10):
            tracker.record_change(f"key{i}", f"old{i}", f"new{i}", context_id)

        # Get limited history (most recent first)
        limited = tracker.get_history(limit=3)
        assert len(limited) == 3
        assert limited[0].key == "key9"  # Most recent
        assert limited[1].key == "key8"
        assert limited[2].key == "key7"

    def test_get_history_since_timestamp(self):
        """Test getting history since a specific timestamp."""
        tracker = HistoryTracker()
        context_id = 123

        # Record changes with time gaps
        tracker.record_change("key1", "old1", "new1", context_id)
        time.sleep(0.1)

        timestamp_marker = time.time()
        time.sleep(0.1)

        tracker.record_change("key2", "old2", "new2", context_id)
        tracker.record_change("key3", "old3", "new3", context_id)

        # Get history since marker
        recent = tracker.get_history(since=timestamp_marker)
        assert len(recent) == 2
        assert recent[0].key == "key3"  # Most recent first
        assert recent[1].key == "key2"

    def test_clear_history(self):
        """Test clearing history."""
        tracker = HistoryTracker()
        context_id = 123

        tracker.record_change("key1", "old1", "new1", context_id)
        tracker.record_change("key2", "old2", "new2", context_id)

        assert tracker.get_history_size() == 2

        tracker.clear_history()

        assert tracker.get_history_size() == 0
        assert len(tracker.get_history()) == 0

    def test_max_history_size(self):
        """Test history size limiting."""
        tracker = HistoryTracker(max_size=5)
        context_id = 123

        # Record more than max size
        for i in range(10):
            tracker.record_change(f"key{i}", f"old{i}", f"new{i}", context_id)

        # Should only keep most recent 5
        assert tracker.get_history_size() == 5
        history = tracker.get_history()
        assert history[0].key == "key9"  # Most recent
        assert history[4].key == "key5"  # Oldest kept

    def test_set_max_history_size(self):
        """Test changing max history size."""
        tracker = HistoryTracker()
        context_id = 123

        # Record 10 changes
        for i in range(10):
            tracker.record_change(f"key{i}", f"old{i}", f"new{i}", context_id)

        # Set max size to 3
        tracker.set_max_history_size(3)

        assert tracker.get_history_size() == 3
        history = tracker.get_history()
        assert history[0].key == "key9"
        assert history[2].key == "key7"

    def test_set_max_history_size_invalid(self):
        """Test setting invalid max history size."""
        tracker = HistoryTracker()

        with pytest.raises(ValueError, match="History size must be non-negative"):
            tracker.set_max_history_size(-1)

    def test_set_max_history_size_zero(self):
        """Test setting max history size to zero."""
        tracker = HistoryTracker()
        context_id = 123

        tracker.record_change("key1", "old1", "new1", context_id)
        tracker.set_max_history_size(0)

        assert tracker.get_history_size() == 0

    def test_replay_changes_since(self):
        """Test replaying changes since a timestamp."""
        tracker = HistoryTracker()
        context_id = 123

        # Record changes
        tracker.record_change("key1", "old1", "new1", context_id)
        time.sleep(0.1)

        timestamp = time.time()
        time.sleep(0.1)

        tracker.record_change("key2", "old2", "new2", context_id)
        tracker.record_change("key3", "old3", "new3", context_id)

        # Replay changes since timestamp (chronological order)
        changes = tracker.replay_changes_since(timestamp)
        assert len(changes) == 2
        assert changes[0].key == "key2"  # First after timestamp
        assert changes[1].key == "key3"  # Second after timestamp

    def test_rollback_preparation(self):
        """Test preparing for rollback by getting changes to reverse."""
        tracker = HistoryTracker()
        context_id = 123

        # Record changes
        tracker.record_change("key1", "old1", "new1", context_id)
        tracker.record_change("key2", "old2", "new2", context_id)
        time.sleep(0.1)

        timestamp = time.time()
        time.sleep(0.1)

        tracker.record_change("key3", "old3", "new3", context_id)
        tracker.record_change("key4", "old4", "new4", context_id)

        # Get changes that need to be reversed for rollback
        to_reverse = tracker.get_changes_to_reverse(timestamp)
        assert len(to_reverse) == 2
        assert to_reverse[0].key == "key4"  # Most recent first for reversal
        assert to_reverse[1].key == "key3"

    def test_history_tracker_with_context_integration(self):
        """Test that HistoryTracker can work with Context objects."""
        context = Context()
        tracker = HistoryTracker()

        # Simulate context changes
        context["key1"] = "value1"
        tracker.record_change("key1", None, "value1", id(context))

        context["key1"] = "value2"
        tracker.record_change("key1", "value1", "value2", id(context))

        history = tracker.get_history()
        assert len(history) == 2
        assert history[0].old_value == "value1"
        assert history[0].new_value == "value2"

    def test_change_event_representation(self):
        """Test ContextChangeEvent string representation."""
        event = ContextChangeEvent("test_key", "old", "new", 123)
        repr_str = repr(event)

        assert "test_key" in repr_str
        assert "old" in repr_str
        assert "new" in repr_str
        assert "t=" in repr_str  # timestamp

    def test_concurrent_recording(self):
        """Test that history tracker handles concurrent recording correctly."""
        tracker = HistoryTracker(max_size=100)
        context_id = 123

        # Record many changes quickly
        for i in range(50):
            tracker.record_change(f"key{i}", f"old{i}", f"new{i}", context_id)

        assert tracker.get_history_size() == 50

        # Verify order is preserved
        history = tracker.get_history()
        for i in range(50):
            assert history[i].key == f"key{49-i}"  # Most recent first
