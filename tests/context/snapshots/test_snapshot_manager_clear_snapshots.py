"""Tests for SnapshotManager.clear_snapshots method."""

from typing import Any

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


class TestSnapshotManagerClearSnapshots:
    """Test suite for SnapshotManager.clear_snapshots method."""

    def test_clear_snapshots_basic(self) -> None:
        """Test basic snapshot clearing functionality."""
        manager = SnapshotManager()
        context = MockContext({"key": "value"})

        # Create some snapshots
        manager.create_snapshot(context, "snapshot1")
        manager.create_snapshot(context, "snapshot2")
        assert len(manager.list_snapshots()) == 2

        # Clear all snapshots
        manager.clear_snapshots()

        # Should be empty
        assert len(manager.list_snapshots()) == 0
        snapshots = manager.list_snapshots()
        assert snapshots == {}

    def test_clear_snapshots_returns_none(self) -> None:
        """Test that clear_snapshots returns None."""
        manager = SnapshotManager()
        context = MockContext({"key": "value"})

        # Create snapshot
        manager.create_snapshot(context, "test_snapshot")

        # Clear should return None
        result = manager.clear_snapshots()
        assert result is None

    def test_clear_snapshots_empty_manager(self) -> None:
        """Test clearing empty manager has no effect."""
        manager = SnapshotManager()

        # Clear empty manager should work
        manager.clear_snapshots()

        # Should still be empty
        assert len(manager.list_snapshots()) == 0
        assert manager.list_snapshots() == {}

    def test_clear_snapshots_multiple_snapshots(self) -> None:
        """Test clearing manager with multiple snapshots."""
        manager = SnapshotManager()
        contexts = [
            MockContext({"key1": "value1"}),
            MockContext({"key2": "value2"}),
            MockContext({"key3": "value3"}),
            MockContext({"key4": "value4"}),
            MockContext({"key5": "value5"}),
        ]
        names = ["snapshot_a", "snapshot_b", "snapshot_c", "snapshot_d", "snapshot_e"]

        # Create multiple snapshots
        for context, name in zip(contexts, names):
            manager.create_snapshot(context, name)

        # Verify all exist
        assert len(manager.list_snapshots()) == 5
        all_snapshots = manager.list_snapshots()
        assert all(name in all_snapshots for name in names)

        # Clear all snapshots
        manager.clear_snapshots()

        # Should be completely empty
        assert len(manager.list_snapshots()) == 0
        final_snapshots = manager.list_snapshots()
        assert final_snapshots == {}
        assert all(name not in final_snapshots for name in names)

    def test_clear_snapshots_different_name_formats(self) -> None:
        """Test clearing snapshots with various name formats."""
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

        # Clear all snapshots
        manager.clear_snapshots()

        # Should be empty regardless of name formats
        assert len(manager.list_snapshots()) == 0
        assert manager.list_snapshots() == {}

    def test_clear_snapshots_updates_internal_state(self) -> None:
        """Test that clearing properly updates internal manager state."""
        manager = SnapshotManager()
        context = MockContext({"key": "value"})

        # Create snapshots
        manager.create_snapshot(context, "snapshot1")
        manager.create_snapshot(context, "snapshot2")

        # Verify internal state before clearing
        assert len(manager._snapshots) == 2  # type: ignore[reportPrivateUsage]
        assert "snapshot1" in manager._snapshots  # type: ignore[reportPrivateUsage]
        assert "snapshot2" in manager._snapshots  # type: ignore[reportPrivateUsage]

        # Clear snapshots
        manager.clear_snapshots()

        # Verify internal state after clearing
        assert len(manager._snapshots) == 0  # type: ignore[reportPrivateUsage]
        assert "snapshot1" not in manager._snapshots  # type: ignore[reportPrivateUsage]
        assert "snapshot2" not in manager._snapshots  # type: ignore[reportPrivateUsage]

    def test_clear_snapshots_after_operations(self) -> None:
        """Test clearing snapshots after various operations."""
        manager = SnapshotManager()
        original_context = MockContext({"key": "original"})
        target_context = MockContext({"key": "target"})

        # Create snapshot and perform operations
        manager.create_snapshot(original_context, "operation_test")
        manager.restore_snapshot(target_context, "operation_test")
        manager.list_snapshots()

        # Verify snapshot exists
        assert "operation_test" in manager.list_snapshots()

        # Clear all snapshots
        manager.clear_snapshots()

        # Should be empty after clearing
        assert len(manager.list_snapshots()) == 0
        assert "operation_test" not in manager.list_snapshots()

    def test_clear_snapshots_idempotent(self) -> None:
        """Test that multiple clear operations are idempotent."""
        manager = SnapshotManager()
        context = MockContext({"key": "value"})

        # Create snapshots
        manager.create_snapshot(context, "test1")
        manager.create_snapshot(context, "test2")
        assert len(manager.list_snapshots()) == 2

        # Clear multiple times
        manager.clear_snapshots()
        assert len(manager.list_snapshots()) == 0

        manager.clear_snapshots()
        assert len(manager.list_snapshots()) == 0

        manager.clear_snapshots()
        assert len(manager.list_snapshots()) == 0

        # Should still be empty
        assert manager.list_snapshots() == {}

    def test_clear_snapshots_complex_data_preservation(self) -> None:
        """Test clearing snapshots with complex data structures."""
        manager = SnapshotManager()
        complex_data = {
            "string": "value",
            "number": "123",
            "nested": "structure",
            "empty": "",
            "special": "chars!@#$%^&*()",
        }
        context = MockContext(complex_data)

        # Create snapshot with complex data
        manager.create_snapshot(context, "complex_test")
        assert len(manager.list_snapshots()) == 1

        # Clear snapshots
        manager.clear_snapshots()

        # Should be empty regardless of data complexity
        assert len(manager.list_snapshots()) == 0
        assert manager.list_snapshots() == {}

    def test_clear_snapshots_no_side_effects(self) -> None:
        """Test that clearing snapshots has no side effects on original contexts."""
        manager = SnapshotManager()
        original_context = MockContext({"key": "original"})

        # Create snapshot
        manager.create_snapshot(original_context, "side_effect_test")

        # Modify original context after snapshot creation
        original_context.data["key"] = "modified"
        original_context.data["new"] = "data"

        # Clear snapshots
        manager.clear_snapshots()

        # Original context should be unaffected
        assert original_context.data == {"key": "modified", "new": "data"}

        # Manager should be empty
        assert len(manager.list_snapshots()) == 0

    def test_clear_snapshots_enables_recreation(self) -> None:
        """Test that snapshots can be recreated after clearing."""
        manager = SnapshotManager()
        context = MockContext({"key": "value"})

        # Create snapshot
        original_snapshot = manager.create_snapshot(context, "recreation_test")
        assert len(manager.list_snapshots()) == 1

        # Clear snapshots
        manager.clear_snapshots()
        assert len(manager.list_snapshots()) == 0

        # Should be able to create new snapshots with same names
        new_snapshot = manager.create_snapshot(context, "recreation_test")
        assert len(manager.list_snapshots()) == 1
        assert new_snapshot is not original_snapshot  # Should be different objects

    def test_clear_snapshots_consistent_with_other_operations(self) -> None:
        """Test that clear_snapshots is consistent with other operations."""
        manager = SnapshotManager()
        context = MockContext({"key": "value"})
        snapshot_names = ["consistency_test1", "consistency_test2", "consistency_test3"]

        # Create snapshots
        for name in snapshot_names:
            manager.create_snapshot(context, name)

        # Verify consistency before clearing
        listed_snapshots = manager.list_snapshots()
        assert len(listed_snapshots) == 3
        assert all(name in listed_snapshots for name in snapshot_names)

        # Clear snapshots
        manager.clear_snapshots()

        # Verify consistency after clearing
        final_list = manager.list_snapshots()
        assert len(final_list) == 0 and final_list == {}
        assert all(name not in final_list for name in snapshot_names)
