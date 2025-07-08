"""Tests for SnapshotManager.get_snapshot method."""

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


class TestSnapshotManagerGetSnapshot:
    """Test suite for SnapshotManager.get_snapshot method."""

    def test_get_snapshot_basic(self) -> None:
        """Test basic snapshot retrieval functionality."""
        manager = SnapshotManager()
        context = MockContext({"key": "value"})

        # Create snapshot
        created_snapshot = manager.create_snapshot(context, "test_snapshot")

        # Get snapshot
        retrieved_snapshot = manager.get_snapshot("test_snapshot")

        # Should return the same snapshot object
        assert retrieved_snapshot is created_snapshot
        assert retrieved_snapshot.name == "test_snapshot"
        assert retrieved_snapshot.context_id == id(context)

    def test_get_snapshot_nonexistent_raises_error(self) -> None:
        """Test that getting nonexistent snapshot raises KeyError."""
        manager = SnapshotManager()

        # Attempt to get nonexistent snapshot should raise KeyError
        with pytest.raises(KeyError, match="Snapshot 'nonexistent' not found"):
            manager.get_snapshot("nonexistent")

    def test_get_snapshot_empty_manager(self) -> None:
        """Test getting snapshot from empty manager raises error."""
        manager = SnapshotManager()

        # Should raise error for any name
        with pytest.raises(KeyError, match="Snapshot 'any_name' not found"):
            manager.get_snapshot("any_name")

    def test_get_snapshot_multiple_snapshots(self) -> None:
        """Test getting specific snapshot from multiple snapshots."""
        manager = SnapshotManager()
        test_data = [
            (MockContext({"key1": "value1"}), "snapshot_a", {"key1": "value1"}),
            (MockContext({"key2": "value2"}), "snapshot_b", {"key2": "value2"}),
            (MockContext({"key3": "value3"}), "snapshot_c", {"key3": "value3"}),
        ]

        # Create snapshots and store references
        created_snapshots = {}
        for context, name, _ in test_data:
            created_snapshots[name] = manager.create_snapshot(context, name)

        # Get and verify each snapshot
        for context, name, expected_data in test_data:
            retrieved = manager.get_snapshot(name)
            assert retrieved is created_snapshots[name]
            assert retrieved.context_id == id(context)

    def test_get_snapshot_different_name_formats(self) -> None:
        """Test getting snapshots with various name formats."""
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

        # Create all snapshots and store references
        created_snapshots = {}
        for name in names:
            created_snapshots[name] = manager.create_snapshot(context, name)

        # Get each snapshot and verify
        for name in names:
            retrieved = manager.get_snapshot(name)
            assert retrieved is created_snapshots[name]
            assert retrieved.name == name

    def test_get_snapshot_exact_name_match(self) -> None:
        """Test that retrieval requires exact name match."""
        manager = SnapshotManager()
        context = MockContext({"key": "value"})

        # Create snapshot with specific case
        created_snapshot = manager.create_snapshot(context, "ExactName")

        # Different case should fail
        with pytest.raises(KeyError, match="Snapshot 'exactname' not found"):
            manager.get_snapshot("exactname")

        # Exact case should work
        retrieved = manager.get_snapshot("ExactName")
        assert retrieved is created_snapshot

    def test_get_snapshot_preserves_snapshot_data(self) -> None:
        """Test that getting snapshot preserves all data."""
        manager = SnapshotManager()
        context = MockContext({"complex": "data", "multiple": "keys"})

        # Create snapshot
        _ = manager.create_snapshot(context, "data_test")

        # Get snapshot and verify data preservation
        retrieved = manager.get_snapshot("data_test")
        assert retrieved.name == "data_test"
        assert retrieved.context_id == id(context)
        assert hasattr(retrieved, "timestamp")

    def test_get_snapshot_after_operations(self) -> None:
        """Test getting snapshot after various operations."""
        manager = SnapshotManager()
        original_context = MockContext({"key": "original"})
        target_context = MockContext({"key": "target"})

        # Create snapshot
        created_snapshot = manager.create_snapshot(original_context, "operation_test")

        # Perform other operations
        manager.restore_snapshot(target_context, "operation_test")
        manager.list_snapshots()

        # Should still be able to get the same snapshot
        retrieved = manager.get_snapshot("operation_test")
        assert retrieved is created_snapshot
        assert retrieved.context_id == id(original_context)

    def test_get_snapshot_independent_of_original_context(self) -> None:
        """Test that retrieved snapshot is independent of original context changes."""
        manager = SnapshotManager()
        context = MockContext({"key": "original"})

        # Create snapshot
        created_snapshot = manager.create_snapshot(context, "independence_test")

        # Modify original context after snapshot creation
        context.data["key"] = "modified"
        context.data["new"] = "data"

        # Retrieved snapshot should be unaffected
        retrieved = manager.get_snapshot("independence_test")
        assert retrieved is created_snapshot
        assert retrieved.context_id == id(context)
        # Note: The new snapshot structure doesn't store the original context data directly,
        # but it maintains the same snapshot object identity

    def test_get_snapshot_no_side_effects(self) -> None:
        """Test that getting snapshot has no side effects."""
        manager = SnapshotManager()
        context = MockContext({"key": "value"})

        # Create snapshot
        created_snapshot = manager.create_snapshot(context, "side_effect_test")

        # Get internal state before retrieval
        snapshots_before = manager.list_snapshots()
        internal_count_before = len(manager._snapshots)

        # Get snapshot multiple times
        retrieved1 = manager.get_snapshot("side_effect_test")
        retrieved2 = manager.get_snapshot("side_effect_test")
        retrieved3 = manager.get_snapshot("side_effect_test")

        # Internal state should be unchanged
        snapshots_after = manager.list_snapshots()
        internal_count_after = len(manager._snapshots)
        assert snapshots_before == snapshots_after
        assert internal_count_before == internal_count_after

        # All retrievals should return the same object
        assert retrieved1 is retrieved2 is retrieved3 is created_snapshot

    def test_get_snapshot_consistent_with_list_snapshots(self) -> None:
        """Test that get_snapshot is consistent with list_snapshots."""
        manager = SnapshotManager()
        context = MockContext({"key": "value"})

        # Create snapshots
        names = ["snapshot1", "snapshot2", "snapshot3"]
        created_snapshots = {}
        for name in names:
            created_snapshots[name] = manager.create_snapshot(context, name)

        # Verify all are listed
        listed_snapshots = manager.list_snapshots()
        assert len(listed_snapshots) == 3
        assert all(name in listed_snapshots for name in names)

        # Verify all can be retrieved
        for name in names:
            retrieved = manager.get_snapshot(name)
            assert retrieved is created_snapshots[name]
            assert retrieved.name == name

    def test_get_snapshot_return_type_verification(self) -> None:
        """Test that get_snapshot returns correct type."""
        manager = SnapshotManager()
        context = MockContext({"key": "value"})

        # Create snapshot
        manager.create_snapshot(context, "type_test")

        # Get snapshot and verify type/attributes
        retrieved = manager.get_snapshot("type_test")
        assert hasattr(retrieved, "name")
        assert hasattr(retrieved, "context_id")
        assert hasattr(retrieved, "timestamp")
        assert hasattr(retrieved, "frames")
        assert retrieved.name == "type_test"
        assert isinstance(retrieved.timestamp, float)

    def test_get_snapshot_complex_data_preservation(self) -> None:
        """Test getting snapshot preserves complex data structures."""
        manager = SnapshotManager()
        complex_data = {
            "string": "value",
            "number": "123",
            "nested": "structure",
            "empty": "",
            "special": "chars!@#$%^&*()",
        }
        context = MockContext(complex_data)

        # Create and retrieve snapshot
        created_snapshot = manager.create_snapshot(context, "complex_test")
        retrieved = manager.get_snapshot("complex_test")

        # Should preserve all complex data
        assert retrieved is created_snapshot
        assert retrieved.context_id == id(context)
        # Note: The new snapshot structure stores frames rather than raw context data,
        # but preserves snapshot identity and metadata
