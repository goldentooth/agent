"""Flow information data structures for enhanced display."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class FlowInfo:
    """Information about a registered flow for display purposes."""

    name: str
    category: str | None = None
    tags: list[str] | None = None
    metadata: dict[str, Any] | None = None

    @property
    def tags_display(self) -> str:
        """Get tags formatted for display."""
        if not self.tags:
            return ""
        return ", ".join(self.tags)

    @property
    def category_display(self) -> str:
        """Get category formatted for display."""
        return self.category or ""

    def __str__(self) -> str:
        """String representation shows flow name."""
        return self.name

    def to_dict(self) -> dict[str, Any]:
        """Convert FlowInfo to dictionary for JSON serialization."""
        return {
            "name": self.name,
            "category": self.category,
            "tags": self.tags,
            "metadata": self.metadata,
        }
