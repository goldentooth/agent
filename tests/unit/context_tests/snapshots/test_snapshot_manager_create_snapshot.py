"""Tests for SnapshotManager.create_snapshot method."""

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


class TestSnapshotManagerCreateSnapshot:
    """Test suite for SnapshotManager.create_snapshot method."""

    def test_create_snapshot_basic(self) -> None:
        """Test basic snapshot creation functionality."""
        manager = SnapshotManager()
        context = MockContext({"key": "value"})

        # Create snapshot
        snapshot = manager.create_snapshot(context, "test_snapshot")

        # Should return a snapshot object
        assert snapshot is not None
        from context.snapshots import ContextSnapshot

        assert isinstance(snapshot, ContextSnapshot)

        # Should be added to manager's snapshots
        assert "test_snapshot" in manager.list_snapshots()
        assert len(manager.list_snapshots()) == 1

    def test_create_snapshot_duplicate_name_raises_error(self) -> None:
        """Test that creating snapshot with duplicate name raises ValueError."""
        manager = SnapshotManager()
        context = MockContext({"key": "value"})

        # Create first snapshot
        manager.create_snapshot(context, "duplicate_name")

        # Attempt to create second snapshot with same name should raise ValueError
        with pytest.raises(
            ValueError, match="Snapshot 'duplicate_name' already exists"
        ):
            manager.create_snapshot(context, "duplicate_name")

    def test_create_snapshot_returns_correct_snapshot(self) -> None:
        """Test that create_snapshot returns the correct snapshot object."""
        manager = SnapshotManager()
        context = MockContext({"key": "value"})

        # Create snapshot and verify it's the correct one
        snapshot = manager.create_snapshot(context, "test_snapshot")
        retrieved = manager.get_snapshot("test_snapshot")

        assert snapshot is retrieved
        assert snapshot.name == "test_snapshot"

    def test_create_snapshot_multiple_snapshots(self) -> None:
        """Test creating multiple snapshots with different names."""
        manager = SnapshotManager()
        contexts = [
            MockContext({"key1": "value1"}),
            MockContext({"key2": "value2"}),
            MockContext({"key3": "value3"}),
        ]
        names = ["snapshot_a", "snapshot_b", "snapshot_c"]

        # Create multiple snapshots
        snapshots = []
        for context, name in zip(contexts, names):
            snapshot = manager.create_snapshot(context, name)
            snapshots.append(snapshot)

        # Verify all exist
        snapshot_list = manager.list_snapshots()
        assert len(snapshot_list) == 3
        assert all(name in snapshot_list for name in names)

        # Verify each snapshot is correct
        for i, name in enumerate(names):
            retrieved = manager.get_snapshot(name)
            assert retrieved is snapshots[i]
            assert retrieved.name == name

    def test_create_snapshot_different_name_formats(self) -> None:
        """Test creating snapshots with various name formats."""
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
        snapshots = []
        for name in names:
            snapshot = manager.create_snapshot(context, name)
            snapshots.append(snapshot)

        # Verify all exist and are correct
        assert len(manager.list_snapshots()) == len(names)
        for i, name in enumerate(names):
            retrieved = manager.get_snapshot(name)
            assert retrieved is snapshots[i]
            assert retrieved.name == name

    def test_create_snapshot_with_different_contexts(self) -> None:
        """Test creating snapshots with different context objects."""
        manager = SnapshotManager()

        # Different context types and data
        contexts = [
            MockContext({"simple": "value"}),
            MockContext({"nested": "deep_value"}),
            MockContext({}),  # Empty context
            MockContext({"multiple": "values", "in": "context"}),
        ]

        snapshots = []
        for i, context in enumerate(contexts):
            snapshot = manager.create_snapshot(context, f"context_{i}")
            snapshots.append(snapshot)

        # Verify all snapshots created correctly
        assert len(manager.list_snapshots()) == len(contexts)
        for i, snapshot in enumerate(snapshots):
            assert snapshot.name == f"context_{i}"
            retrieved = manager.get_snapshot(f"context_{i}")
            assert retrieved is snapshot

    def test_create_snapshot_updates_internal_state(self) -> None:
        """Test that creation properly updates internal manager state."""
        manager = SnapshotManager()
        context = MockContext({"key": "value"})

        # Verify initial state
        assert len(manager._snapshots) == 0
        assert "test_snapshot" not in manager._snapshots

        # Create snapshot
        snapshot = manager.create_snapshot(context, "test_snapshot")

        # Verify internal state after creation
        assert len(manager._snapshots) == 1
        assert "test_snapshot" in manager._snapshots
        assert manager._snapshots["test_snapshot"] is snapshot

    def test_create_snapshot_preserves_existing_snapshots(self) -> None:
        """Test that creating new snapshot preserves existing ones."""
        manager = SnapshotManager()
        context1 = MockContext({"data": "first"})
        context2 = MockContext({"data": "second"})

        # Create first snapshot
        snapshot1 = manager.create_snapshot(context1, "first")
        first_timestamp = snapshot1.timestamp

        # Create second snapshot
        snapshot2 = manager.create_snapshot(context2, "second")

        # Verify both exist and first is preserved
        snapshots = manager.list_snapshots()
        assert len(snapshots) == 2
        assert "first" in snapshots
        assert "second" in snapshots
        assert snapshots["first"] == first_timestamp

        # Verify first snapshot is still accessible and unchanged
        retrieved_first = manager.get_snapshot("first")
        assert retrieved_first is snapshot1
        assert retrieved_first.timestamp == first_timestamp

    def test_create_snapshot_handles_none_context(self) -> None:
        """Test creating snapshot with None context."""
        manager = SnapshotManager()

        # Create snapshot with None context
        snapshot = manager.create_snapshot(None, "none_context")

        # Should still create successfully
        assert snapshot is not None
        assert "none_context" in manager.list_snapshots()
        retrieved = manager.get_snapshot("none_context")
        assert retrieved is snapshot

    def test_create_snapshot_case_sensitive_names(self) -> None:
        """Test that snapshot names are case sensitive."""
        manager = SnapshotManager()
        context = MockContext({"key": "value"})

        # Create snapshots with similar but different case names
        snapshot1 = manager.create_snapshot(context, "TestSnapshot")
        snapshot2 = manager.create_snapshot(context, "testSnapshot")
        snapshot3 = manager.create_snapshot(context, "testsnapshot")

        # All should exist as separate snapshots
        snapshots = manager.list_snapshots()
        assert len(snapshots) == 3
        assert "TestSnapshot" in snapshots
        assert "testSnapshot" in snapshots
        assert "testsnapshot" in snapshots

        # Each should be retrievable independently
        assert manager.get_snapshot("TestSnapshot") is snapshot1
        assert manager.get_snapshot("testSnapshot") is snapshot2
        assert manager.get_snapshot("testsnapshot") is snapshot3

    def test_create_snapshot_import_handling(self) -> None:
        """Test that create_snapshot handles circular import correctly."""
        manager = SnapshotManager()
        context = MockContext({"key": "value"})

        # Create multiple snapshots to test import behavior
        snapshot1 = manager.create_snapshot(context, "import_test1")
        snapshot2 = manager.create_snapshot(context, "import_test2")

        # Both should be created successfully despite internal import
        assert snapshot1 is not None
        assert snapshot2 is not None
        assert len(manager.list_snapshots()) == 2

        # Imports should work for both
        from context.snapshots import ContextSnapshot

        assert isinstance(snapshot1, ContextSnapshot)
        assert isinstance(snapshot2, ContextSnapshot)

    def test_create_snapshot_sequential_creation(self) -> None:
        """Test creating snapshots sequentially maintains correct state."""
        manager = SnapshotManager()
        context = MockContext({"counter": "0"})

        snapshots = []
        for i in range(5):
            snapshot = manager.create_snapshot(context, f"sequential_{i}")
            snapshots.append(snapshot)

            # After each creation, verify state is correct
            assert len(manager.list_snapshots()) == i + 1
            assert f"sequential_{i}" in manager.list_snapshots()

        # Final verification
        assert len(manager.list_snapshots()) == 5
        for i in range(5):
            retrieved = manager.get_snapshot(f"sequential_{i}")
            assert retrieved is snapshots[i]

    def test_create_snapshot_with_complex_context_data(self) -> None:
        """Test creating snapshots with complex context data structures."""
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
        context = MockContext(complex_data)

        # Create snapshot
        snapshot = manager.create_snapshot(context, "complex_context")

        # Should create successfully
        assert snapshot is not None
        assert "complex_context" in manager.list_snapshots()
        retrieved = manager.get_snapshot("complex_context")
        assert retrieved is snapshot

    def test_create_snapshot_error_message_format(self) -> None:
        """Test that duplicate name error has correct message format."""
        manager = SnapshotManager()
        context = MockContext({"key": "value"})

        # Create first snapshot
        manager.create_snapshot(context, "error_test")

        # Test exact error message format
        with pytest.raises(ValueError) as exc_info:
            manager.create_snapshot(context, "error_test")

        error_message = str(exc_info.value)
        assert "Snapshot 'error_test' already exists" == error_message
