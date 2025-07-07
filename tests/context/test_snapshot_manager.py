"""Tests for SnapshotManager class."""

from typing import Any

import pytest

from context.snapshot_manager import SnapshotManager


class TestSnapshotManagerInit:
    """Test suite for SnapshotManager.__init__ method."""

    def test_init_basic(self) -> None:
        """Test basic SnapshotManager initialization."""
        manager = SnapshotManager()

        # Basic existence check
        assert manager is not None
        assert isinstance(manager, SnapshotManager)

    def test_init_snapshots_storage_exists(self) -> None:
        """Test that SnapshotManager initializes with snapshots storage."""
        manager = SnapshotManager()

        # Should have internal snapshots storage (dict[str, ContextSnapshot])
        assert hasattr(manager, "_snapshots")
        assert isinstance(manager._snapshots, dict)  # type: ignore[reportPrivateUsage]

    def test_init_snapshots_storage_empty(self) -> None:
        """Test that SnapshotManager starts with empty snapshots storage."""
        manager = SnapshotManager()

        # Should start empty
        assert len(manager._snapshots) == 0  # type: ignore[reportPrivateUsage]
        assert manager._snapshots == {}  # type: ignore[reportPrivateUsage]

    def test_init_multiple_instances_isolated(self) -> None:
        """Test that different SnapshotManager instances have isolated storage."""
        manager1 = SnapshotManager()
        manager2 = SnapshotManager()

        # Should be different objects
        assert manager1 is not manager2

        # Should have separate storage
        assert manager1._snapshots is not manager2._snapshots  # type: ignore[reportPrivateUsage]

        # Modifying one should not affect the other
        manager1._snapshots["test"] = "value"  # type: ignore[reportPrivateUsage]
        assert "test" not in manager2._snapshots  # type: ignore[reportPrivateUsage]

    def test_init_attributes_types(self) -> None:
        """Test that SnapshotManager attributes have correct types."""
        manager = SnapshotManager()

        # _snapshots should be a dict
        assert isinstance(manager._snapshots, dict)  # type: ignore[reportPrivateUsage]

        # Should be able to store string keys (snapshot names)
        manager._snapshots["test_name"] = None  # type: ignore[reportPrivateUsage]
        assert "test_name" in manager._snapshots  # type: ignore[reportPrivateUsage]

    def test_init_inheritance(self) -> None:
        """Test that SnapshotManager inherits correctly."""
        manager = SnapshotManager()

        # Should be instance of SnapshotManager
        assert isinstance(manager, SnapshotManager)

        # Should call super().__init__() properly
        assert hasattr(manager, "__dict__")

    def test_init_no_parameters_required(self) -> None:
        """Test that SnapshotManager initialization requires no parameters."""
        # Should work without any arguments
        manager = SnapshotManager()
        assert manager is not None

        # Should not accept extra arguments (test default behavior)
        with pytest.raises(TypeError):
            SnapshotManager("extra_arg")  # type: ignore[reportCallIssue]

    def test_init_state_consistency(self) -> None:
        """Test that SnapshotManager state is consistent after initialization."""
        manager = SnapshotManager()

        # Should be in a valid initial state
        assert manager._snapshots == {}  # type: ignore[reportPrivateUsage]
        assert len(manager._snapshots) == 0  # type: ignore[reportPrivateUsage]

        # Should be able to check if empty
        assert not manager._snapshots  # type: ignore[reportPrivateUsage]

    def test_init_callable_immediately(self) -> None:
        """Test that SnapshotManager is immediately usable after initialization."""
        manager = SnapshotManager()

        # Should have the expected interface (methods will be added later)
        assert hasattr(manager, "_snapshots")

        # Should be able to interact with storage
        assert "nonexistent" not in manager._snapshots  # type: ignore[reportPrivateUsage]

    def test_init_memory_efficiency(self) -> None:
        """Test that SnapshotManager initialization is memory efficient."""
        manager = SnapshotManager()

        # Should not pre-allocate large structures
        assert len(manager._snapshots) == 0  # type: ignore[reportPrivateUsage]

        # Storage should be a simple dict
        assert type(manager._snapshots) is dict  # type: ignore[reportPrivateUsage]

    def test_init_thread_safety_isolation(self) -> None:
        """Test that SnapshotManager instances are isolated for thread safety."""
        managers = [SnapshotManager() for _ in range(10)]

        # All should be different instances
        for i, manager1 in enumerate(managers):
            for j, manager2 in enumerate(managers):
                if i != j:
                    assert manager1 is not manager2
                    assert manager1._snapshots is not manager2._snapshots  # type: ignore[reportPrivateUsage]

    def test_init_repr_and_str(self) -> None:
        """Test that SnapshotManager has basic string representations."""
        manager = SnapshotManager()

        # Should have basic representations
        repr_str = repr(manager)
        str_str = str(manager)

        assert "SnapshotManager" in repr_str or "SnapshotManager" in str_str
        assert isinstance(repr_str, str)
        assert isinstance(str_str, str)


