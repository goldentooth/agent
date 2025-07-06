"""FlowRegistry class for managing Flow objects."""

import threading
from typing import Any, Dict, List, Optional, Union

from ..exceptions import FlowError
from ..flow import Flow

# Type alias for flows with any input/output types
AnyFlow = Flow[Any, Any]

# Sentinel value for optional parameter detection
_MISSING = object()


class FlowRegistryError(FlowError):
    """Exception raised by FlowRegistry operations."""

    pass


class FlowRegistry(object):
    """A thread-safe registry for Flow objects.

    Provides centralized management of Flow objects with support for:
    - Name-based registration and retrieval
    - Category-based organization
    - Tag-based classification
    - Metadata storage and search
    - Thread-safe concurrent operations
    """

    def __init__(self):
        """Initialize empty registry with thread safety."""
        super().__init__()
        self._flows: Dict[str, AnyFlow] = {}
        self._categories: Dict[str, List[str]] = {}
        self._tags: Dict[str, List[str]] = {}
        self._metadata: Dict[str, Dict[str, Any]] = {}
        self._lock = threading.Lock()

    def register(
        self,
        name: str,
        flow: AnyFlow,
        category: Optional[str] = None,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Register a flow with the registry."""
        if not name:
            raise FlowRegistryError("Flow name cannot be empty")

        if not isinstance(flow, Flow):  # type: ignore
            raise FlowRegistryError("Flow must be an instance of Flow")

        with self._lock:
            if name in self._flows:
                raise FlowRegistryError(f"Flow '{name}' already exists")

            # Register the flow
            self._flows[name] = flow

            # Add to category if provided
            if category:
                if category not in self._categories:
                    self._categories[category] = []
                self._categories[category].append(name)

            # Add to tags if provided
            if tags:
                for tag in tags:
                    if tag not in self._tags:
                        self._tags[tag] = []
                    self._tags[tag].append(name)

            # Store metadata if provided
            if metadata is not None:
                self._metadata[name] = metadata.copy()

    def unregister(self, name: str) -> None:
        """Remove a flow from the registry."""
        with self._lock:
            if name not in self._flows:
                raise FlowRegistryError(f"Flow '{name}' not found")

            # Remove from flows
            del self._flows[name]

            # Remove from categories
            for category_flows in self._categories.values():
                if name in category_flows:
                    category_flows.remove(name)

            # Remove from tags
            for tag_flows in self._tags.values():
                if name in tag_flows:
                    tag_flows.remove(name)

            # Remove metadata
            if name in self._metadata:
                del self._metadata[name]

    def get(self, name: str, default: Any = _MISSING) -> Optional[AnyFlow]:
        """Get a flow by name."""
        with self._lock:
            if name in self._flows:
                return self._flows[name]
            elif default is not _MISSING:  # Default was explicitly provided
                return default
            else:
                raise FlowRegistryError(f"Flow '{name}' not found")

    def list(
        self, category: Optional[str] = None, tags: Optional[List[str]] = None
    ) -> List[str]:
        """List flow names, optionally filtered by category or tags.

        Args:
            category: Filter by category name. Takes precedence over tags.
            tags: Filter by tags (flows must have ALL specified tags).

        Note: If both category and tags are provided, category takes precedence
        and tags are ignored.
        """
        with self._lock:
            if category is not None:
                return self._categories.get(category, []).copy()
            elif tags is not None:
                if not tags:
                    return list(self._flows.keys())

                # Find flows that have ALL specified tags
                result_flows = None
                for tag in tags:
                    tag_flows = set(self._tags.get(tag, []))
                    if result_flows is None:
                        result_flows = tag_flows
                    else:
                        result_flows = result_flows.intersection(tag_flows)

                return list(result_flows) if result_flows else []
            else:
                return list(self._flows.keys())

    def search(self, query: str) -> List[str]:
        """Search flows by name or metadata."""
        if not query:
            return self.list()

        with self._lock:
            results: List[str] = []
            query_lower = query.lower()

            for name in self._flows.keys():
                # Search in name
                if query_lower in name.lower():
                    results.append(name)
                    continue

                # Search in metadata
                metadata = self._metadata.get(name, {})
                for value in metadata.values():
                    if isinstance(value, str) and query_lower in value.lower():
                        results.append(name)
                        break

            return results

    def clear(self, category: Optional[str] = None) -> None:
        """Clear all flows or flows from a specific category."""
        with self._lock:
            if category is None:
                # Clear everything
                self._flows.clear()
                self._categories.clear()
                self._tags.clear()
                self._metadata.clear()
            else:
                # Clear specific category
                if category in self._categories:
                    flow_names = self._categories[category].copy()

                    for name in flow_names:
                        # Remove from flows
                        if name in self._flows:
                            del self._flows[name]

                        # Remove from tags
                        for tag_flows in self._tags.values():
                            if name in tag_flows:
                                tag_flows.remove(name)

                        # Remove metadata
                        if name in self._metadata:
                            del self._metadata[name]

                    # Remove the category entirely
                    del self._categories[category]

    @property
    def flows(self) -> Dict[str, AnyFlow]:
        """Get read-only view of all flows."""
        with self._lock:
            return self._flows.copy()

    @property
    def categories(self) -> Dict[str, List[str]]:
        """Get read-only view of all categories."""
        with self._lock:
            return {k: v.copy() for k, v in self._categories.items()}

    @property
    def tags(self) -> Dict[str, List[str]]:
        """Get read-only view of all tags."""
        with self._lock:
            return {k: v.copy() for k, v in self._tags.items()}

    @property
    def metadata(self) -> Dict[str, Dict[str, Any]]:
        """Get read-only view of all metadata."""
        with self._lock:
            return {k: v.copy() for k, v in self._metadata.items()}


# Global flow registry instance
flow_registry = FlowRegistry()


# Convenience functions
def register_flow(name: str, flow: AnyFlow, category: str | None = None) -> AnyFlow:
    """Register a flow in the global registry.

    Args:
        name: Unique name for the flow
        flow: Flow instance to register
        category: Optional category for organization

    Returns:
        The registered flow (for chaining)
    """
    flow_registry.register(name, flow, category)
    return flow


def get_flow(name: str) -> AnyFlow | None:
    """Get a flow from the global registry.

    Args:
        name: Name of the flow to retrieve

    Returns:
        Flow instance or None if not found
    """
    return flow_registry.get(name)


def list_flows(category: str | None = None) -> list[str]:
    """List flows in the global registry.

    Args:
        category: Optional category to filter by

    Returns:
        List of flow names
    """
    return flow_registry.list_flows(category)
