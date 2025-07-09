"""Snapshot management for Context objects."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .snapshots import ContextSnapshot


class SnapshotManager:
    """Manages snapshots for Context objects."""

    def __init__(self) -> None:
        """Initialize the snapshot manager."""
        super().__init__()
        self._snapshots: dict[str, Any] = {}

    def create_snapshot(self, context: Any, name: str) -> ContextSnapshot:
        """Create a snapshot of the current context state.

        Args:
            context: The context to snapshot
            name: Name/identifier for the snapshot

        Returns:
            The created snapshot

        Raises:
            ValueError: If a snapshot with the same name already exists
        """
        if name in self._snapshots:
            raise ValueError(f"Snapshot '{name}' already exists")

        # Import here to avoid circular import
        from .snapshots import ContextSnapshot

        snapshot = ContextSnapshot(context, name)
        self._snapshots[name] = snapshot
        return snapshot

    def restore_snapshot(self, context: Any, name: str) -> None:
        """Restore the context to a previous snapshot state.

        Args:
            context: The context to restore to
            name: Name of the snapshot to restore

        Raises:
            KeyError: If snapshot with the given name doesn't exist
        """
        if name not in self._snapshots:
            raise KeyError(f"Snapshot '{name}' not found")

        snapshot = self._snapshots[name]
        snapshot.restore_to(context)

    def list_snapshots(self) -> dict[str, float]:
        """List all available snapshots with their timestamps.

        Returns:
            Dictionary mapping snapshot names to their timestamps
        """
        return {name: snapshot.timestamp for name, snapshot in self._snapshots.items()}

    def delete_snapshot(self, name: str) -> None:
        """Delete a snapshot.

        Args:
            name: Name of the snapshot to delete

        Raises:
            KeyError: If snapshot doesn't exist
        """
        if name not in self._snapshots:
            raise KeyError(f"Snapshot '{name}' not found")

        del self._snapshots[name]

    def get_snapshot(self, name: str) -> Any:
        """Get a specific snapshot.

        Args:
            name: Name of the snapshot

        Returns:
            The snapshot

        Raises:
            KeyError: If snapshot doesn't exist
        """
        if name not in self._snapshots:
            raise KeyError(f"Snapshot '{name}' not found")

        return self._snapshots[name]

    def clear_snapshots(self) -> None:
        """Clear all snapshots."""
        self._snapshots.clear()
