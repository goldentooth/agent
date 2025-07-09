"""Computed properties management for Context objects."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Callable

if TYPE_CHECKING:
    from .main import Context

from .computed import ComputedProperty
from .dependency_graph import DependencyGraph

# Type aliases
ComputedFunction = Callable[["Context"], Any]
ContextValue = Any


class ComputedPropertiesManager:
    """Manages computed properties for a Context, including caching and dependency tracking."""

    def __init__(self) -> None:
        """Initialize the computed properties manager."""
        super().__init__()
        self._computed_properties: dict[str, ComputedProperty] = {}
        self._dependency_graph: DependencyGraph = DependencyGraph()

    def add_computed_property(
        self,
        key: str,
        func: ComputedFunction,
        dependencies: list[str] | None,
        context: "Context",
    ) -> None:
        """Add a computed property to the manager.

        Args:
            key: The key where the computed value will be accessible
            func: Function that computes the value, takes Context as parameter
            dependencies: List of context keys this property depends on. If None, will track automatically.
            context: The context this property belongs to
        """
        # Create the computed property
        computed_prop = ComputedProperty(func, dependencies)

        # Subscribe the context to the computed property for change notifications
        computed_prop.subscribe(context)

        # Store the computed property
        self._computed_properties[key] = computed_prop

        # Build dependency graph if dependencies are provided
        if dependencies:
            for dep_key in dependencies:
                self._dependency_graph.add_dependency(dep_key, key)

    def remove_computed_property(self, key: str) -> None:
        """Remove a computed property from the manager.

        Args:
            key: The key of the computed property to remove
        """
        if key not in self._computed_properties:
            return

        # Remove from dependency graph
        self._dependency_graph.remove_all_dependencies(key)

        # Remove dependencies where this property is the dependent
        for source_key in self._dependency_graph.get_all_source_keys():
            self._dependency_graph.remove_dependency(source_key, key)

        # Remove the computed property
        del self._computed_properties[key]

    def get_computed_value(self, key: str, context: "Context") -> ContextValue:
        """Get the value of a computed property.

        Args:
            key: The computed property key
            context: The context to compute the value from

        Returns:
            The computed value

        Raises:
            KeyError: If the key is not a computed property
        """
        if key not in self._computed_properties:
            raise KeyError(f"No computed property found for key: {key}")

        return self._computed_properties[key].compute(context)

    def is_computed_property(self, key: str) -> bool:
        """Check if a key represents a computed property.

        Args:
            key: The key to check

        Returns:
            True if the key is a computed property, False otherwise
        """
        return key in self._computed_properties

    def get_all_properties(self) -> dict[str, ComputedProperty]:
        """Get all computed properties in this manager.

        Returns:
            Dictionary mapping property names to ComputedProperty objects (copy)
        """
        return self._computed_properties.copy()

    def invalidate_property(self, key: str) -> None:
        """Invalidate a computed property's cache.

        Args:
            key: The key of the computed property to invalidate
        """
        if key in self._computed_properties:
            self._computed_properties[key].invalidate()

    def invalidate_dependent_properties(self, key: str) -> None:
        """Invalidate computed properties that depend on the given key.

        Args:
            key: The key that was changed, whose dependents should be invalidated
        """
        if self._dependency_graph.has_dependents(key):
            for computed_key in self._dependency_graph.get_dependents(key):
                if computed_key in self._computed_properties:
                    computed_prop = self._computed_properties[computed_key]
                    computed_prop.invalidate()
                    computed_prop.notify_change()

    def handle_property_change(
        self, computed_prop: ComputedProperty, context: "Context"
    ) -> None:
        """Handle when a computed property has changed.

        Args:
            computed_prop: The computed property that has changed
            context: The context the property belongs to
        """
        # Find the key for this computed property
        for key, prop in self._computed_properties.items():
            if prop is computed_prop:
                # Get the old cached value if it exists
                old_value = None
                if prop.is_cached():
                    old_value = prop.get_cached_value()

                # Invalidate the cache to force recomputation
                prop.invalidate()

                # Compute the new value
                new_value = prop.compute(context)

                # Emit change event through context
                emit_change_event = getattr(context, "_emit_change_event", None)
                if emit_change_event:
                    emit_change_event(key, new_value, old_value)

                # Invalidate any computed properties that depend on this one
                self.invalidate_dependent_properties(key)
                break

    def get_keys(self) -> list[str]:
        """Get all computed property keys.

        Returns:
            List of all computed property keys
        """
        return list(self._computed_properties.keys())

    def copy_to_manager(self, other_manager: "ComputedPropertiesManager") -> None:
        """Copy all computed properties to another manager.

        Args:
            other_manager: The target manager to copy properties to
        """
        for key, prop in self._computed_properties.items():
            # Create a new computed property with the same function and dependencies
            other_manager._computed_properties[key] = ComputedProperty(
                prop.func, prop.dependencies.copy()
            )

        # Copy dependency graph
        other_manager._dependency_graph = DependencyGraph()
        for source_key, dependents in self._dependency_graph.get_graph_copy().items():
            for dependent_key in dependents:
                other_manager._dependency_graph.add_dependency(
                    source_key, dependent_key
                )

    def clear(self) -> None:
        """Clear all computed properties and dependencies."""
        self._computed_properties.clear()
        self._dependency_graph.clear()
