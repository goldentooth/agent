"""Tests for SnapshotManager.__init__ method."""

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
        from unittest.mock import Mock

        mock_snapshot = Mock()
        manager1._snapshots["test"] = mock_snapshot  # type: ignore[reportPrivateUsage]
        assert "test" not in manager2._snapshots  # type: ignore[reportPrivateUsage]

    def test_init_attributes_types(self) -> None:
        """Test that SnapshotManager attributes have correct types."""
        manager = SnapshotManager()

        # _snapshots should be a dict
        assert isinstance(manager._snapshots, dict)  # type: ignore[reportPrivateUsage]

        # Should be able to store string keys (snapshot names)
        from unittest.mock import Mock

        mock_snapshot = Mock()
        manager._snapshots["test_name"] = mock_snapshot  # type: ignore[reportPrivateUsage]
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
            SnapshotManager("extra_arg")  # type: ignore[call-arg,reportCallIssue]

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