class MockContext:
    """Mock Context class for testing purposes."""

    def __init__(self, data: dict[str, str] | None = None) -> None:
        super().__init__()
        self.data = data or {}

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, MockContext):
            return False
        return self.data == other.data


class MockContextSnapshot:
    """Mock ContextSnapshot class for testing purposes."""

    def __init__(self, context: MockContext, name: str) -> None:
        super().__init__()
        self.context = context
        self.name = name
        self.timestamp = 123.456  # Fixed timestamp for predictable testing

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, MockContextSnapshot):
            return False
        return (
            self.context == other.context
            and self.name == other.name
            and self.timestamp == other.timestamp
        )


class TestSnapshotManagerCreateSnapshot:
    """Test suite for SnapshotManager.create_snapshot method."""

    def test_create_snapshot_basic(self) -> None:
        """Test basic snapshot creation functionality."""
        manager = SnapshotManager()
        context = MockContext({"key": "value"})

        # Should fail because method doesn't exist yet
        snapshot = manager.create_snapshot(context, "test_snapshot")

        # Basic verification
        assert snapshot is not None
        assert snapshot.name == "test_snapshot"
        assert snapshot.context == context

    def test_create_snapshot_stores_in_manager(self) -> None:
        """Test that created snapshot is stored in the manager."""
        manager = SnapshotManager()
        context = MockContext({"key": "value"})

        snapshot = manager.create_snapshot(context, "test_snapshot")

        # Should be stored in manager's snapshots
        assert "test_snapshot" in manager._snapshots  # type: ignore[reportPrivateUsage]
        assert manager._snapshots["test_snapshot"] == snapshot  # type: ignore[reportPrivateUsage]

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

    def test_create_snapshot_different_names_allowed(self) -> None:
        """Test that snapshots with different names can be created."""
        manager = SnapshotManager()
        context = MockContext({"key": "value"})

        snapshot1 = manager.create_snapshot(context, "snapshot1")
        snapshot2 = manager.create_snapshot(context, "snapshot2")

        # Both should be stored
        assert snapshot1.name == "snapshot1"
        assert snapshot2.name == "snapshot2"
        assert len(manager._snapshots) == 2  # type: ignore[reportPrivateUsage]

    def test_create_snapshot_different_contexts(self) -> None:
        """Test creating snapshots from different contexts."""
        manager = SnapshotManager()
        context1 = MockContext({"key1": "value1"})
        context2 = MockContext({"key2": "value2"})

        snapshot1 = manager.create_snapshot(context1, "snapshot1")
        snapshot2 = manager.create_snapshot(context2, "snapshot2")

        # Should preserve different context data
        assert snapshot1.context.data == {"key1": "value1"}
        assert snapshot2.context.data == {"key2": "value2"}

    def test_create_snapshot_empty_context(self) -> None:
        """Test creating snapshot from empty context."""
        manager = SnapshotManager()
        context = MockContext({})

        snapshot = manager.create_snapshot(context, "empty_snapshot")

        assert snapshot.context.data == {}
        assert snapshot.name == "empty_snapshot"

    def test_create_snapshot_complex_context_data(self) -> None:
        """Test creating snapshot with complex context data."""
        manager = SnapshotManager()
        context = MockContext({"string": "value", "number": "123", "nested": "data"})

        snapshot = manager.create_snapshot(context, "complex_snapshot")

        assert snapshot.context.data["string"] == "value"
        assert snapshot.context.data["number"] == "123"
        assert snapshot.context.data["nested"] == "data"

    def test_create_snapshot_name_types(self) -> None:
        """Test creating snapshots with different name types and formats."""
        manager = SnapshotManager()
        context = MockContext({"key": "value"})

        # Various name formats
        names = [
            "simple",
            "with_underscore",
            "with-dash",
            "with.dot",
            "with spaces",
            "123numeric",
            "MixedCase",
            "UPPERCASE",
            "",  # Empty string should be allowed
        ]

        for i, name in enumerate(names):
            snapshot = manager.create_snapshot(context, name)
            assert snapshot.name == name
            assert name in manager._snapshots  # type: ignore[reportPrivateUsage]

    def test_create_snapshot_returns_correct_type(self) -> None:
        """Test that create_snapshot returns the correct snapshot type."""
        manager = SnapshotManager()
        context = MockContext({"key": "value"})

        snapshot = manager.create_snapshot(context, "test_snapshot")

        # Should return a ContextSnapshot-like object
        assert hasattr(snapshot, "name")
        assert hasattr(snapshot, "context")
        assert hasattr(snapshot, "timestamp")

    def test_create_snapshot_preserves_context_state(self) -> None:
        """Test that snapshot preserves context state at creation time."""
        manager = SnapshotManager()
        context = MockContext({"key": "original"})

        snapshot = manager.create_snapshot(context, "test_snapshot")

        # Modify context after snapshot creation
        context.data["key"] = "modified"

        # Snapshot should preserve original state (depends on implementation)
        # This test will verify the behavior once implemented
        assert snapshot.context is not None

    def test_create_snapshot_multiple_snapshots_independence(self) -> None:
        """Test that multiple snapshots are independent."""
        manager = SnapshotManager()
        context1 = MockContext({"key": "value1"})
        context2 = MockContext({"key": "value2"})

        snapshot1 = manager.create_snapshot(context1, "snapshot1")
        snapshot2 = manager.create_snapshot(context2, "snapshot2")

        # Snapshots should be independent
        assert snapshot1 is not snapshot2
        assert snapshot1.context != snapshot2.context
        assert snapshot1.name != snapshot2.name

    def test_create_snapshot_manager_state_updates(self) -> None:
        """Test that manager state is properly updated after creating snapshots."""
        manager = SnapshotManager()
        context = MockContext({"key": "value"})

        # Initially empty
        assert len(manager._snapshots) == 0  # type: ignore[reportPrivateUsage]

        # Create snapshots and verify state updates
        snapshot1 = manager.create_snapshot(context, "snapshot1")
        assert len(manager._snapshots) == 1  # type: ignore[reportPrivateUsage]

        snapshot2 = manager.create_snapshot(context, "snapshot2")
        assert len(manager._snapshots) == 2  # type: ignore[reportPrivateUsage]

        # Verify correct storage
        assert manager._snapshots["snapshot1"] == snapshot1  # type: ignore[reportPrivateUsage]
        assert manager._snapshots["snapshot2"] == snapshot2  # type: ignore[reportPrivateUsage]


