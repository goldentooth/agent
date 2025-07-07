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
