"""Main Context system implementation."""

from __future__ import annotations

import time
from typing import TYPE_CHECKING, Any
from weakref import WeakSet

if TYPE_CHECKING:
    pass

# Type aliases for context system
ContextValue = Any
ComputedFunction = Any


class ContextSnapshot:
    """Represents a snapshot of context state at a specific point in time."""

    def __init__(self, context: Any, name: str) -> None:
        """Create a snapshot of the current context state.

        Args:
            context: The context to snapshot
            name: Name/identifier for this snapshot
        """
        super().__init__()
        self.name = name
        self.timestamp = time.time()

        # Deep copy the frames to preserve state
        self.frames = (
            [frame.copy() for frame in context.frames]
            if hasattr(context, "frames")
            else []
        )

        # Store computed property definitions (but not cached values)
        self.computed_properties: dict[str, dict[str, Any]] = {}
        if hasattr(context, "_computed_properties"):
            for key, prop in context._computed_properties.items():  # type: ignore[reportUnknownMemberType]
                self.computed_properties[key] = {
                    "func": prop.func,  # type: ignore[reportUnknownMemberType]
                    "dependencies": prop.dependencies.copy(),  # type: ignore[reportUnknownMemberType]
                }

        # Store transformations
        self.transformations: dict[str, list[Any]] = {}
        if hasattr(context, "_transformations"):
            for key, transforms in context._transformations.items():  # type: ignore[reportUnknownMemberType]
                self.transformations[key] = [t.func for t in transforms]  # type: ignore[reportUnknownMemberType]

        # Store metadata
        self.context_id = id(context)

    def restore_to(self, context: Any) -> None:
        """Restore this snapshot to the given context.

        Args:
            context: The context to restore to
        """
        # Clear current state
        if hasattr(context, "frames"):
            context.frames.clear()
        if hasattr(context, "_computed_properties"):
            context._computed_properties.clear()  # type: ignore[reportUnknownMemberType]
        if hasattr(context, "_transformations"):
            context._transformations.clear()  # type: ignore[reportUnknownMemberType]
        if hasattr(context, "_dependency_graph"):
            context._dependency_graph.clear()  # type: ignore[reportUnknownMemberType]
        if hasattr(context, "_sync_events"):
            context._sync_events.clear()  # type: ignore[reportUnknownMemberType]
        if hasattr(context, "_async_events"):
            context._async_events.clear()  # type: ignore[reportUnknownMemberType]

        # Restore frames
        if hasattr(context, "frames"):
            context.frames.extend([frame.copy() for frame in self.frames])  # type: ignore[reportUnknownMemberType]

        # Restore computed properties
        for key, prop_data in self.computed_properties.items():
            if hasattr(context, "add_computed_property"):
                context.add_computed_property(  # type: ignore[reportUnknownMemberType]
                    key,
                    prop_data["func"],
                    prop_data["dependencies"],
                )

        # Restore transformations
        for key, funcs in self.transformations.items():
            for func in funcs:
                if hasattr(context, "add_transformation"):
                    context.add_transformation(key, func)  # type: ignore[reportUnknownMemberType]


class ComputedProperty:
    """Represents a computed property that automatically updates when its dependencies change."""

    def __init__(
        self, func: ComputedFunction, dependencies: list[str] | None = None
    ) -> None:
        """Initialize a computed property.

        Args:
            func: Function that computes the value, takes Context as parameter
            dependencies: List of context keys this property depends on. If None, will track automatically.
        """
        super().__init__()
        self.func = func
        self.dependencies = (dependencies or []).copy()
        self._cached_value: ContextValue = None
        self._is_cached = False
        self._subscribers: WeakSet[Any] = WeakSet()

    def compute(self, context: Any) -> ContextValue:
        """Compute the property value for the given context.

        Args:
            context: The context to compute the value from

        Returns:
            The computed value (cached if already computed)
        """
        if self._is_cached:
            return self._cached_value

        value = self.func(context)
        self._cached_value = value
        self._is_cached = True
        return value
