"""Main Context system implementation."""

from __future__ import annotations

import time
from typing import TYPE_CHECKING, Any
from weakref import WeakSet

from .frame import ContextFrame

if TYPE_CHECKING:
    from .snapshot_manager import SnapshotManager

# Type aliases for context system
ContextValue = Any
ComputedFunction = Any
TransformFunction = Any


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

    def invalidate(self) -> None:
        """Invalidate the cached value, requiring recomputation."""
        self._is_cached = False
        self._cached_value = None

    def subscribe(self, context: Any) -> None:
        """Subscribe a context to this computed property for dependency tracking."""
        self._subscribers.add(context)

    def notify_change(self) -> None:
        """Notify all subscribed contexts that this property may have changed."""
        for context in self._subscribers:
            try:
                if hasattr(context, "_handle_computed_property_change"):
                    context._handle_computed_property_change(self)
            except Exception:
                # Continue notifying other contexts even if one fails
                pass


class Transformation:
    """Represents a value transformation applied to context keys."""

    def __init__(self, func: TransformFunction, key: str) -> None:
        """Initialize a transformation.

        Args:
            func: Function that transforms the value
            key: The context key this transformation applies to
        """
        super().__init__()
        self.func = func
        self.key = key

    def apply(self, value: ContextValue) -> ContextValue:
        """Apply the transformation to a value."""
        return self.func(value)


