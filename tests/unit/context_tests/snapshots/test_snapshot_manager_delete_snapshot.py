"""Tests for SnapshotManager.delete_snapshot method."""

from typing import Any

import pytest

from context.snapshot_manager import SnapshotManager


class MockContext:
    """Mock Context class for testing purposes."""

    def __init__(self, data: dict[str, str] | None = None) -> None:
        super().__init__()
        self.data = data or {}

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, MockContext):
            return False
        return self.data == other.data


class TestSnapshotManagerDeleteSnapshot:
    """Test suite for SnapshotManager.delete_snapshot method."""

    def test_delete_snapshot_basic(self) -> None:
        """Test basic snapshot deletion functionality."""
        manager = SnapshotManager()
        context = MockContext({"key": "value"})

        # Create snapshot
        manager.create_snapshot(context, "test_snapshot")
        assert "test_snapshot" in manager.list_snapshots()

        # Delete snapshot
        manager.delete_snapshot("test_snapshot")

        # Should be removed from snapshots
        assert "test_snapshot" not in manager.list_snapshots()
        assert len(manager.list_snapshots()) == 0

    def test_delete_snapshot_nonexistent_raises_error(self) -> None:
        """Test that deleting nonexistent snapshot raises KeyError."""
        manager = SnapshotManager()

        # Attempt to delete nonexistent snapshot should raise KeyError
        with pytest.raises(KeyError, match="Snapshot 'nonexistent' not found"):
            manager.delete_snapshot("nonexistent")

    def test_delete_snapshot_returns_none(self) -> None:
        """Test that delete_snapshot returns None."""
        manager = SnapshotManager()
        context = MockContext({"key": "value"})

        # Create snapshot
        manager.create_snapshot(context, "test_snapshot")

        # Delete doesn't return a value
        manager.delete_snapshot("test_snapshot")

    def test_delete_snapshot_multiple_snapshots(self) -> None:
        """Test deleting specific snapshot from multiple snapshots."""
        manager = SnapshotManager()
        contexts = [
            MockContext({"key1": "value1"}),
            MockContext({"key2": "value2"}),
            MockContext({"key3": "value3"}),
        ]
        names = ["snapshot_a", "snapshot_b", "snapshot_c"]

        # Create multiple snapshots
        for context, name in zip(contexts, names):
            manager.create_snapshot(context, name)

        # Verify all exist
        snapshots = manager.list_snapshots()
        assert len(snapshots) == 3
        assert all(name in snapshots for name in names)

        # Delete middle snapshot and verify removal
        manager.delete_snapshot("snapshot_b")
        remaining = manager.list_snapshots()
        assert len(remaining) == 2
        assert "snapshot_a" in remaining
        assert "snapshot_b" not in remaining
        assert "snapshot_c" in remaining

    def test_delete_snapshot_different_name_formats(self) -> None:
        """Test deleting snapshots with various name formats."""
        manager = SnapshotManager()
        context = MockContext({"key": "value"})

        # Create snapshots with different name formats
        names = [
            "simple",
            "with_underscore",
            "with-dash",
            "with.dot",
            "with spaces",
            "123numeric",
            "MixedCase",
            "UPPERCASE",
            "",  # Empty string
        ]

        # Create all snapshots
        for name in names:
            manager.create_snapshot(context, name)

        # Verify all exist
        assert len(manager.list_snapshots()) == len(names)

        # Delete each snapshot and verify removal
        for name in names:
            manager.delete_snapshot(name)
            assert name not in manager.list_snapshots()

        # Should be empty at the end
        assert len(manager.list_snapshots()) == 0

    def test_delete_snapshot_exact_name_match(self) -> None:
        """Test that deletion requires exact name match."""
        manager = SnapshotManager()
        context = MockContext({"key": "value"})

        # Create snapshot with specific case
        manager.create_snapshot(context, "ExactName")

        # Different case should fail
        with pytest.raises(KeyError, match="Snapshot 'exactname' not found"):
            manager.delete_snapshot("exactname")

        # Original should still exist
        assert "ExactName" in manager.list_snapshots()

        # Exact case should work
        manager.delete_snapshot("ExactName")
        assert "ExactName" not in manager.list_snapshots()

    def test_delete_snapshot_empty_manager(self) -> None:
        """Test deleting from empty manager raises error."""
        manager = SnapshotManager()

        # Should raise error for any name
        with pytest.raises(KeyError, match="Snapshot 'any_name' not found"):
            manager.delete_snapshot("any_name")

    def test_delete_snapshot_after_restore_operations(self) -> None:
        """Test deleting snapshot after restore operations."""
        manager = SnapshotManager()
        original_context = MockContext({"key": "original"})
        target_context = MockContext({"key": "target"})

        # Create snapshot
        manager.create_snapshot(original_context, "restore_test")

        # Restore snapshot multiple times
        manager.restore_snapshot(target_context, "restore_test")
        manager.restore_snapshot(target_context, "restore_test")

        # Should still be able to delete
        manager.delete_snapshot("restore_test")
        assert "restore_test" not in manager.list_snapshots()

    def test_delete_snapshot_multiple_deletions_same_name(self) -> None:
        """Test that multiple deletions of same name raise errors."""
        manager = SnapshotManager()
        context = MockContext({"key": "value"})

        # Create snapshot
        manager.create_snapshot(context, "delete_test")

        # First deletion should work
        manager.delete_snapshot("delete_test")
        assert "delete_test" not in manager.list_snapshots()

        # Second deletion should raise error
        with pytest.raises(KeyError, match="Snapshot 'delete_test' not found"):
            manager.delete_snapshot("delete_test")

    def test_delete_snapshot_preserves_other_snapshots(self) -> None:
        """Test that deleting one snapshot preserves others completely."""
        manager = SnapshotManager()
        contexts = [
            MockContext({"data": "first"}),
            MockContext({"data": "second"}),
            MockContext({"data": "third"}),
        ]
        names = ["keep1", "delete_me", "keep2"]

        # Create snapshots and store for later verification
        snapshots: dict[str, Any] = {}
        for context, name in zip(contexts, names):
            snapshots[name] = manager.create_snapshot(context, name)

        # Delete middle snapshot and verify others preserved
        manager.delete_snapshot("delete_me")
        remaining = manager.list_snapshots()
        assert len(remaining) == 2
        assert remaining["keep1"] == snapshots["keep1"].timestamp
        assert remaining["keep2"] == snapshots["keep2"].timestamp
        assert "delete_me" not in remaining

        # Verify restore still works for preserved snapshots
        target = MockContext({})
        manager.restore_snapshot(target, "keep1")
        assert target.data == {"data": "first"}

    def test_delete_snapshot_updates_internal_state(self) -> None:
        """Test that deletion properly updates internal manager state."""
        manager = SnapshotManager()
        context = MockContext({"key": "value"})

        # Create snapshot
        manager.create_snapshot(context, "state_test")

        # Verify internal state before deletion
        assert len(manager._snapshots) == 1
        assert "state_test" in manager._snapshots

        # Delete snapshot
        manager.delete_snapshot("state_test")

        # Verify internal state after deletion
        assert len(manager._snapshots) == 0
        assert "state_test" not in manager._snapshots

    def test_delete_snapshot_consistent_with_list_snapshots(self) -> None:
        """Test that delete_snapshot is consistent with list_snapshots."""
        manager = SnapshotManager()
        context = MockContext({"key": "value"})

        # Create snapshots and verify initial state
        names = ["snapshot1", "snapshot2", "snapshot3"]
        for name in names:
            manager.create_snapshot(context, name)
        assert len(manager.list_snapshots()) == 3

        # Delete first snapshot and verify consistency
        manager.delete_snapshot("snapshot2")
        updated_list = manager.list_snapshots()
        assert len(updated_list) == 2
        assert "snapshot1" in updated_list and "snapshot3" in updated_list
        assert "snapshot2" not in updated_list

        # Delete second snapshot and verify final state
        manager.delete_snapshot("snapshot1")
        final_list = manager.list_snapshots()
        assert len(final_list) == 1 and "snapshot3" in final_list
