"""Tests for refactored Context class."""

from goldentooth_agent.core.context import Context


class TestContextWithSnapshotManager:
    """Test Context class with SnapshotManager integration."""

    def test_context_snapshot_methods_still_work(self):
        """Test that Context snapshot methods still work after refactoring."""
        context = Context()
        context["key1"] = "value1"
        context["key2"] = "value2"

        # Create snapshot
        snapshot = context.create_snapshot("test_snapshot")
        assert snapshot.name == "test_snapshot"

        # Modify context
        context["key1"] = "modified"

        # Restore snapshot
        context.restore_snapshot("test_snapshot")
        assert context["key1"] == "value1"

        # List snapshots
        snapshots = context.list_snapshots()
        assert "test_snapshot" in snapshots

        # Delete snapshot
        context.delete_snapshot("test_snapshot")
        assert "test_snapshot" not in context.list_snapshots()

    def test_context_snapshot_isolation(self):
        """Test that snapshots are isolated between different Context instances."""
        context1 = Context()
        context2 = Context()

        context1["key"] = "value1"
        context2["key"] = "value2"

        context1.create_snapshot("snap1")
        context2.create_snapshot("snap2")

        # Each context should only see its own snapshots
        assert "snap1" in context1.list_snapshots()
        assert "snap1" not in context2.list_snapshots()
        assert "snap2" in context2.list_snapshots()
        assert "snap2" not in context1.list_snapshots()

    def test_context_fork_preserves_snapshots(self):
        """Test that forking with history preserves snapshots."""
        context = Context()
        context["key"] = "value"
        context.create_snapshot("original_snap")

        # Fork with history
        forked = context.fork_with_history()

        # Forked context should have the snapshot
        assert "original_snap" in forked.list_snapshots()

        # But they should be independent
        forked.create_snapshot("forked_snap")
        assert "forked_snap" in forked.list_snapshots()
        assert "forked_snap" not in context.list_snapshots()
