"""Main Context system implementation."""

from __future__ import annotations

import re
import time
from typing import TYPE_CHECKING, Any, Callable, Dict, Iterator, Set, cast

if TYPE_CHECKING:
    from .history_tracker import ContextChangeEvent

from .computed import ComputedProperty, Transformation
from .frame import ContextFrame
from .snapshots import ContextSnapshot

if TYPE_CHECKING:
    from .snapshot_manager import SnapshotManager

# Type aliases for context system
ContextValue = Any
TransformFunction = Any
ContextData = dict[str, Any]
ValuePredicate = Callable[[Any], bool]


class Context:
    """A layered, reactive, symbolic context with scoped access and transformation support."""

    def __init__(self, frames: list[ContextFrame] | None = None) -> None:
        """Initialize the context with optional initial frames."""
        super().__init__()

        # Import here to avoid circular imports
        from .frame import ContextFrame
        from .history_tracker import HistoryTracker
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

        # History tracking for change events
        self._history_tracker: HistoryTracker = HistoryTracker()

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
        # Get old value for history tracking
        old_value = self.get(key, None)

        # Set value in the current (last) frame
        self.frames[-1][key] = value

        # Record the change in history
        self._history_tracker.record_change(key, old_value, value, id(self))

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
        self, old: Any, new: Any, max_depth: int, visited: Set[int]
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
                    cast(Dict[str, Any], old),
                    cast(Dict[str, Any], new),
                    max_depth - 1,
                    visited,
                )
            elif isinstance(old, list) and isinstance(new, list):
                return self._deep_compare_lists(
                    old,  # pyright: ignore[reportUnknownArgumentType]
                    new,  # pyright: ignore[reportUnknownArgumentType]
                    max_depth - 1,
                    visited,
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
        visited: Set[int],
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
        visited: Set[int],
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

    def create_snapshot(self, name: str) -> ContextSnapshot:
        """Create a snapshot of the current context state.

        Args:
            name: Name/identifier for this snapshot

        Returns:
            A ContextSnapshot instance containing the current state
        """
        return self._snapshot_manager.create_snapshot(self, name)

    def restore_snapshot(self, name: str) -> None:
        """Restore the context to a previous snapshot state.

        Args:
            name: Name of the snapshot to restore

        Raises:
            KeyError: If snapshot with the given name doesn't exist
        """
        self._snapshot_manager.restore_snapshot(self, name)

    def list_snapshots(self) -> dict[str, float]:
        """List all available snapshots with their timestamps.

        Returns:
            Dictionary mapping snapshot names to their timestamps
        """
        return self._snapshot_manager.list_snapshots()

    def delete_snapshot(self, name: str) -> None:
        """Delete a snapshot.

        Args:
            name: Name of the snapshot to delete

        Raises:
            KeyError: If snapshot with the given name doesn't exist
        """
        self._snapshot_manager.delete_snapshot(name)

    def get_snapshots(self) -> dict[str, ContextSnapshot]:
        """Get all snapshots (returns a copy).

        Returns:
            Dictionary of snapshot names to snapshot objects
        """
        return {
            name: self._snapshot_manager.get_snapshot(name)
            for name in self._snapshot_manager.list_snapshots()
        }

    def get_change_history(
        self, limit: int | None = None, since: float | None = None
    ) -> list[ContextChangeEvent]:
        """Get the change history for this context.

        Args:
            limit: Maximum number of events to return (most recent first)
            since: Only return events after this timestamp

        Returns:
            List of change events
        """
        return self._history_tracker.get_history(limit=limit, since=since)

    def clear_history(self) -> None:
        """Clear the change history."""
        self._history_tracker.clear_history()

    def get_history_size(self) -> int:
        """Get the current size of the change history.

        Returns:
            The number of change events currently stored in the history
        """
        return self._history_tracker.get_history_size()

    def set_max_history_size(self, size: int) -> None:
        """Set the maximum history size.

        Args:
            size: Maximum number of change events to keep
        """
        self._history_tracker.set_max_history_size(size)

    def rollback_to_timestamp(self, timestamp: float) -> None:
        """Rollback the context to a specific timestamp.

        Args:
            timestamp: The timestamp to rollback to

        Raises:
            ValueError: If timestamp is in the future or no history exists
        """
        current_time = time.time()
        if timestamp > current_time:
            raise ValueError("Cannot rollback to a future timestamp")

        if self.get_history_size() == 0:
            raise ValueError("No history available for rollback")

        # Create automatic snapshot before rollback
        auto_snapshot_name = f"auto_rollback_backup_{current_time}"
        self.create_snapshot(auto_snapshot_name)

        # Get changes to reverse from history tracker
        changes_to_reverse = self._history_tracker.get_changes_to_reverse(timestamp)

        if not changes_to_reverse:
            # No changes to reverse, but we've already created a snapshot
            return

        # Temporarily store original history tracker to avoid recording rollback operations
        original_tracker = self._history_tracker

        # Create a temporary history tracker to avoid recording rollback operations
        from .history_tracker import HistoryTracker

        temp_tracker = HistoryTracker()
        temp_tracker.set_max_history_size(
            0
        )  # Disable history recording during rollback
        self._history_tracker = temp_tracker

        try:
            # Apply reversals - set each key back to its old value
            for event in changes_to_reverse:
                try:
                    if event.old_value is None:
                        # Key was added, so remove it if it exists
                        for frame in reversed(self.frames):
                            if event.key in frame:
                                del frame[event.key]
                                break
                    else:
                        # Key was modified or deleted, so restore old value
                        self.frames[-1][event.key] = event.old_value
                except Exception:
                    # Continue with other reversals even if one fails
                    pass
        finally:
            # Restore original history tracker
            self._history_tracker = original_tracker

    def replay_changes_since(self, timestamp: float) -> list[ContextChangeEvent]:
        """Get all changes that occurred since a specific timestamp.

        Args:
            timestamp: Timestamp to get changes since

        Returns:
            List of change events in chronological order
        """
        return self._history_tracker.replay_changes_since(timestamp)

    def keys(self) -> Iterator[str]:
        """Yield all unique keys from the context, including computed properties."""
        seen: set[str] = set()

        # First yield computed properties
        for k in self._computed_properties:
            if k not in seen:
                yield k
                seen.add(k)

        # Then yield frame keys
        for frame in reversed(self.frames):
            for k in frame.data:
                if k not in seen:
                    yield k
                    seen.add(k)

    def add_computed_property(
        self, key: str, func: Any, dependencies: list[str] | None = None
    ) -> None:
        """Add a computed property to the context.

        Args:
            key: The key where the computed value will be accessible
            func: Function that computes the value, takes Context as parameter
            dependencies: List of context keys this property depends on. If None, will track automatically.
        """
        # Create the computed property
        computed_prop = ComputedProperty(func, dependencies)

        # Subscribe this context to the computed property for dependency tracking
        computed_prop.subscribe(self)

        # Store the computed property
        self._computed_properties[key] = computed_prop

    def remove_computed_property(self, key: str) -> None:
        """Remove a computed property from the context.

        Args:
            key: The key of the computed property to remove
        """
        if key not in self._computed_properties:
            return

        # Remove the computed property
        del self._computed_properties[key]

    def get_computed_value(self, key: str) -> Any:
        """Get the value of a computed property.

        Args:
            key: The computed property key

        Returns:
            The computed value

        Raises:
            KeyError: If the key is not a computed property
        """
        if key not in self._computed_properties:
            raise KeyError(f"No computed property found for key: {key}")

        return self._computed_properties[key].compute(self)

    def is_computed_property(self, key: str) -> bool:
        """Check if a key represents a computed property.

        Args:
            key: The key to check

        Returns:
            True if the key is a computed property, False otherwise
        """
        return key in self._computed_properties

    def computed_properties(self) -> dict[str, ComputedProperty]:
        """Get all computed properties in this context.

        Returns:
            Dictionary mapping property names to ComputedProperty objects (copy)
        """
        return self._computed_properties.copy()

    def add_transformation(self, key: str, func: TransformFunction) -> None:
        """Add a value transformation for a specific key.

        Args:
            key: The context key to apply transformation to
            func: Function that transforms the value
        """
        if key not in self._transformations:
            self._transformations[key] = []

        transformation = Transformation(func, key)
        self._transformations[key].append(transformation)

    def remove_transformations(self, key: str) -> None:
        """Remove all transformations for a specific key.

        Args:
            key: The context key to remove transformations from
        """
        if key in self._transformations:
            del self._transformations[key]

    def transformations(self) -> dict[str, list[Transformation]]:
        """Get all transformations in this context.

        Returns:
            Dictionary mapping context keys to lists of transformations (copy)
        """
        return {k: v.copy() for k, v in self._transformations.items()}

    def query(
        self,
        pattern: str | None = None,
        key_filter: Callable[[str], bool] | None = None,
        value_filter: ValuePredicate | None = None,
        include_computed: bool = True,
    ) -> ContextData:
        """Query the context with flexible filtering options.

        Args:
            pattern: Regex pattern to match against context keys
            key_filter: Function to filter keys based on custom logic
            value_filter: Function to filter values
            include_computed: Whether to include computed properties in results

        Returns:
            Dictionary of filtered key-value pairs
        """
        result: ContextData = {}

        # Compile regex pattern if provided
        compiled_pattern = None
        if pattern is not None:
            try:
                compiled_pattern = re.compile(pattern)
            except re.error:
                # Invalid regex pattern, return empty result
                return result

        # Iterate through all context keys
        for key in self.keys():
            # Skip computed properties if not included
            if not include_computed and self.is_computed_property(key):
                continue

            # Apply pattern filter
            if compiled_pattern is not None and not compiled_pattern.search(key):
                continue

            # Apply key filter
            if key_filter is not None and not key_filter(key):
                continue

            # Get value and apply value filter
            try:
                value = self.get(key)
                if value_filter is not None and not value_filter(value):
                    continue

                # Key passed all filters, include in result
                result[key] = value
            except Exception:
                # Skip keys that can't be accessed
                continue

        return result

    def find_keys(self, pattern: str) -> list[str]:
        """Find all keys matching a regex pattern.

        Args:
            pattern: Regex pattern to match against keys

        Returns:
            List of matching keys
        """
        try:
            regex = re.compile(pattern)
            return [key for key in self.keys() if regex.search(key)]
        except re.error:
            # Invalid regex pattern, return empty list
            return []

    def find_values(self, predicate: ValuePredicate) -> ContextData:
        """Find all key-value pairs where the value matches a predicate.

        Args:
            predicate: Function that returns True for matching values

        Returns:
            Dictionary of matching key-value pairs
        """
        return self.query(value_filter=predicate)

    def filter_by_type(self, value_type: type | tuple[type, ...]) -> ContextData:
        """Filter context entries by value type.

        Args:
            value_type: Type or tuple of types to filter by

        Returns:
            Dictionary of entries with values of the specified type(s)
        """
        return self.query(value_filter=lambda v: isinstance(v, value_type))

    def search(self, search_term: str, case_sensitive: bool = False) -> ContextData:
        """Search for keys or values containing a term.

        Args:
            search_term: Term to search for
            case_sensitive: Whether search should be case sensitive

        Returns:
            Dictionary of matching key-value pairs
        """
        if not case_sensitive:
            search_term = search_term.lower()

        def matches_search(key: str, value: ContextValue) -> bool:
            # Check key
            key_match = search_term in (key if case_sensitive else key.lower())

            # Check value (convert to string)
            try:
                value_str = str(value)
                if not case_sensitive:
                    value_str = value_str.lower()
                value_match = search_term in value_str
            except Exception:
                value_match = False

            return key_match or value_match

        results: ContextData = {}
        for key in self.keys():
            try:
                value = self[key]
                if matches_search(key, value):
                    results[key] = value
            except Exception:
                continue

        return results
