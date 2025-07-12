"""Tests for SnapshotManager.list_snapshots method."""

import time
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


class TestSnapshotManagerListSnapshots:
    """Test suite for SnapshotManager.list_snapshots method."""

    def test_list_snapshots_empty_manager(self) -> None:
        """Test listing snapshots from empty manager."""
        manager = SnapshotManager()

        # Should return empty dict
        snapshots = manager.list_snapshots()
        assert snapshots == {}
        assert isinstance(snapshots, dict)
        assert len(snapshots) == 0

    def test_list_snapshots_single_snapshot(self) -> None:
        """Test listing snapshots with single snapshot."""
        manager = SnapshotManager()
        context = MockContext({"key": "value"})

        # Create single snapshot
        snapshot = manager.create_snapshot(context, "single_test")

        # List should contain one entry
        snapshots = manager.list_snapshots()
        assert len(snapshots) == 1
        assert "single_test" in snapshots
        assert snapshots["single_test"] == snapshot.timestamp

    def test_list_snapshots_multiple_snapshots(self) -> None:
        """Test listing snapshots with multiple snapshots."""
        manager = SnapshotManager()
        contexts = [
            MockContext({"key1": "value1"}),
            MockContext({"key2": "value2"}),
            MockContext({"key3": "value3"}),
        ]
        names = ["snapshot_a", "snapshot_b", "snapshot_c"]

        # Create multiple snapshots
        created_snapshots = []
        for context, name in zip(contexts, names):
            snapshot = manager.create_snapshot(context, name)
            created_snapshots.append(snapshot)

        # List should contain all entries
        snapshots = manager.list_snapshots()
        assert len(snapshots) == 3
        for i, name in enumerate(names):
            assert name in snapshots
            assert snapshots[name] == created_snapshots[i].timestamp

    def test_list_snapshots_returns_dict_name_to_timestamp(self) -> None:
        """Test that list_snapshots returns dict mapping names to timestamps."""
        manager = SnapshotManager()
        context = MockContext({"timestamp": "test"})

        # Create snapshot
        snapshot = manager.create_snapshot(context, "timestamp_test")

        # List should return name -> timestamp mapping
        snapshots = manager.list_snapshots()
        assert isinstance(snapshots, dict)
        assert isinstance(list(snapshots.keys())[0], str)
        assert isinstance(list(snapshots.values())[0], float)
        assert snapshots["timestamp_test"] == snapshot.timestamp

    def test_list_snapshots_different_name_formats(self) -> None:
        """Test listing snapshots with various name formats."""
        manager = SnapshotManager()
        context = MockContext({"format": "test"})

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

        # Create all snapshots and track timestamps
        created_snapshots = {}
        for name in names:
            snapshot = manager.create_snapshot(context, name)
            created_snapshots[name] = snapshot.timestamp

        # List should contain all with correct timestamps
        snapshots = manager.list_snapshots()
        assert len(snapshots) == len(names)
        for name in names:
            assert name in snapshots
            assert snapshots[name] == created_snapshots[name]

    def test_list_snapshots_preserves_order_consistency(self) -> None:
        """Test that list_snapshots maintains consistent ordering."""
        manager = SnapshotManager()
        context = MockContext({"order": "test"})

        # Create snapshots
        names = ["first", "second", "third", "fourth"]
        for name in names:
            manager.create_snapshot(context, name)

        # List multiple times and verify consistency
        list1 = manager.list_snapshots()
        list2 = manager.list_snapshots()
        list3 = manager.list_snapshots()

        assert list1 == list2 == list3
        assert list(list1.keys()) == list(list2.keys()) == list(list3.keys())

    def test_list_snapshots_after_deletion(self) -> None:
        """Test listing snapshots after some deletions."""
        manager = SnapshotManager()
        context = MockContext({"deletion": "test"})

        # Create multiple snapshots
        names = ["keep1", "delete1", "keep2", "delete2", "keep3"]
        created_snapshots = self._create_test_snapshots(manager, context, names)

        # Delete some snapshots
        manager.delete_snapshot("delete1")
        manager.delete_snapshot("delete2")

        # Verify remaining snapshots
        snapshots = manager.list_snapshots()
        self._verify_deletion_results(snapshots, created_snapshots)

    def _create_test_snapshots(
        self, manager: SnapshotManager, context: MockContext, names: list[str]
    ) -> dict[str, float]:
        """Helper method to create test snapshots."""
        created_snapshots = {}
        for name in names:
            snapshot = manager.create_snapshot(context, name)
            created_snapshots[name] = snapshot.timestamp
        return created_snapshots

    def _verify_deletion_results(
        self, snapshots: dict[str, float], created_snapshots: dict[str, float]
    ) -> None:
        """Helper method to verify deletion results."""
        assert len(snapshots) == 3
        assert "keep1" in snapshots
        assert "keep2" in snapshots
        assert "keep3" in snapshots
        assert "delete1" not in snapshots
        assert "delete2" not in snapshots

        # Timestamps should be preserved for remaining snapshots
        assert snapshots["keep1"] == created_snapshots["keep1"]
        assert snapshots["keep2"] == created_snapshots["keep2"]
        assert snapshots["keep3"] == created_snapshots["keep3"]

    def test_list_snapshots_after_clear(self) -> None:
        """Test listing snapshots after clearing all."""
        manager = SnapshotManager()
        context = MockContext({"clear": "test"})

        # Create multiple snapshots
        for i in range(5):
            manager.create_snapshot(context, f"snapshot_{i}")

        # Verify snapshots exist
        assert len(manager.list_snapshots()) == 5

        # Clear all snapshots
        manager.clear_snapshots()

        # List should be empty
        snapshots = manager.list_snapshots()
        assert snapshots == {}
        assert len(snapshots) == 0

    def test_list_snapshots_returns_copy_not_reference(self) -> None:
        """Test that list_snapshots returns a copy, not internal reference."""
        manager = SnapshotManager()
        context = MockContext({"copy": "test"})

        # Create snapshot
        manager.create_snapshot(context, "copy_test")

        # Get list and modify it
        snapshots1 = manager.list_snapshots()
        snapshots1["external_modification"] = 999.999

        # Get list again - should not include external modification
        snapshots2 = manager.list_snapshots()
        assert "external_modification" not in snapshots2
        assert len(snapshots2) == 1
        assert "copy_test" in snapshots2

        # Original list should still have the modification
        assert "external_modification" in snapshots1

    def test_list_snapshots_timestamp_accuracy(self) -> None:
        """Test that list_snapshots returns accurate timestamps."""
        manager = SnapshotManager()
        context = MockContext({"time": "test"})

        # Record time before creation
        before_time = time.time()
        snapshot = manager.create_snapshot(context, "time_test")
        after_time = time.time()

        # List snapshots and check timestamp
        snapshots = manager.list_snapshots()
        listed_timestamp = snapshots["time_test"]

        # Timestamp should match snapshot timestamp
        assert listed_timestamp == snapshot.timestamp

        # Timestamp should be within reasonable range
        assert before_time <= listed_timestamp <= after_time

    def test_list_snapshots_with_sequential_creation(self) -> None:
        """Test listing snapshots created sequentially."""
        manager = SnapshotManager()
        context = MockContext({"sequential": "test"})

        # Create snapshots with small delays
        snapshots_data = []
        for i in range(3):
            snapshot = manager.create_snapshot(context, f"seq_{i}")
            snapshots_data.append((f"seq_{i}", snapshot.timestamp))
            time.sleep(0.01)  # Small delay to ensure different timestamps

        # List snapshots
        listed = manager.list_snapshots()

        # Should contain all snapshots with correct timestamps
        assert len(listed) == 3
        for name, expected_timestamp in snapshots_data:
            assert name in listed
            assert listed[name] == expected_timestamp

        # Timestamps should be in creation order (approximately)
        timestamps = [listed[f"seq_{i}"] for i in range(3)]
        assert timestamps[0] < timestamps[1] < timestamps[2]

    def test_list_snapshots_empty_string_name(self) -> None:
        """Test listing snapshots including one with empty string name."""
        manager = SnapshotManager()
        context = MockContext({"empty": "name"})

        # Create snapshots including empty string name
        names = ["normal", "", "another"]
        for name in names:
            manager.create_snapshot(context, name)

        # List should include all names including empty string
        snapshots = manager.list_snapshots()
        assert len(snapshots) == 3
        assert "normal" in snapshots
        assert "" in snapshots
        assert "another" in snapshots

        # All should have valid timestamps
        for timestamp in snapshots.values():
            assert isinstance(timestamp, float)
            assert timestamp > 0

    def test_list_snapshots_case_sensitivity(self) -> None:
        """Test that list_snapshots preserves case sensitivity."""
        manager = SnapshotManager()
        context = MockContext({"case": "test"})

        # Create snapshots with similar names but different cases
        names = ["Test", "test", "TEST", "tEsT"]
        created_timestamps = {}
        for name in names:
            snapshot = manager.create_snapshot(context, name)
            created_timestamps[name] = snapshot.timestamp

        # List should preserve all case variations
        snapshots = manager.list_snapshots()
        assert len(snapshots) == 4
        for name in names:
            assert name in snapshots
            assert snapshots[name] == created_timestamps[name]

    def test_list_snapshots_after_restore_operations(self) -> None:
        """Test that list_snapshots is unaffected by restore operations."""
        manager = SnapshotManager()
        original_context = MockContext({"original": "data"})
        target_context = MockContext({"target": "data"})

        # Create snapshot
        snapshot = manager.create_snapshot(original_context, "restore_test")
        original_timestamp = snapshot.timestamp

        # List before restore
        before_restore = manager.list_snapshots()

        # Perform multiple restore operations
        manager.restore_snapshot(target_context, "restore_test")
        manager.restore_snapshot(target_context, "restore_test")

        # List after restore
        after_restore = manager.list_snapshots()

        # List should be identical before and after restores
        assert before_restore == after_restore
        assert after_restore["restore_test"] == original_timestamp

    def test_list_snapshots_large_number_of_snapshots(self) -> None:
        """Test listing large number of snapshots."""
        manager = SnapshotManager()
        context = MockContext({"large": "test"})

        # Create many snapshots
        num_snapshots = 100
        expected_names = []
        for i in range(num_snapshots):
            name = f"snapshot_{i:03d}"
            manager.create_snapshot(context, name)
            expected_names.append(name)

        # List all snapshots
        snapshots = manager.list_snapshots()

        # Should contain all snapshots
        assert len(snapshots) == num_snapshots
        for name in expected_names:
            assert name in snapshots
            assert isinstance(snapshots[name], float)

    def test_list_snapshots_with_special_characters(self) -> None:
        """Test listing snapshots with special characters in names."""
        manager = SnapshotManager()
        context = MockContext({"special": "chars"})

        # Names with special characters
        special_names = [
            "name@email.com",
            "path/to/snapshot",
            "query?param=value",
            "fragment#section",
            "encoded%20space",
            "unicode_测试",
            "symbols!@#$%^&*()",
            "brackets[0]",
            "braces{key}",
            "quotes'double\"",
        ]

        # Create snapshots with special names
        created_timestamps = {}
        for name in special_names:
            snapshot = manager.create_snapshot(context, name)
            created_timestamps[name] = snapshot.timestamp

        # List should handle all special characters
        snapshots = manager.list_snapshots()
        assert len(snapshots) == len(special_names)
        for name in special_names:
            assert name in snapshots
            assert snapshots[name] == created_timestamps[name]

    def test_list_snapshots_consistent_with_internal_state(self) -> None:
        """Test that list_snapshots is consistent with internal manager state."""
        manager = SnapshotManager()
        context = MockContext({"consistency": "test"})

        # Create snapshots
        names = ["internal1", "internal2", "internal3"]
        for name in names:
            manager.create_snapshot(context, name)

        # List snapshots
        listed = manager.list_snapshots()

        # Should match internal state size
        assert len(listed) == len(manager._snapshots)

        # All internal snapshots should be in list
        for name in manager._snapshots:
            assert name in listed

        # All listed snapshots should be in internal state
        for name in listed:
            assert name in manager._snapshots

        # Timestamps should match
        for name in listed:
            internal_snapshot = manager._snapshots[name]
            assert listed[name] == internal_snapshot.timestamp