class Context:
    """A layered, reactive, symbolic context with scoped access and transformation support."""

    def __init__(self, frames: list[ContextFrame] | None = None) -> None:
        """Initialize the context with optional initial frames."""
        super().__init__()

        # Import here to avoid circular imports
        from .frame import ContextFrame
        from .snapshot_manager import SnapshotManager

        if frames is None:
            self.frames: list[ContextFrame] = [ContextFrame()]
        elif len(frames) == 0:
            self.frames = [ContextFrame()]
        else:
            self.frames = frames

        # Computed properties and transformations
        self._computed_properties: dict[str, ComputedProperty] = {}
        self._transformations: dict[str, list[Transformation]] = {}

        # Snapshots for time-travel debugging
        self._snapshot_manager: SnapshotManager = SnapshotManager()

    def get(self, key: str, default: Any | None = None) -> Any | None:
        """Get the value for a key, searching through all frames and computed properties.

        Args:
            key: The key to search for
            default: Default value to return if key is not found

        Returns:
            The value for the key, or the default value if not found
        """
        # Check if it's a computed property first
        if key in self._computed_properties:
            computed_value = self._computed_properties[key].compute(self)
            return computed_value

        # Search through frames in reverse order (top to bottom)
        for frame in reversed(self.frames):
            if key in frame:
                frame_value = frame[key]
                return frame_value
        return default

    def __getitem__(self, key: str) -> ContextValue:
        """Get the value for a key, raising KeyError if not found.

        Args:
            key: The key to search for

        Returns:
            The value for the key

        Raises:
            KeyError: If the key is not found in any frame or computed property
        """
        # Check if it's a computed property first
        if key in self._computed_properties:
            return self._computed_properties[key].compute(self)

        # Search through frames in reverse order (top to bottom)
        for frame in reversed(self.frames):
            if key in frame:
                return frame[key]
        raise KeyError(f"Context key '{key}' not found")

    def set(self, key: str, value: ContextValue) -> None:
        """Set a value for a key in the current frame.

        Args:
            key: The key to set
            value: The value to set
        """
        # Set value in the current (last) frame
        self.frames[-1][key] = value

    def __setitem__(self, key: str, value: ContextValue) -> None:
        """Set a value for a key in the current frame.

        Args:
            key: The key to set
            value: The value to set
        """
        # Delegate to the set method
        self.set(key, value)

    def __contains__(self, key: str) -> bool:
        """Check if a key exists in any of the frames or as a computed property.

        Args:
            key: The key to check for

        Returns:
            True if the key exists in any frame or as a computed property, False otherwise
        """
        # Check computed properties first
        if key in self._computed_properties:
            return True

        # Check frames
        for frame in reversed(self.frames):
            if key in frame:
                return True
        return False

    def push_layer(self) -> None:
        """Push a new layer onto the context stack."""
        self.frames.append(ContextFrame())

    def pop_layer(self) -> None:
        """Pop the top layer from the context stack."""
        if len(self.frames) <= 1:
            raise IndexError("Cannot pop root context frame")
        self.frames.pop()

    def fork(self) -> "Context":
        """Create a fork of the current context with copies of the frames, computed properties, and transformations.

        Returns:
            A new Context instance that is an independent copy of this context
        """
        # Create new context with deep copies of all frames
        forked = Context([frame.copy() for frame in self.frames])

        # TODO: Copy computed properties when add_computed_property is implemented
        # for key, computed_prop in self._computed_properties.items():
        #     forked.add_computed_property(
        #         key, computed_prop.func, computed_prop.dependencies
        #     )

        # TODO: Copy transformations when add_transformation is implemented
        # for key, transformations in self._transformations.items():
        #     for transformation in transformations:
        #         forked.add_transformation(key, transformation.func)

        return forked

    def fork_with_history(self) -> "Context":
        """Create a fork of the current context that includes history and snapshots.

        Returns:
            A new Context instance that is an independent copy with preserved history and snapshots
        """
        # Start with a basic fork
        forked = self.fork()

        # TODO: Copy history when history tracking is fully implemented
        # all_history = self._history_tracker.get_all_history()
        # for event in all_history:
        #     # Create a deep copy of the event
        #     copied_event = ContextChangeEvent(
        #         event.key,
        #         copy.deepcopy(event.old_value),
        #         copy.deepcopy(event.new_value),
        #         id(forked),  # Update context_id to the forked context
        #     )
        #     copied_event.timestamp = event.timestamp  # Preserve original timestamp
        #     forked._history_tracker._change_history.append(copied_event)

        # TODO: Copy snapshots when snapshot system is fully implemented
        # for name in self._snapshot_manager.list_snapshots():
        #     snapshot = self._snapshot_manager.get_snapshot(name)
        #     forked_snapshot = ContextSnapshot(forked, name)
        #     forked_snapshot.timestamp = snapshot.timestamp
        #     forked_snapshot.frames = [frame.copy() for frame in snapshot.frames]
        #     forked_snapshot.computed_properties = copy.deepcopy(snapshot.computed_properties)
        #     forked_snapshot.transformations = copy.deepcopy(snapshot.transformations)
        #     forked._snapshot_manager._snapshots[name] = forked_snapshot

        return forked

    def merge(self, other: "Context") -> "Context":
        """Merge another context into this context.

        Args:
            other: The context to merge into this context

        Returns:
            This context (for method chaining)
        """
        # Merge all data from other context's frames into current context
        for frame in other.frames:
            for key in frame.keys():
                self.set(key, frame[key])

        return self

    def diff(self, other: "Context") -> dict[str, Any]:
        """Compare this context with another context and return the differences.

        Args:
            other: The context to compare against

        Returns:
            Dictionary with 'added', 'modified', and 'removed' keys containing the differences
        """
        diff_result: dict[str, Any] = {"added": {}, "modified": {}, "removed": {}}

        # Get all keys from both contexts
        self_keys: set[str] = set()
        other_keys: set[str] = set()

        # Collect all keys that exist in self
        for frame in self.frames:
            self_keys.update(frame.keys())

        # Add computed property keys
        self_keys.update(self._computed_properties.keys())

        # Collect all keys that exist in other
        for frame in other.frames:
            other_keys.update(frame.keys())

        # Add computed property keys from other
        other_keys.update(other._computed_properties.keys())

        # Find added keys (in other but not in self)
        added_keys = other_keys - self_keys
        for key in added_keys:
            diff_result["added"][key] = other.get(key)

        # Find removed keys (in self but not in other)
        removed_keys = self_keys - other_keys
        for key in removed_keys:
            diff_result["removed"][key] = self.get(key)

        # Find modified keys (in both but with different values)
        shared_keys = self_keys & other_keys
        for key in shared_keys:
            self_value = self.get(key)
            other_value = other.get(key)
            if self_value != other_value:
                diff_result["modified"][key] = {"old": self_value, "new": other_value}

        return diff_result

    def deep_diff(self, other: "Context", max_depth: int = 10) -> dict[str, Any]:
        """Compare this context with another context and return deep differences.

        Args:
            other: The context to compare against
            max_depth: Maximum depth for recursive comparison to prevent infinite recursion

        Returns:
            Dictionary with 'added', 'modified', and 'removed' keys containing deep differences
        """
        # Start with basic diff
        basic_diff = self.diff(other)

        # Enhance modified section with deep analysis
        for key, change in basic_diff["modified"].items():
            old_value = change["old"]
            new_value = change["new"]

            # If both values are complex types, perform deep comparison
            if self._is_complex_type(old_value) and self._is_complex_type(new_value):
                deep_changes = self._deep_compare(
                    old_value, new_value, max_depth, set()
                )
                if deep_changes:
                    basic_diff["modified"][key]["deep_changes"] = deep_changes

        return basic_diff

    def _is_complex_type(self, value: Any) -> bool:
        """Check if a value is a complex type that supports deep comparison."""
        return isinstance(value, (dict, list))

    def _deep_compare(
        self, old: Any, new: Any, max_depth: int, visited: set[int]
    ) -> dict[str, Any]:
        """Recursively compare two complex values and return deep differences."""
        if max_depth <= 0:
            return {}

        # Prevent infinite recursion with circular references
        old_id = id(old)
        new_id = id(new)
        if old_id in visited or new_id in visited:
            return {}

        visited.add(old_id)
        visited.add(new_id)

        try:
            if isinstance(old, dict) and isinstance(new, dict):
                return self._deep_compare_dicts(
                    old, new, max_depth - 1, visited  # type: ignore[arg-type]
                )
            elif isinstance(old, list) and isinstance(new, list):
                return self._deep_compare_lists(
                    old, new, max_depth - 1, visited  # type: ignore[arg-type]
                )
            else:
                return {}
        finally:
            visited.discard(old_id)
            visited.discard(new_id)

    def _deep_compare_dicts(
        self,
        old_dict: dict[str, Any],
        new_dict: dict[str, Any],
        max_depth: int,
        visited: set[int],
    ) -> dict[str, Any]:
        """Compare two dictionaries deeply."""
        result: dict[str, Any] = {"added": {}, "modified": {}, "removed": {}}

        old_keys = set(old_dict.keys())
        new_keys = set(new_dict.keys())

        # Find added keys
        for key in new_keys - old_keys:
            result["added"][key] = new_dict[key]

        # Find removed keys
        for key in old_keys - new_keys:
            result["removed"][key] = old_dict[key]

        # Find modified keys
        for key in old_keys & new_keys:
            old_value = old_dict[key]
            new_value = new_dict[key]

            if old_value != new_value:
                if self._is_complex_type(old_value) and self._is_complex_type(
                    new_value
                ):
                    deep_changes = self._deep_compare(
                        old_value, new_value, max_depth, visited.copy()
                    )
                    result["modified"][key] = {
                        "old": old_value,
                        "new": new_value,
                        "deep_changes": deep_changes,
                    }
                else:
                    result["modified"][key] = {"old": old_value, "new": new_value}

        return result

    def _deep_compare_lists(
        self,
        old_list: list[Any],
        new_list: list[Any],
        max_depth: int,
        visited: set[int],
    ) -> dict[str, Any]:
        """Compare two lists deeply."""
        result: dict[str, Any] = {"added": {}, "modified": {}, "removed": {}}

        # For lists, we'll do a simple index-based comparison
        # This is a simplified approach - more sophisticated list diffing could be implemented
        old_len = len(old_list)
        new_len = len(new_list)
        min_len = min(old_len, new_len)

        # Compare items at same indices
        for i in range(min_len):
            old_item = old_list[i]
            new_item = new_list[i]

            if old_item != new_item:
                if self._is_complex_type(old_item) and self._is_complex_type(new_item):
                    deep_changes = self._deep_compare(
                        old_item, new_item, max_depth, visited.copy()
                    )
                    result["modified"][f"[{i}]"] = {
                        "old": old_item,
                        "new": new_item,
                        "deep_changes": deep_changes,
                    }
                else:
                    result["modified"][f"[{i}]"] = {"old": old_item, "new": new_item}

        # Handle added items (new list is longer)
        if new_len > old_len:
            for i in range(old_len, new_len):
                result["added"][f"[{i}]"] = new_list[i]

        # Handle removed items (old list is longer)
        if old_len > new_len:
            for i in range(new_len, old_len):
                result["removed"][f"[{i}]"] = old_list[i]

        return result
