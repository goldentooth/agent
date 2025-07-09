"""Context snapshot functionality."""

from __future__ import annotations

import time
from typing import Any


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
            for key, prop in context._computed_properties.items():
                self.computed_properties[key] = {
                    "func": prop.func,
                    "dependencies": prop.dependencies.copy(),
                }

        # Store transformations
        self.transformations: dict[str, list[Any]] = {}
        if hasattr(context, "_transformations"):
            for key, transforms in context._transformations.items():
                self.transformations[key] = [t.func for t in transforms]

        # Store metadata
        self.context_id = id(context)

        # For backward compatibility with MockContext objects (used in tests)
        if hasattr(context, "data") and not hasattr(context, "frames"):
            self.mock_data: dict[str, Any] | None = (
                context.data.copy() if context.data else {}
            )
        else:
            self.mock_data = None

    def restore_to(self, context: Any) -> None:
        """Restore this snapshot to the given context.

        Args:
            context: The context to restore to
        """
        # Handle MockContext objects (backward compatibility for tests)
        if hasattr(context, "data") and not hasattr(context, "frames"):
            if self.mock_data is not None:
                context.data = self.mock_data.copy()
            else:
                context.data = {}
            return

        # Handle real Context objects
        # Clear current state
        if hasattr(context, "frames"):
            context.frames.clear()
        if hasattr(context, "_computed_properties"):
            context._computed_properties.clear()
        if hasattr(context, "_transformations"):
            context._transformations.clear()
        if hasattr(context, "_dependency_graph"):
            context._dependency_graph.clear()
        if hasattr(context, "_sync_events"):
            context._sync_events.clear()
        if hasattr(context, "_async_events"):
            context._async_events.clear()

        # Restore frames
        if hasattr(context, "frames"):
            context.frames.extend([frame.copy() for frame in self.frames])

        # Restore computed properties
        for key, prop_data in self.computed_properties.items():
            if hasattr(context, "add_computed_property"):
                context.add_computed_property(
                    key,
                    prop_data["func"],
                    prop_data["dependencies"],
                )

        # Restore transformations
        for key, funcs in self.transformations.items():
            for func in funcs:
                if hasattr(context, "add_transformation"):
                    context.add_transformation(key, func)
