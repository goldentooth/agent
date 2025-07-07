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
    ) -> None:
        """Create a change event.

        Args:
            key: The key that changed
            old_value: Previous value
            new_value: New value
            context_id: ID of the context that changed
        """
        super().__init__()
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
        super().__init__()
        self._change_history: list[ContextChangeEvent] = []
        self._max_history_size = max_size
