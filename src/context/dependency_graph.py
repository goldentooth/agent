"""Dependency graph management for Context computed properties."""

from __future__ import annotations


class DependencyGraph:
    """Manages dependency relationships between context keys and computed properties."""

    def __init__(self) -> None:
        """Initialize the dependency graph."""
        super().__init__()
        self._graph: dict[str, set[str]] = {}

    def get_internal_graph_for_testing(self) -> dict[str, set[str]]:
        """Get the internal graph structure for testing purposes."""
        return self._graph