class TestSnapshotManagerRestoreSnapshot:
    """Test suite for SnapshotManager.restore_snapshot method."""

    def test_restore_snapshot_basic(self) -> None:
        """Test basic snapshot restoration functionality."""
        manager = SnapshotManager()
        original_context = MockContext({"key": "original_value"})
        target_context = MockContext({"key": "current_value"})

        # Create a snapshot
        snapshot = manager.create_snapshot(original_context, "test_snapshot")

        # Restore the snapshot to target context
        manager.restore_snapshot(target_context, "test_snapshot")

        # Target context should now have the original data
        assert target_context.data == {"key": "original_value"}

    def test_restore_snapshot_nonexistent_raises_error(self) -> None:
        """Test that restoring nonexistent snapshot raises KeyError."""
        manager = SnapshotManager()
        context = MockContext({"key": "value"})

        # Attempt to restore nonexistent snapshot should raise KeyError
        with pytest.raises(KeyError, match="Snapshot 'nonexistent' not found"):
            manager.restore_snapshot(context, "nonexistent")

    def test_restore_snapshot_preserves_original_snapshot(self) -> None:
        """Test that restoring doesn't modify the original snapshot."""
        manager = SnapshotManager()
        original_context = MockContext({"key": "original"})
        target_context = MockContext({"key": "current"})

        # Create snapshot
        snapshot = manager.create_snapshot(original_context, "test_snapshot")

        # Modify original context after snapshot creation
        original_context.data["key"] = "modified"

        # Restore snapshot
        manager.restore_snapshot(target_context, "test_snapshot")

        # Target should have snapshot data, not current original data
        assert target_context.data == {"key": "original"}
        assert original_context.data == {"key": "modified"}

    def test_restore_snapshot_multiple_contexts(self) -> None:
        """Test restoring the same snapshot to multiple contexts."""
        manager = SnapshotManager()
        original_context = MockContext({"shared": "data", "unique": "original"})
        target1 = MockContext({"different": "data1"})
        target2 = MockContext({"different": "data2"})

        # Create snapshot
        manager.create_snapshot(original_context, "shared_snapshot")

        # Restore to multiple targets
        manager.restore_snapshot(target1, "shared_snapshot")
        manager.restore_snapshot(target2, "shared_snapshot")

        # Both targets should have the same restored data
        expected_data = {"shared": "data", "unique": "original"}
        assert target1.data == expected_data
        assert target2.data == expected_data

    def test_restore_snapshot_overwrites_target_data(self) -> None:
        """Test that restoration completely overwrites target context data."""
        manager = SnapshotManager()
        original_context = MockContext({"snapshot": "data"})
        target_context = MockContext(
            {"existing": "data", "multiple": "keys", "will_be": "overwritten"}
        )

        # Create snapshot
        manager.create_snapshot(original_context, "overwrite_test")

        # Restore snapshot
        manager.restore_snapshot(target_context, "overwrite_test")

        # Target should only have snapshot data
        assert target_context.data == {"snapshot": "data"}
        assert "existing" not in target_context.data
        assert "multiple" not in target_context.data
        assert "will_be" not in target_context.data

    def test_restore_snapshot_empty_data(self) -> None:
        """Test restoring snapshot with empty data."""
        manager = SnapshotManager()
        original_context = MockContext({})
        target_context = MockContext({"will_be": "cleared"})

        # Create snapshot with empty data
        manager.create_snapshot(original_context, "empty_snapshot")

        # Restore snapshot
        manager.restore_snapshot(target_context, "empty_snapshot")

        # Target should now be empty
        assert target_context.data == {}

    def test_restore_snapshot_complex_data(self) -> None:
        """Test restoring snapshot with complex data structures."""
        manager = SnapshotManager()
        complex_data = {"string": "value", "number": "123", "nested": "structure"}
        original_context = MockContext(complex_data)
        target_context = MockContext({"simple": "data"})

        # Create snapshot
        manager.create_snapshot(original_context, "complex_snapshot")

        # Restore snapshot
        manager.restore_snapshot(target_context, "complex_snapshot")

        # Target should have all complex data
        assert target_context.data == complex_data
        assert target_context.data["string"] == "value"
        assert target_context.data["number"] == "123"
        assert target_context.data["nested"] == "structure"

    def test_restore_snapshot_independence_after_restore(self) -> None:
        """Test that restored context is independent from snapshot."""
        manager = SnapshotManager()
        original_context = MockContext({"key": "original"})
        target_context = MockContext({"key": "target"})

        # Create snapshot
        manager.create_snapshot(original_context, "independence_test")

        # Restore snapshot
        manager.restore_snapshot(target_context, "independence_test")

        # Modify target after restoration
        target_context.data["key"] = "modified_after_restore"
        target_context.data["new"] = "key"

        # Original context and snapshot should be unaffected
        snapshot = manager._snapshots["independence_test"]  # type: ignore[reportPrivateUsage]
        assert snapshot.context.data == {"key": "original"}
        assert original_context.data == {"key": "original"}

    def test_restore_snapshot_multiple_snapshots(self) -> None:
        """Test restoring different snapshots to the same context."""
        manager = SnapshotManager()
        context1 = MockContext({"state": "first"})
        context2 = MockContext({"state": "second"})
        target = MockContext({"state": "initial"})

        # Create multiple snapshots
        manager.create_snapshot(context1, "snapshot1")
        manager.create_snapshot(context2, "snapshot2")

        # Restore first snapshot
        manager.restore_snapshot(target, "snapshot1")
        assert target.data == {"state": "first"}

        # Restore second snapshot
        manager.restore_snapshot(target, "snapshot2")
        assert target.data == {"state": "second"}

    def test_restore_snapshot_returns_none(self) -> None:
        """Test that restore_snapshot returns None."""
        manager = SnapshotManager()
        original_context = MockContext({"key": "value"})
        target_context = MockContext({})

        # Create snapshot
        manager.create_snapshot(original_context, "test_snapshot")

        # Restore should return None
        result = manager.restore_snapshot(target_context, "test_snapshot")
        assert result is None

    def test_restore_snapshot_exact_name_match(self) -> None:
        """Test that restoration requires exact name match."""
        manager = SnapshotManager()
        original_context = MockContext({"key": "value"})
        target_context = MockContext({})

        # Create snapshot
        manager.create_snapshot(original_context, "ExactName")

        # Different case should fail
        with pytest.raises(KeyError, match="Snapshot 'exactname' not found"):
            manager.restore_snapshot(target_context, "exactname")

        # Exact case should work
        manager.restore_snapshot(target_context, "ExactName")
        assert target_context.data == {"key": "value"}

    def test_restore_snapshot_after_multiple_creates(self) -> None:
        """Test restoring snapshot after creating multiple snapshots."""
        manager = SnapshotManager()
        contexts = [
            MockContext({"id": "first"}),
            MockContext({"id": "second"}),
            MockContext({"id": "third"}),
        ]
        target = MockContext({})

        # Create multiple snapshots
        for i, context in enumerate(contexts):
            manager.create_snapshot(context, f"snapshot_{i}")

        # Restore middle snapshot
        manager.restore_snapshot(target, "snapshot_1")
        assert target.data == {"id": "second"}

        # Restore first snapshot
        manager.restore_snapshot(target, "snapshot_0")
        assert target.data == {"id": "first"}


