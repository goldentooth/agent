"""Tests for Context.replay_changes_since method."""

import time
from typing import Any

from context.main import Context


class TestContextReplayChangesSince:
    """Test suite for Context.replay_changes_since method."""

    def test_replay_changes_since_basic(self) -> None:
        """Test basic replay_changes_since functionality."""
        context = Context()

        # Make changes with delays to ensure different timestamps
        context.set("key1", "value1")
        time.sleep(0.001)

        timestamp = time.time()
        time.sleep(0.001)

        context.set("key2", "value2")
        context.set("key3", "value3")

        # Replay changes since timestamp
        changes = context.replay_changes_since(timestamp)

        assert len(changes) == 2
        assert changes[0].key == "key2"
        assert changes[0].new_value == "value2"
        assert changes[1].key == "key3"
        assert changes[1].new_value == "value3"

    def test_replay_changes_since_no_changes_after_timestamp(self) -> None:
        """Test replay_changes_since when no changes occurred after timestamp."""
        context = Context()

        # Make all changes
        context.set("key1", "value1")
        context.set("key2", "value2")
        context.set("key3", "value3")

        # Use timestamp after all changes
        future_timestamp = time.time() + 100

        changes = context.replay_changes_since(future_timestamp)

        assert changes == []

    def test_replay_changes_since_all_changes_after_timestamp(self) -> None:
        """Test replay_changes_since when all changes occurred after timestamp."""
        context = Context()

        # Use timestamp before any changes
        past_timestamp = time.time() - 100

        # Make changes
        context.set("key1", "value1")
        context.set("key2", "value2")
        context.set("key3", "value3")

        changes = context.replay_changes_since(past_timestamp)

        assert len(changes) == 3
        assert changes[0].key == "key1"
        assert changes[0].new_value == "value1"
        assert changes[1].key == "key2"
        assert changes[1].new_value == "value2"
        assert changes[2].key == "key3"
        assert changes[2].new_value == "value3"

    def test_replay_changes_since_empty_history(self) -> None:
        """Test replay_changes_since with empty history."""
        context = Context()

        changes = context.replay_changes_since(time.time())

        assert changes == []

    def test_replay_changes_since_chronological_order(self) -> None:
        """Test that replay_changes_since returns events in chronological order."""
        context = Context()

        # Make change before timestamp
        context.set("key1", "value1")
        time.sleep(0.001)

        timestamp = time.time()
        time.sleep(0.001)

        # Make multiple changes after timestamp
        for i in range(2, 5):
            context.set(f"key{i}", f"value{i}")
            time.sleep(0.001)

        changes = context.replay_changes_since(timestamp)

        assert len(changes) == 3
        # Verify order and timestamps
        for i in range(3):
            assert changes[i].key == f"key{i+2}"
            if i > 0:
                assert changes[i - 1].timestamp < changes[i].timestamp

    def test_replay_changes_since_exact_timestamp_match(self) -> None:
        """Test replay_changes_since with exact timestamp match (should not include)."""
        context = Context()

        # Make a change and capture its exact timestamp
        context.set("key1", "value1")
        event1_timestamp = context.get_change_history()[0].timestamp

        time.sleep(0.001)
        context.set("key2", "value2")

        # Use exact timestamp of first event
        changes = context.replay_changes_since(event1_timestamp)

        # Should only get key2 (events AFTER the timestamp)
        assert len(changes) == 1
        assert changes[0].key == "key2"

    def test_replay_changes_since_returns_independent_list(self) -> None:
        """Test that replay_changes_since returns a new list, not a reference."""
        context = Context()

        context.set("key1", "value1")
        time.sleep(0.001)

        timestamp = time.time()
        time.sleep(0.001)

        context.set("key2", "value2")

        # Get changes
        changes1 = context.replay_changes_since(timestamp)
        changes2 = context.replay_changes_since(timestamp)

        # Should be different list instances
        assert changes1 is not changes2

        # But with same content
        assert len(changes1) == len(changes2)
        assert all(c1.key == c2.key for c1, c2 in zip(changes1, changes2))

    def test_replay_changes_since_with_setitem(self) -> None:
        """Test that replay_changes_since works with __setitem__ syntax."""
        context = Context()

        context["key1"] = "value1"
        time.sleep(0.001)

        timestamp = time.time()
        time.sleep(0.001)

        context["key2"] = "value2"
        context["key3"] = "value3"

        changes = context.replay_changes_since(timestamp)

        assert len(changes) == 2
        assert changes[0].key == "key2"
        assert changes[0].new_value == "value2"
        assert changes[1].key == "key3"
        assert changes[1].new_value == "value3"

    def test_replay_changes_since_with_complex_values(self) -> None:
        """Test that replay_changes_since preserves complex values."""
        context = Context()

        # Complex data
        old_data = {"nested": {"value": 123}}
        new_data = [1, 2, 3]

        context.set("complex_key", old_data)
        time.sleep(0.001)

        timestamp = time.time()
        time.sleep(0.001)

        context.set("complex_key", new_data)
        changes = context.replay_changes_since(timestamp)

        assert len(changes) == 1
        event = changes[0]
        self._assert_complex_event_valid(
            event, "complex_key", old_data, new_data, context
        )

    def _assert_complex_event_valid(
        self, event: Any, key: str, old_value: Any, new_value: Any, context: Context
    ) -> None:
        """Helper method to validate complex event properties."""
        assert event.key == key
        assert event.old_value == old_value
        assert event.new_value == new_value
        assert event.context_id == id(context)
        assert isinstance(event.timestamp, float)

    def test_replay_changes_since_with_zero_timestamp(self) -> None:
        """Test replay_changes_since with zero timestamp (should return all)."""
        context = Context()

        context.set("key1", "value1")
        context.set("key2", "value2")
        context.set("key3", "value3")

        # Zero timestamp means all events are after it
        changes = context.replay_changes_since(0.0)

        assert len(changes) == 3
        assert changes[0].key == "key1"
        assert changes[1].key == "key2"
        assert changes[2].key == "key3"

    def test_replay_changes_since_with_negative_timestamp(self) -> None:
        """Test replay_changes_since with negative timestamp."""
        context = Context()

        context.set("key1", "value1")
        context.set("key2", "value2")

        # Negative timestamp should work (all events are after it)
        changes = context.replay_changes_since(-100.0)

        assert len(changes) == 2
        assert changes[0].key == "key1"
        assert changes[1].key == "key2"

    def test_replay_changes_since_delegates_to_history_tracker(self) -> None:
        """Test that replay_changes_since properly delegates to history tracker."""
        context = Context()

        # Make some changes
        context.set("key1", "value1")
        time.sleep(0.001)

        timestamp = time.time()
        time.sleep(0.001)

        context.set("key2", "value2")

        # Get changes from context method
        context_changes = context.replay_changes_since(timestamp)

        # Get changes directly from history tracker
        tracker_changes = context._history_tracker.replay_changes_since(timestamp)

        # Should be identical
        assert len(context_changes) == len(tracker_changes)
        for ctx_change, tracker_change in zip(context_changes, tracker_changes):
            assert ctx_change.key == tracker_change.key
            assert ctx_change.old_value == tracker_change.old_value
            assert ctx_change.new_value == tracker_change.new_value
            assert ctx_change.context_id == tracker_change.context_id
            assert ctx_change.timestamp == tracker_change.timestamp
