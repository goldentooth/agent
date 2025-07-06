"""FlowRegistry class for managing Flow objects."""

import json
import threading
from typing import Any, Dict, List, Literal, Optional, Union

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

    def to_dict(self) -> Dict[str, Any]:
        """Export registry contents to dictionary format.

        Returns:
            Dictionary containing registry structure and metadata
        """
        with self._lock:
            return {
                "flows": {
                    name: {
                        "name": name,
                        "flow_name": flow.name,
                        "function_name": getattr(flow.fn, "__name__", "anonymous"),
                        "repr": repr(flow),
                    }
                    for name, flow in self._flows.items()
                },
                "categories": self._categories.copy(),
                "tags": self._tags.copy(),
                "metadata": {k: v.copy() for k, v in self._metadata.items()},
                "stats": {
                    "total_flows": len(self._flows),
                    "total_categories": len(self._categories),
                    "total_tags": len(self._tags),
                },
            }

    def from_dict(self, data: Dict[str, Any]) -> None:
        """Import registry structure from dictionary format.

        Args:
            data: Dictionary containing registry data

        Note:
            This function only imports metadata, categories, and tags.
            Flow objects cannot be deserialized and must be re-registered.
        """
        with self._lock:
            # Clear existing registry (direct access to avoid deadlock)
            self._flows.clear()
            self._categories.clear()
            self._tags.clear()
            self._metadata.clear()

            # Import metadata only (flows cannot be reconstructed)
            for name, metadata in data.get("metadata", {}).items():
                if name in data.get("flows", {}):
                    self._metadata[name] = metadata.copy()

            # Import categories and tags structure (without actual flows)
            for category in data.get("categories", {}):
                self._categories[category] = []

            for tag in data.get("tags", {}):
                self._tags[tag] = []


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
    return flow_registry.get(name, None)


def list_flows(category: str | None = None) -> list[str]:
    """List flows in the global registry.

    Args:
        category: Optional category to filter by

    Returns:
        List of flow names
    """
    return flow_registry.list(category)


def search_flows(query: str) -> list[str]:
    """Search flows in the global registry.

    Args:
        query: Search query

    Returns:
        List of matching flow names
    """
    return flow_registry.search(query)


def unregister_flow(name: str) -> None:
    """Remove a flow from the global registry.

    Args:
        name: Name of the flow to remove

    Raises:
        FlowRegistryError: If flow is not found
    """
    flow_registry.unregister(name)


def clear_registry(category: str | None = None) -> None:
    """Clear flows from the global registry.

    Args:
        category: Optional category to clear, or None to clear all flows
    """
    flow_registry.clear(category)


def export_registry(format: Literal["json"] = "json") -> str:
    """Export registry contents to a serialized format.

    Args:
        format: Export format, currently only "json" is supported

    Returns:
        Serialized registry data as string

    Raises:
        ValueError: If format is not supported
    """
    if format == "json":
        data = flow_registry.to_dict()
        return json.dumps(data, indent=2)
    else:
        raise ValueError(f"Unsupported export format: {format}")


def import_registry(data: str | Dict[str, Any]) -> None:
    """Import registry contents from serialized data.

    Args:
        data: JSON string or dictionary containing registry data

    Raises:
        ValueError: If data format is invalid
        FlowRegistryError: If import operation fails

    Note:
        This function only imports metadata, categories, and tags.
        Flow objects cannot be deserialized and must be re-registered.
    """
    if isinstance(data, str):
        try:
            parsed_data = json.loads(data)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON data: {e}")
    else:
        parsed_data = data

    # Validate data structure
    required_keys = ["flows", "categories", "tags", "metadata"]
    if not all(key in parsed_data for key in required_keys):
        raise ValueError(f"Missing required keys. Expected: {required_keys}")

    # Use the registry's from_dict method
    flow_registry.from_dict(parsed_data)
