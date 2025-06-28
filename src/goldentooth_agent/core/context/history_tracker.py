"""History tracking for Context objects."""

from __future__ import annotations

import time
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    pass

# Type alias for tracked values - contexts can store any type of value
TrackedValue = Any


class ContextChangeEvent:
    """Represents a single change event in context history."""

    def __init__(
        self,
        key: str,
        old_value: TrackedValue,
        new_value: TrackedValue,
        context_id: int,
    ):
        """Create a change event.

        Args:
            key: The key that changed
            old_value: Previous value
            new_value: New value
            context_id: ID of the context that changed
        """
        self.key = key
        self.old_value = old_value
        self.new_value = new_value
        self.context_id = context_id
        self.timestamp = time.time()

    def __repr__(self) -> str:
        """String representation of the change event."""
        return f"ContextChangeEvent(key='{self.key}', {self.old_value} -> {self.new_value}, t={self.timestamp})"


class HistoryTracker:
    """Tracks change history for Context objects."""

    def __init__(self, max_size: int = 1000) -> None:
        """Initialize the history tracker.

        Args:
            max_size: Maximum number of change events to keep
        """
        self._change_history: list[ContextChangeEvent] = []
        self._max_history_size = max_size

    def record_change(
        self,
        key: str,
        old_value: TrackedValue,
        new_value: TrackedValue,
        context_id: int,
    ) -> None:
        """Record a change event in the history.

        Args:
            key: The key that changed
            old_value: Previous value
            new_value: New value
            context_id: ID of the context that changed
        """
        change_event = ContextChangeEvent(key, old_value, new_value, context_id)
        self._change_history.append(change_event)

        # Limit history size to prevent memory issues
        if len(self._change_history) > self._max_history_size:
            # Remove oldest entries, keeping most recent ones
            self._change_history = self._change_history[-self._max_history_size :]

    def get_history(
        self, limit: int | None = None, since: float | None = None
    ) -> list[ContextChangeEvent]:
        """Get the change history.

        Args:
            limit: Maximum number of events to return (most recent first)
            since: Only return events after this timestamp

        Returns:
            List of change events
        """
        history = self._change_history

        # Filter by timestamp if specified
        if since is not None:
            history = [event for event in history if event.timestamp > since]

        # Reverse to get most recent first
        history = list(reversed(history))

        # Apply limit if specified
        if limit is not None:
            history = history[:limit]

        return history

    def clear_history(self) -> None:
        """Clear the change history."""
        self._change_history.clear()

    def get_history_size(self) -> int:
        """Get the current size of the change history."""
        return len(self._change_history)

    def set_max_history_size(self, size: int) -> None:
        """Set the maximum history size.

        Args:
            size: Maximum number of change events to keep

        Raises:
            ValueError: If size is negative
        """
        if size < 0:
            raise ValueError("History size must be non-negative")

        self._max_history_size = size

        # Trim current history if needed
        if len(self._change_history) > size:
            self._change_history = self._change_history[-size:] if size > 0 else []

    def replay_changes_since(self, timestamp: float) -> list[ContextChangeEvent]:
        """Get all changes that occurred since a specific timestamp.

        Args:
            timestamp: Timestamp to get changes since

        Returns:
            List of change events in chronological order
        """
        return [event for event in self._change_history if event.timestamp > timestamp]

    def get_changes_to_reverse(self, timestamp: float) -> list[ContextChangeEvent]:
        """Get changes that need to be reversed for rollback to a timestamp.

        Args:
            timestamp: Target timestamp to rollback to

        Returns:
            List of change events in reverse chronological order (most recent first)
        """
        changes_to_reverse = [
            event
            for event in reversed(self._change_history)
            if event.timestamp > timestamp
        ]
        return changes_to_reverse

    def get_all_history(self) -> list[ContextChangeEvent]:
        """Get all history without filtering or reversing.

        Returns:
            List of all change events in chronological order
        """
        return self._change_history.copy()
