"""Tests for Context class with HistoryTracker integration."""

import time

from goldentooth_agent.core.context import Context


class TestContextWithHistoryTracker:
    """Test Context class with HistoryTracker integration."""

    def test_context_history_methods_still_work(self):
        """Test that Context history methods still work after refactoring."""
        context = Context()

        # Make some changes
        context["key1"] = "value1"
        context["key2"] = "value2"
        context["key1"] = "updated1"

        # Get history
        history = context.get_change_history()
        assert len(history) == 3
        assert history[0].key == "key1"  # Most recent first
        assert history[0].new_value == "updated1"

        # Clear history
        context.clear_history()
        assert context.get_history_size() == 0

    def test_context_history_size_limits(self):
        """Test that history size limiting still works."""
        context = Context()
        context.set_max_history_size(5)

        # Make more changes than limit
        for i in range(10):
            context[f"key{i}"] = f"value{i}"

        assert context.get_history_size() == 5
        history = context.get_change_history()
        assert history[0].key == "key9"  # Most recent

    def test_context_rollback_functionality(self):
        """Test that rollback functionality still works."""
        context = Context()

        # Set initial values
        context["key1"] = "initial1"
        context["key2"] = "initial2"

        time.sleep(0.1)
        timestamp = time.time()
        time.sleep(0.1)

        # Make changes after timestamp
        context["key1"] = "changed1"
        context["key2"] = "changed2"
        context["key3"] = "new3"

        # Rollback
        context.rollback_to_timestamp(timestamp)

        # Should have reverted to state at timestamp
        assert context["key1"] == "initial1"
        assert context["key2"] == "initial2"
        assert "key3" not in context

        # Should have created auto snapshot
        snapshots = context.list_snapshots()
        assert any("auto_rollback" in name for name in snapshots)

    def test_context_replay_changes(self):
        """Test replaying changes since timestamp."""
        context = Context()

        context["key1"] = "value1"
        time.sleep(0.1)

        timestamp = time.time()
        time.sleep(0.1)

        context["key2"] = "value2"
        context["key3"] = "value3"

        changes = context.replay_changes_since(timestamp)
        assert len(changes) == 2
        assert changes[0].key == "key2"
        assert changes[1].key == "key3"

    def test_context_history_isolation(self):
        """Test that history is isolated between different Context instances."""
        context1 = Context()
        context2 = Context()

        context1["key"] = "value1"
        context2["key"] = "value2"

        history1 = context1.get_change_history()
        history2 = context2.get_change_history()

        assert len(history1) == 1
        assert len(history2) == 1
        assert history1[0].new_value == "value1"
        assert history2[0].new_value == "value2"

    def test_context_fork_with_history_preserves_history(self):
        """Test that forking with history preserves change history."""
        context = Context()

        context["key1"] = "value1"
        context["key2"] = "value2"

        forked = context.fork_with_history()

        # Both should have same history
        original_history = context.get_change_history()
        forked_history = forked.get_change_history()

        assert len(original_history) == len(forked_history)
        assert original_history[0].key == forked_history[0].key

        # But they should be independent
        forked["key3"] = "value3"

        assert len(context.get_change_history()) == 2
        assert len(forked.get_change_history()) == 3
