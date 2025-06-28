"""Flow registry for discoverability and reuse.

This module provides a global registry for named flows, enabling
easy discovery and reuse across applications.
"""

from collections.abc import Callable
from typing import Any, TypeVar

from .main import Flow

Input = TypeVar("Input")
Output = TypeVar("Output")

# Type aliases for generic flow storage
AnyFlow = Flow[Any, Any]
FlowInfo = dict[str, Any]


class FlowRegistry:
    """Registry for named flows with discovery and introspection capabilities."""

    def __init__(self) -> None:
        self._flows: dict[str, AnyFlow] = {}
        self._categories: dict[str, list[str]] = {}

    def register(
        self, name: str, flow: AnyFlow, category: str | None = None
    ) -> AnyFlow:
        """Register a flow with the given name.

        Args:
            name: Unique name for the flow
            flow: Flow instance to register
            category: Optional category for organization

        Returns:
            The registered flow (for chaining)
        """
        self._flows[name] = flow

        if category:
            if category not in self._categories:
                self._categories[category] = []
            if name not in self._categories[category]:
                self._categories[category].append(name)

        return flow

    def get(self, name: str) -> AnyFlow | None:
        """Get a flow by name.

        Args:
            name: Name of the flow to retrieve

        Returns:
            Flow instance or None if not found
        """
        return self._flows.get(name)

    def list_flows(self, category: str | None = None) -> list[str]:
        """List all registered flow names.

        Args:
            category: Optional category to filter by

        Returns:
            List of flow names
        """
        if category:
            return self._categories.get(category, [])
        return list(self._flows.keys())

    def list_categories(self) -> list[str]:
        """List all categories.

        Returns:
            List of category names
        """
        return list(self._categories.keys())

    def search(self, query: str) -> list[str]:
        """Search for flows by name or metadata.

        Args:
            query: Search query (substring match)

        Returns:
            List of matching flow names
        """
        query_lower = query.lower()
        matches = []

        for name, flow in self._flows.items():
            # Check name
            if query_lower in name.lower():
                matches.append(name)
                continue

            # Check metadata
            if hasattr(flow, "metadata"):
                for key, value in flow.metadata.items():
                    if (
                        query_lower in str(key).lower()
                        or query_lower in str(value).lower()
                    ):
                        matches.append(name)
                        break

        return matches

    def remove(self, name: str) -> bool:
        """Remove a flow from the registry.

        Args:
            name: Name of the flow to remove

        Returns:
            True if removed, False if not found
        """
        if name in self._flows:
            del self._flows[name]

            # Remove from categories
            for category_flows in self._categories.values():
                if name in category_flows:
                    category_flows.remove(name)

            return True
        return False

    def clear(self, category: str | None = None) -> None:
        """Clear flows from registry.

        Args:
            category: Optional category to clear, or None to clear all
        """
        if category:
            if category in self._categories:
                for name in self._categories[category]:
                    self._flows.pop(name, None)
                del self._categories[category]
        else:
            self._flows.clear()
            self._categories.clear()

    def info(self, name: str) -> FlowInfo | None:
        """Get detailed information about a flow.

        Args:
            name: Name of the flow

        Returns:
            Dictionary with flow information or None if not found
        """
        flow = self._flows.get(name)
        if not flow:
            return None

        # Find categories
        categories = []
        for cat, flows in self._categories.items():
            if name in flows:
                categories.append(cat)

        return {
            "name": name,
            "flow_name": flow.name,
            "function_name": getattr(flow.fn, "__name__", "anonymous"),
            "metadata": getattr(flow, "metadata", {}),
            "categories": categories,
            "repr": repr(flow),
        }

    def print_registry(self) -> None:
        """Print a formatted view of the registry."""
        print("🗂️  Flow Registry")
        print("=" * 40)

        if not self._flows:
            print("(empty)")
            return

        # Print by categories
        for category in sorted(self._categories.keys()):
            print(f"\n📁 {category}:")
            for name in sorted(self._categories[category]):
                flow = self._flows[name]
                print(f"  • {name} ({flow.name})")

        # Print uncategorized
        categorized_flows = set()
        for flows in self._categories.values():
            categorized_flows.update(flows)

        uncategorized = [
            name for name in self._flows.keys() if name not in categorized_flows
        ]
        if uncategorized:
            print("\n📄 Uncategorized:")
            for name in sorted(uncategorized):
                flow = self._flows[name]
                print(f"  • {name} ({flow.name})")


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
    return flow_registry.register(name, flow, category)


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


def search_flows(query: str) -> list[str]:
    """Search flows in the global registry.

    Args:
        query: Search query

    Returns:
        List of matching flow names
    """
    return flow_registry.search(query)


# Decorator for registering flows
def registered_flow(
    name: str, category: str | None = None
) -> Callable[[AnyFlow], AnyFlow]:
    """Decorator to register a flow in the global registry.

    Args:
        name: Unique name for the flow
        category: Optional category for organization

    Example:
        @registered_flow("text_processor", "nlp")
        @Flow.from_sync_fn
        def process_text(text):
            return text.upper()
    """

    def decorator(flow: AnyFlow) -> AnyFlow:
        return register_flow(name, flow, category)

    return decorator
