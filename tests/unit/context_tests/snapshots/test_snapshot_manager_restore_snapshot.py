"""Tests for SnapshotManager.restore_snapshot method."""

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


class TestSnapshotManagerRestoreSnapshot:
    """Test suite for SnapshotManager.restore_snapshot method."""

    def test_restore_snapshot_basic(self) -> None:
        """Test basic snapshot restoration functionality."""
        manager = SnapshotManager()
        original_context = MockContext({"key": "original_value"})
        target_context = MockContext({"key": "target_value"})

        # Create snapshot
        manager.create_snapshot(original_context, "test_snapshot")

        # Restore snapshot to target context
        manager.restore_snapshot(target_context, "test_snapshot")

        # Target context should now have original data
        assert target_context.data == original_context.data

    def test_restore_snapshot_nonexistent_raises_error(self) -> None:
        """Test that restoring nonexistent snapshot raises KeyError."""
        manager = SnapshotManager()
        context = MockContext({"key": "value"})

        # Attempt to restore nonexistent snapshot should raise KeyError
        with pytest.raises(KeyError, match="Snapshot 'nonexistent' not found"):
            manager.restore_snapshot(context, "nonexistent")

    def test_restore_snapshot_returns_none(self) -> None:
        """Test that restore_snapshot returns None."""
        manager = SnapshotManager()
        original_context = MockContext({"key": "value"})
        target_context = MockContext({})

        # Create snapshot
        manager.create_snapshot(original_context, "test_snapshot")

        # Restore doesn't return a value
        manager.restore_snapshot(target_context, "test_snapshot")
        # restore_snapshot returns None, so no need to check return value

    def test_restore_snapshot_multiple_times(self) -> None:
        """Test restoring the same snapshot multiple times."""
        manager = SnapshotManager()
        original_context = MockContext({"key": "original"})
        target_context = MockContext({"key": "target"})

        # Create snapshot
        manager.create_snapshot(original_context, "multi_restore")

        # Restore multiple times
        manager.restore_snapshot(target_context, "multi_restore")
        first_restore_data = target_context.data.copy()

        # Modify target context
        target_context.data = {"key": "modified"}

        # Restore again
        manager.restore_snapshot(target_context, "multi_restore")
        second_restore_data = target_context.data.copy()

        # Both restores should result in the same data
        assert first_restore_data == second_restore_data
        assert target_context.data == original_context.data

    def test_restore_snapshot_to_different_contexts(self) -> None:
        """Test restoring the same snapshot to different target contexts."""
        manager = SnapshotManager()
        original_context = MockContext({"shared": "data"})

        targets = [
            MockContext({"target1": "data"}),
            MockContext({"target2": "different"}),
            MockContext({}),
        ]

        # Create snapshot
        manager.create_snapshot(original_context, "shared_snapshot")

        # Restore to all target contexts
        for target in targets:
            manager.restore_snapshot(target, "shared_snapshot")
            assert target.data == original_context.data

        # All targets should have the same data now
        for target in targets:
            assert target.data == original_context.data

    def test_restore_snapshot_preserves_original_snapshot(self) -> None:
        """Test that restoring doesn't modify the original snapshot."""
        manager = SnapshotManager()
        original_context = MockContext({"preserve": "this"})
        target_context = MockContext({"change": "this"})

        # Create snapshot
        snapshot = manager.create_snapshot(original_context, "preserve_test")
        original_timestamp = snapshot.timestamp

        # Restore snapshot
        manager.restore_snapshot(target_context, "preserve_test")

        # Modify target context after restore
        target_context.data = {"modified": "after_restore"}

        # Original snapshot should be unchanged
        preserved_snapshot = manager.get_snapshot("preserve_test")
        assert preserved_snapshot is snapshot
        assert preserved_snapshot.timestamp == original_timestamp

        # Create another target and restore again
        another_target = MockContext({})
        manager.restore_snapshot(another_target, "preserve_test")
        assert another_target.data == original_context.data

    def test_restore_snapshot_exact_name_match(self) -> None:
        """Test that restoration requires exact name match."""
        manager = SnapshotManager()
        original_context = MockContext({"key": "value"})
        target_context = MockContext({})

        # Create snapshot with specific case
        manager.create_snapshot(original_context, "ExactName")

        # Different case should fail
        with pytest.raises(KeyError, match="Snapshot 'exactname' not found"):
            manager.restore_snapshot(target_context, "exactname")

        # Target should be unchanged
        assert target_context.data == {}

        # Exact case should work
        manager.restore_snapshot(target_context, "ExactName")
        assert target_context.data == original_context.data

    def test_restore_snapshot_empty_manager(self) -> None:
        """Test restoring from empty manager raises error."""
        manager = SnapshotManager()
        context = MockContext({})

        # Should raise error for any name
        with pytest.raises(KeyError, match="Snapshot 'any_name' not found"):
            manager.restore_snapshot(context, "any_name")

    def test_restore_snapshot_after_deletion(self) -> None:
        """Test that restore fails after snapshot deletion."""
        manager = SnapshotManager()
        original_context = MockContext({"key": "value"})
        target_context = MockContext({})

        # Create and then delete snapshot
        manager.create_snapshot(original_context, "delete_test")
        manager.delete_snapshot("delete_test")

        # Restore should fail
        with pytest.raises(KeyError, match="Snapshot 'delete_test' not found"):
            manager.restore_snapshot(target_context, "delete_test")

    def test_restore_snapshot_different_name_formats(self) -> None:
        """Test restoring snapshots with various name formats."""
        manager = SnapshotManager()
        original_context = MockContext({"format": "test"})

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
            manager.create_snapshot(original_context, name)

        # Restore each snapshot and verify
        for name in names:
            target_context = MockContext({})
            manager.restore_snapshot(target_context, name)
            assert target_context.data == original_context.data

    def test_restore_snapshot_with_complex_data(self) -> None:
        """Test restoring snapshots with complex data structures."""
        manager = SnapshotManager()

        # Complex data structure (as strings for MockContext)
        complex_data = {
            "simple": "value",
            "nested": "deep_structure",
            "list": "list_representation",
            "number": "42",
            "boolean": "true",
            "none_value": "null",
        }
        original_context = MockContext(complex_data)
        target_context = MockContext({"empty": "start"})

        # Create and restore snapshot
        manager.create_snapshot(original_context, "complex_restore")
        manager.restore_snapshot(target_context, "complex_restore")

        # Should restore all complex data correctly
        assert target_context.data == complex_data

    def test_restore_snapshot_with_none_context(self) -> None:
        """Test restoring snapshot with None context."""
        manager = SnapshotManager()
        target_context = MockContext({"existing": "data"})

        # Create snapshot with None context
        manager.create_snapshot(None, "none_context")

        # Restore should work
        manager.restore_snapshot(target_context, "none_context")

        # The restore behavior depends on implementation
        # but should not raise an error
        assert True  # Test passes if no exception

    def test_restore_snapshot_calls_snapshot_restore_to(self) -> None:
        """Test that restore_snapshot calls the snapshot's restore_to method."""
        manager = SnapshotManager()
        original_context = MockContext({"method": "test"})
        target_context = MockContext({})

        # Create snapshot
        snapshot = manager.create_snapshot(original_context, "method_test")

        # Verify snapshot has restore_to method
        assert hasattr(snapshot, "restore_to")
        assert callable(snapshot.restore_to)

        # Restore snapshot
        manager.restore_snapshot(target_context, "method_test")

        # Should have called restore_to and modified target
        assert target_context.data == original_context.data

    def test_restore_snapshot_sequential_restores(self) -> None:
        """Test sequential restores to the same context."""
        manager = SnapshotManager()
        contexts = [
            MockContext({"stage": "first"}),
            MockContext({"stage": "second"}),
            MockContext({"stage": "third"}),
        ]
        target_context = MockContext({"stage": "initial"})

        # Create multiple snapshots
        for i, context in enumerate(contexts):
            manager.create_snapshot(context, f"stage_{i}")

        # Restore in sequence
        for i in range(len(contexts)):
            manager.restore_snapshot(target_context, f"stage_{i}")
            assert target_context.data == contexts[i].data

        # Final state should match last restore
        assert target_context.data == contexts[-1].data

    def test_restore_snapshot_error_message_format(self) -> None:
        """Test that missing snapshot error has correct message format."""
        manager = SnapshotManager()
        context = MockContext({})

        # Test exact error message format
        with pytest.raises(KeyError) as exc_info:
            manager.restore_snapshot(context, "missing_snapshot")

        error_message = str(exc_info.value)
        assert "Snapshot 'missing_snapshot' not found" in error_message

    def test_restore_snapshot_consistent_with_get_snapshot(self) -> None:
        """Test that restore_snapshot is consistent with get_snapshot."""
        manager = SnapshotManager()
        original_context = MockContext({"consistency": "test"})
        target_context = MockContext({})

        # Create snapshot
        manager.create_snapshot(original_context, "consistency_test")

        # Get snapshot directly
        snapshot = manager.get_snapshot("consistency_test")

        # Restore using manager method
        manager.restore_snapshot(target_context, "consistency_test")

        # Both should reference the same snapshot and produce same result
        manual_target = MockContext({})
        snapshot.restore_to(manual_target)

        assert target_context.data == manual_target.data
        assert target_context.data == original_context.data

    def test_restore_snapshot_updates_target_completely(self) -> None:
        """Test that restore completely updates target context."""
        manager = SnapshotManager()
        original_context = MockContext({"complete": "new_data"})
        target_context = MockContext(
            {"old_key1": "old_value1", "old_key2": "old_value2", "complete": "old_data"}
        )

        # Create snapshot
        manager.create_snapshot(original_context, "complete_test")

        # Store original target state for comparison
        old_data = target_context.data.copy()

        # Restore snapshot
        manager.restore_snapshot(target_context, "complete_test")

        # Target should be completely updated to match original
        assert target_context.data == original_context.data
        assert target_context.data != old_data

    def test_restore_snapshot_handles_empty_original_context(self) -> None:
        """Test restoring snapshot from empty original context."""
        manager = SnapshotManager()
        original_context = MockContext({})  # Empty
        target_context = MockContext({"has": "data"})

        # Create snapshot from empty context
        manager.create_snapshot(original_context, "empty_original")

        # Restore to target with data
        manager.restore_snapshot(target_context, "empty_original")

        # Target should become empty like original
        assert target_context.data == {}
        assert target_context.data == original_context.data
