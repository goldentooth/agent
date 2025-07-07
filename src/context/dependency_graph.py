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

    def add_dependency(self, source_key: str, dependent_key: str) -> None:
        """Add a dependency relationship.

        Args:
            source_key: The key that is depended upon
            dependent_key: The key that depends on the source
        """
        if source_key not in self._graph:
            self._graph[source_key] = set()
        self._graph[source_key].add(dependent_key)

    def remove_dependency(self, source_key: str, dependent_key: str) -> None:
        """Remove a specific dependency relationship.

        Args:
            source_key: The key that is depended upon
            dependent_key: The key that depends on the source
        """
        if source_key in self._graph:
            self._graph[source_key].discard(dependent_key)
            # Clean up empty sets
            if not self._graph[source_key]:
                del self._graph[source_key]

    def remove_all_dependencies(self, source_key: str) -> None:
        """Remove all dependencies for a source key.

        Args:
            source_key: The key to remove all dependencies for
        """
        if source_key in self._graph:
            del self._graph[source_key]

    def get_dependents(self, source_key: str) -> set[str]:
        """Get all keys that depend on the given source key.

        Args:
            source_key: The key to get dependents for

        Returns:
            Set of dependent keys
        """
        return self._graph.get(source_key, set()).copy()
