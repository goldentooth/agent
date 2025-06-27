"""Tests for the ContextSnapshotManager class."""

import pytest

from goldentooth_agent.core.context import Context
from goldentooth_agent.core.context.snapshot_manager import SnapshotManager


class TestSnapshotManager:
    """Test suite for SnapshotManager."""

    def test_create_snapshot(self):
        """Test creating a snapshot."""
        context = Context()
        context["key1"] = "value1"
        context["key2"] = "value2"

        manager = SnapshotManager()
        snapshot = manager.create_snapshot(context, "test_snapshot")

        assert snapshot.name == "test_snapshot"
        assert len(snapshot.frames) == 1
        assert snapshot.frames[0]["key1"] == "value1"
        assert snapshot.frames[0]["key2"] == "value2"

    def test_create_duplicate_snapshot_raises_error(self):
        """Test that creating a snapshot with duplicate name raises ValueError."""
        context = Context()
        manager = SnapshotManager()

        manager.create_snapshot(context, "test_snapshot")

        with pytest.raises(ValueError, match="Snapshot 'test_snapshot' already exists"):
            manager.create_snapshot(context, "test_snapshot")

    def test_restore_snapshot(self):
        """Test restoring a snapshot."""
        context = Context()
        context["key1"] = "value1"
        context["key2"] = "value2"

        manager = SnapshotManager()
        manager.create_snapshot(context, "test_snapshot")

        # Modify context
        context["key1"] = "modified"
        context["key3"] = "new_value"

        # Restore snapshot
        manager.restore_snapshot(context, "test_snapshot")

        assert context["key1"] == "value1"
        assert context["key2"] == "value2"
        assert "key3" not in context

    def test_restore_nonexistent_snapshot_raises_error(self):
        """Test that restoring a nonexistent snapshot raises KeyError."""
        context = Context()
        manager = SnapshotManager()

        with pytest.raises(KeyError, match="Snapshot 'nonexistent' not found"):
            manager.restore_snapshot(context, "nonexistent")

    def test_list_snapshots(self):
        """Test listing snapshots."""
        context = Context()
        manager = SnapshotManager()

        # Create multiple snapshots
        manager.create_snapshot(context, "snapshot1")
        manager.create_snapshot(context, "snapshot2")

        snapshots = manager.list_snapshots()

        assert "snapshot1" in snapshots
        assert "snapshot2" in snapshots
        assert isinstance(snapshots["snapshot1"], float)  # timestamp

    def test_delete_snapshot(self):
        """Test deleting a snapshot."""
        context = Context()
        manager = SnapshotManager()

        manager.create_snapshot(context, "test_snapshot")
        manager.delete_snapshot("test_snapshot")

        snapshots = manager.list_snapshots()
        assert "test_snapshot" not in snapshots

    def test_delete_nonexistent_snapshot_raises_error(self):
        """Test that deleting a nonexistent snapshot raises KeyError."""
        manager = SnapshotManager()

        with pytest.raises(KeyError, match="Snapshot 'nonexistent' not found"):
            manager.delete_snapshot("nonexistent")

    def test_snapshot_preserves_multiple_frames(self):
        """Test that snapshots preserve multiple context frames."""
        context = Context()
        context["key1"] = "value1"

        context.push_layer()
        context["key2"] = "value2"

        manager = SnapshotManager()
        snapshot = manager.create_snapshot(context, "multi_frame")

        assert len(snapshot.frames) == 2
        assert snapshot.frames[0]["key1"] == "value1"
        assert snapshot.frames[1]["key2"] == "value2"

    def test_snapshot_preserves_computed_properties(self):
        """Test that snapshots preserve computed property definitions."""
        context = Context()
        context["base"] = 10

        # Add a computed property
        context.add_computed_property("doubled", lambda ctx: ctx["base"] * 2, ["base"])

        manager = SnapshotManager()
        snapshot = manager.create_snapshot(context, "with_computed")

        assert "doubled" in snapshot.computed_properties
        assert snapshot.computed_properties["doubled"]["dependencies"] == ["base"]

    def test_restore_preserves_computed_properties(self):
        """Test that restoring snapshots preserves computed properties."""
        context = Context()
        context["base"] = 10
        context.add_computed_property("doubled", lambda ctx: ctx["base"] * 2, ["base"])

        manager = SnapshotManager()
        manager.create_snapshot(context, "with_computed")

        # Clear computed properties
        context._computed_properties.clear()

        # Restore
        manager.restore_snapshot(context, "with_computed")

        assert context["doubled"] == 20