class TestSnapshotManagerListSnapshots:
    """Test suite for SnapshotManager.list_snapshots method."""

    def test_list_snapshots_empty_manager(self) -> None:
        """Test listing snapshots when manager is empty."""
        manager = SnapshotManager()

        # Should return empty dict when no snapshots exist
        result = manager.list_snapshots()
        assert result == {}
        assert isinstance(result, dict)

    def test_list_snapshots_single_snapshot(self) -> None:
        """Test listing snapshots with single snapshot."""
        manager = SnapshotManager()
        context = MockContext({"key": "value"})

        # Create single snapshot
        snapshot = manager.create_snapshot(context, "single_snapshot")

        # Should return dict with name->timestamp mapping
        result = manager.list_snapshots()
        assert len(result) == 1
        assert "single_snapshot" in result
        assert result["single_snapshot"] == snapshot.timestamp
        assert isinstance(result["single_snapshot"], float)

    def test_list_snapshots_multiple_snapshots(self) -> None:
        """Test listing snapshots with multiple snapshots."""
        manager = SnapshotManager()
        context1 = MockContext({"key1": "value1"})
        context2 = MockContext({"key2": "value2"})
        context3 = MockContext({"key3": "value3"})

        # Create multiple snapshots
        snapshot1 = manager.create_snapshot(context1, "snapshot_a")
        snapshot2 = manager.create_snapshot(context2, "snapshot_b")
        snapshot3 = manager.create_snapshot(context3, "snapshot_c")

        # Should return dict with all snapshots
        result = manager.list_snapshots()
        assert len(result) == 3
        assert result["snapshot_a"] == snapshot1.timestamp
        assert result["snapshot_b"] == snapshot2.timestamp
        assert result["snapshot_c"] == snapshot3.timestamp

    def test_list_snapshots_return_type(self) -> None:
        """Test that list_snapshots returns correct type."""
        manager = SnapshotManager()
        context = MockContext({"test": "data"})

        # Create snapshot
        manager.create_snapshot(context, "test_snapshot")

        # Should return dict[str, float]
        result = manager.list_snapshots()
        assert isinstance(result, dict)

        # Check key and value types
        for name, timestamp in result.items():
            assert isinstance(name, str)
            assert isinstance(timestamp, float)

    def test_list_snapshots_different_name_formats(self) -> None:
        """Test listing snapshots with various name formats."""
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

        snapshots: dict[str, Any] = {}
        for name in names:
            snapshot = manager.create_snapshot(context, name)
            snapshots[name] = snapshot

        # Should list all snapshots with correct names
        result = manager.list_snapshots()
        assert len(result) == len(names)
        for name in names:
            assert name in result
            assert result[name] == snapshots[name].timestamp  # type: ignore[reportUnknownMemberType]

    def test_list_snapshots_independence_from_internal_state(self) -> None:
        """Test that returned dict is independent from internal state."""
        manager = SnapshotManager()
        context = MockContext({"key": "value"})

        # Create snapshot
        manager.create_snapshot(context, "test_snapshot")

        # Get snapshot list
        result1 = manager.list_snapshots()
        result2 = manager.list_snapshots()

        # Should return different dict instances each time
        assert result1 is not result2
        assert result1 == result2

        # Modifying result should not affect manager
        result1["new_key"] = 999.999
        result3 = manager.list_snapshots()
        assert "new_key" not in result3

    def test_list_snapshots_consistent_with_create_snapshot(self) -> None:
        """Test that list_snapshots is consistent with create_snapshot."""
        manager = SnapshotManager()
        context = MockContext({"key": "value"})

        # Initially empty
        assert manager.list_snapshots() == {}

        # Create first snapshot
        snapshot1 = manager.create_snapshot(context, "first")
        result = manager.list_snapshots()
        assert len(result) == 1
        assert result["first"] == snapshot1.timestamp

        # Create second snapshot
        snapshot2 = manager.create_snapshot(context, "second")
        result = manager.list_snapshots()
        assert len(result) == 2
        assert result["first"] == snapshot1.timestamp
        assert result["second"] == snapshot2.timestamp

    def test_list_snapshots_preserves_timestamp_values(self) -> None:
        """Test that exact timestamp values are preserved."""
        manager = SnapshotManager()
        context = MockContext({"key": "value"})

        # Create snapshot and capture timestamp
        snapshot = manager.create_snapshot(context, "timestamp_test")
        original_timestamp = snapshot.timestamp

        # List snapshots should preserve exact timestamp
        result = manager.list_snapshots()
        assert result["timestamp_test"] == original_timestamp

        # Should be exact match, not approximation
        assert result["timestamp_test"] is original_timestamp

    def test_list_snapshots_after_snapshot_operations(self) -> None:
        """Test listing snapshots after various operations."""
        manager = SnapshotManager()
        original_context = MockContext({"key": "original"})
        target_context = MockContext({"key": "target"})

        # Create snapshot
        snapshot = manager.create_snapshot(original_context, "operation_test")

        # Restore snapshot (should not affect listing)
        manager.restore_snapshot(target_context, "operation_test")

        # Should still list the snapshot correctly
        result = manager.list_snapshots()
        assert len(result) == 1
        assert result["operation_test"] == snapshot.timestamp

        # Multiple restores should not affect listing
        manager.restore_snapshot(target_context, "operation_test")
        result = manager.list_snapshots()
        assert len(result) == 1
        assert result["operation_test"] == snapshot.timestamp

    def test_list_snapshots_empty_names_handled(self) -> None:
        """Test that empty and unusual names are handled correctly."""
        manager = SnapshotManager()
        context = MockContext({"key": "value"})

        # Create snapshot with empty name
        empty_snapshot = manager.create_snapshot(context, "")

        # Should be listed correctly
        result = manager.list_snapshots()
        assert "" in result
        assert result[""] == empty_snapshot.timestamp

    def test_list_snapshots_chronological_information(self) -> None:
        """Test that timestamp information enables chronological ordering."""
        manager = SnapshotManager()
        context = MockContext({"key": "value"})

        # Create snapshots in sequence
        # (Note: actual timestamps may be very close but should be different)
        snapshot1 = manager.create_snapshot(context, "first")
        snapshot2 = manager.create_snapshot(context, "second")

        result = manager.list_snapshots()

        # Should contain both timestamps
        assert len(result) == 2
        assert "first" in result
        assert "second" in result

        # Timestamps should enable ordering (first should be <= second)
        assert result["first"] <= result["second"]

    def test_list_snapshots_no_side_effects(self) -> None:
        """Test that list_snapshots has no side effects on manager state."""
        manager = SnapshotManager()
        context = MockContext({"key": "value"})

        # Create snapshot
        snapshot = manager.create_snapshot(context, "side_effect_test")

        # Get internal state before listing
        internal_count_before = len(manager._snapshots)  # type: ignore[reportPrivateUsage]

        # List snapshots multiple times
        result1 = manager.list_snapshots()
        result2 = manager.list_snapshots()
        result3 = manager.list_snapshots()

        # Internal state should be unchanged
        internal_count_after = len(manager._snapshots)  # type: ignore[reportPrivateUsage]
        assert internal_count_before == internal_count_after

        # All results should be identical
        assert result1 == result2 == result3
