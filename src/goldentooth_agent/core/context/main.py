from __future__ import annotations

import copy
import json
import re
import time
from collections.abc import Callable, Iterator
from typing import Any, TypeVar
from weakref import WeakSet

from pyee import EventEmitter
from pyee.asyncio import AsyncIOEventEmitter

from goldentooth_agent.core.event import AsyncEventFlow, SyncEventFlow
from goldentooth_agent.core.flow import Flow

from .dependency_graph import DependencyGraph
from .frame import ContextFrame
from .history_tracker import ContextChangeEvent, HistoryTracker
from .snapshot_manager import SnapshotManager

T = TypeVar("T")


class ContextSnapshot:
    """Represents a snapshot of context state at a specific point in time."""

    def __init__(self, context: Context, name: str):
        """Create a snapshot of the current context state.

        Args:
            context: The context to snapshot
            name: Name/identifier for this snapshot
        """
        self.name = name
        self.timestamp = time.time()

        # Deep copy the frames to preserve state
        self.frames = [frame.copy() for frame in context.frames]

        # Store computed property definitions (but not cached values)
        self.computed_properties = {}
        for key, prop in context._computed_properties.items():
            self.computed_properties[key] = {
                "func": prop.func,
                "dependencies": prop.dependencies.copy(),
            }

        # Store transformations
        self.transformations = {}
        for key, transforms in context._transformations.items():
            self.transformations[key] = [t.func for t in transforms]

        # Store metadata
        self.context_id = id(context)

    def restore_to(self, context: Context) -> None:
        """Restore this snapshot to the given context.

        Args:
            context: The context to restore to
        """
        # Clear current state
        context.frames.clear()
        context._computed_properties.clear()
        context._transformations.clear()
        context._dependency_graph.clear()
        context._sync_events.clear()
        context._async_events.clear()

        # Restore frames
        context.frames.extend([frame.copy() for frame in self.frames])

        # Restore computed properties
        for key, prop_data in self.computed_properties.items():
            context.add_computed_property(
                key,
                prop_data["func"],  # type: ignore[arg-type]
                prop_data["dependencies"],  # type: ignore[arg-type]
            )

        # Restore transformations
        for key, funcs in self.transformations.items():
            for func in funcs:
                context.add_transformation(key, func)


class ComputedProperty:
    """Represents a computed property that automatically updates when its dependencies change."""

    def __init__(
        self, func: Callable[[Context], Any], dependencies: list[str] | None = None
    ):
        """Initialize a computed property.

        Args:
            func: Function that computes the value, takes Context as parameter
            dependencies: List of context keys this property depends on. If None, will track automatically.
        """
        self.func = func
        self.dependencies = dependencies or []
        self._cached_value: Any = None
        self._is_cached = False
        self._subscribers: WeakSet[Context] = WeakSet()

    def compute(self, context: Context) -> Any:
        """Compute the property value for the given context."""
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

    def subscribe(self, context: Context) -> None:
        """Subscribe a context to this computed property for dependency tracking."""
        self._subscribers.add(context)

    def notify_change(self) -> None:
        """Notify all subscribed contexts that this property may have changed."""
        for context in self._subscribers:
            context._handle_computed_property_change(self)


class Transformation:
    """Represents a value transformation applied to context keys."""

    def __init__(self, func: Callable[[Any], Any], key: str):
        """Initialize a transformation.

        Args:
            func: Function that transforms the value
            key: The context key this transformation applies to
        """
        self.func = func
        self.key = key

    def apply(self, value: Any) -> Any:
        """Apply the transformation to a value."""
        return self.func(value)


class Context:
    """A layered, reactive, symbolic context with scoped access and EventFlow integration."""

    def __init__(self, frames: list[ContextFrame] | None = None):
        """Initialize the context with optional initial frames."""
        self.frames: list[ContextFrame] = frames or [ContextFrame()]

        # Create isolated emitters for this context instance
        self._sync_emitter = EventEmitter()
        self._async_emitter = AsyncIOEventEmitter()

        # EventFlow integration with isolated emitters
        self._sync_events: dict[str, SyncEventFlow[Any]] = {}
        self._async_events: dict[str, AsyncEventFlow[Any]] = {}

        # Global context change events with isolated emitters
        self._global_sync_events = SyncEventFlow[dict[str, Any]](
            "context.global_changes", self._sync_emitter
        )
        self._global_async_events = AsyncEventFlow[dict[str, Any]](
            "context.global_changes", self._async_emitter
        )

        # Computed properties and transformations
        self._computed_properties: dict[str, ComputedProperty] = {}
        self._transformations: dict[str, list[Transformation]] = {}
        self._dependency_graph = DependencyGraph()

        # Snapshots and time-travel debugging
        self._snapshot_manager = SnapshotManager()
        self._history_tracker = HistoryTracker(max_size=1000)

    def get(self, key: str, default: T | None = None) -> T | None:
        """Get the value for a key, searching through all frames and computed properties."""
        # Check if it's a computed property first
        if key in self._computed_properties:
            return self._computed_properties[key].compute(self)  # type: ignore[no-any-return]

        # Search through frames
        for frame in reversed(self.frames):
            if key in frame:
                return frame[key]  # type: ignore[no-any-return]
        return default

    def __getitem__(self, key: str) -> Any:
        """Get the value for a key, raising KeyError if not found."""
        # Check if it's a computed property first
        if key in self._computed_properties:
            return self._computed_properties[key].compute(self)

        # Search through frames
        for frame in reversed(self.frames):
            if key in frame:
                return frame[key]
        raise KeyError(f"Context key '{key}' not found")

    def set(self, key: str, value: Any) -> None:
        """Set a value for a key in the current frame and notify subscribers/emit events."""
        old_value = self.get(key)

        # Apply transformations if any exist for this key
        transformed_value = self._apply_transformations(key, value)

        self.frames[-1][key] = transformed_value

        # Invalidate computed properties that depend on this key
        self._invalidate_dependent_computed_properties(key)

        # Record change in history
        self._record_change(key, old_value, transformed_value)

        # Emit events through EventFlow system
        self._emit_change_event(key, transformed_value, old_value)

    def __setitem__(self, key: str, value: Any) -> None:
        """Set a value for a key in the current frame and notify subscribers/emit events."""
        old_value = self.get(key)

        # Apply transformations if any exist for this key
        transformed_value = self._apply_transformations(key, value)

        self.frames[-1][key] = transformed_value

        # Invalidate computed properties that depend on this key
        self._invalidate_dependent_computed_properties(key)

        # Record change in history
        self._record_change(key, old_value, transformed_value)

        # Emit events through EventFlow system
        self._emit_change_event(key, transformed_value, old_value)

    def __contains__(self, key: str) -> bool:
        """Check if a key exists in any of the frames or as a computed property."""
        # Check computed properties first
        if key in self._computed_properties:
            return True

        # Check frames
        return self.get(key) is not None

    def push_layer(self) -> None:
        """Push a new layer onto the context stack."""
        self.frames.append(ContextFrame())

    def pop_layer(self) -> None:
        """Pop the top layer from the context stack."""
        if len(self.frames) <= 1:
            raise IndexError("Cannot pop root context frame")
        self.frames.pop()

    def fork(self) -> Context:
        """Create a fork of the current context with copies of the frames, computed properties, and transformations."""
        forked = Context([frame.copy() for frame in self.frames])

        # Copy computed properties
        for key, computed_prop in self._computed_properties.items():
            forked.add_computed_property(
                key, computed_prop.func, computed_prop.dependencies
            )

        # Copy transformations
        for key, transformations in self._transformations.items():
            for transformation in transformations:
                forked.add_transformation(key, transformation.func)

        return forked

    def fork_with_history(self) -> Context:
        """Create a fork of the current context that includes history and snapshots.

        Returns:
            Forked context with preserved history and snapshots
        """
        forked = self.fork()

        # Copy history (deep copy to avoid shared references)
        all_history = self._history_tracker.get_all_history()
        for event in all_history:
            # Create a deep copy of the event
            copied_event = ContextChangeEvent(
                event.key,
                copy.deepcopy(event.old_value),
                copy.deepcopy(event.new_value),
                id(forked),  # Update context_id to the forked context
            )
            copied_event.timestamp = event.timestamp  # Preserve original timestamp
            forked._history_tracker._change_history.append(copied_event)

        # Copy snapshots (but update context_id references)
        for name in self._snapshot_manager.list_snapshots():
            snapshot = self._snapshot_manager.get_snapshot(name)
            forked_snapshot = ContextSnapshot(forked, name)
            forked_snapshot.timestamp = snapshot.timestamp
            forked_snapshot.frames = [frame.copy() for frame in snapshot.frames]
            forked_snapshot.computed_properties = copy.deepcopy(
                snapshot.computed_properties
            )
            forked_snapshot.transformations = copy.deepcopy(snapshot.transformations)
            forked._snapshot_manager._snapshots[name] = forked_snapshot

        return forked

    def merge(self, other: Context) -> Context:
        """Merge another context into this one, updating frames."""
        new = self.fork()
        for i, frame in enumerate(other.frames):
            if i < len(new.frames):
                new.frames[i].data.update(frame.data)
            else:
                new.frames.append(frame.copy())
        return new

    def diff(self, other: Context) -> dict[str, tuple[Any, Any]]:
        """Compute the differences between this context and another."""
        diffs = {}
        keys = set(self.keys()) | set(other.keys())
        for k in keys:
            a = self.get(k)
            b = other.get(k)
            if a != b:
                diffs[k] = (a, b)
        return diffs

    def deep_diff(
        self, other: Context, delimiter: str = "."
    ) -> dict[str, tuple[Any, Any]]:
        """Compute deep differences including nested values.

        Args:
            other: Other context to compare with
            delimiter: Delimiter for nested paths

        Returns:
            Dictionary of differences with nested paths as keys
        """
        # Flatten both contexts
        flat_self = self.flatten(delimiter)
        flat_other = other.flatten(delimiter)

        diffs = {}
        all_keys = set(flat_self.keys()) | set(flat_other.keys())

        for key in all_keys:
            a = flat_self.get(key)
            b = flat_other.get(key)
            if a != b:
                diffs[key] = (a, b)

        return diffs

    def create_snapshot(self, name: str) -> ContextSnapshot:
        """Create a snapshot of the current context state.

        Args:
            name: Name/identifier for the snapshot

        Returns:
            The created snapshot

        Raises:
            ValueError: If a snapshot with the same name already exists
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
        """Get the current size of the change history."""
        return self._history_tracker.get_history_size()

    def set_max_history_size(self, size: int) -> None:
        """Set the maximum history size.

        Args:
            size: Maximum number of change events to keep
        """
        self._history_tracker.set_max_history_size(size)

    def rollback_to_timestamp(self, timestamp: float) -> None:
        """Rollback context to state at a specific timestamp.

        This creates a snapshot of the current state first, then attempts to
        reconstruct the context state at the given timestamp by replaying history.

        Args:
            timestamp: Target timestamp to rollback to

        Raises:
            ValueError: If timestamp is in the future or no history available
        """
        if timestamp > time.time():
            raise ValueError("Cannot rollback to future timestamp")

        if self._history_tracker.get_history_size() == 0:
            raise ValueError("No change history available for rollback")

        # Create automatic snapshot before rollback
        auto_snapshot_name = f"auto_rollback_{int(time.time())}"
        self.create_snapshot(auto_snapshot_name)

        # Get changes that need to be reversed
        changes_to_reverse = self._history_tracker.get_changes_to_reverse(timestamp)

        # Apply the reversals
        for event in changes_to_reverse:
            try:
                # Set the value back to its old value
                # We temporarily save and clear history to avoid recording the rollback changes
                saved_tracker = self._history_tracker
                self._history_tracker = HistoryTracker(max_size=0)

                self[event.key] = event.old_value

                # Restore the history tracker (with the reversed change removed)
                self._history_tracker = saved_tracker
                # Remove the reversed event from history
                all_history = self._history_tracker.get_all_history()
                filtered_history = [e for e in all_history if e != event]
                self._history_tracker.clear_history()
                for e in filtered_history:
                    self._history_tracker._change_history.append(e)

            except Exception:
                # If we can't reverse a change (e.g., key doesn't exist anymore),
                # restore the tracker and continue with the next one
                self._history_tracker = saved_tracker
                pass

    def get_snapshots(self) -> dict[str, ContextSnapshot]:
        """Get all snapshots (returns a copy).

        Returns:
            Dictionary of snapshot names to snapshot objects
        """
        return {
            name: self._snapshot_manager.get_snapshot(name)
            for name in self._snapshot_manager.list_snapshots()
        }

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
        seen = set()

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

    def _record_change(self, key: str, old_value: Any, new_value: Any) -> None:
        """Record a change event in the history."""
        self._history_tracker.record_change(key, old_value, new_value, id(self))

    def _emit_change_event(self, key: str, new_value: Any, old_value: Any) -> None:
        """Emit context change events through EventFlow system."""
        change_data = {
            "key": key,
            "new_value": new_value,
            "old_value": old_value,
            "timestamp": time.time(),
            "context_id": id(self),
        }

        # Emit to key-specific event flows (catch errors to prevent breaking context operations)
        try:
            if key in self._sync_events:
                self._sync_events[key].emit(new_value)
        except Exception:
            # Ignore handler errors - they shouldn't break context operations
            pass

        try:
            if key in self._async_events:
                self._async_events[key].emit(new_value)
        except Exception:
            # Ignore handler errors - they shouldn't break context operations
            pass

        # Emit to global context change events
        try:
            self._global_sync_events.emit(change_data)
        except Exception:
            # Ignore handler errors - they shouldn't break context operations
            pass

        try:
            self._global_async_events.emit(change_data)
        except Exception:
            # Ignore handler errors - they shouldn't break context operations
            pass

    def subscribe_sync(self, key: str) -> SyncEventFlow[Any]:
        """Get a synchronous EventFlow for changes to a specific key.

        Args:
            key: The context key to watch for changes

        Returns:
            SyncEventFlow that emits new values when the key changes
        """
        if key not in self._sync_events:
            self._sync_events[key] = SyncEventFlow[Any](
                f"context.{key}", self._sync_emitter
            )
        return self._sync_events[key]

    def subscribe_async(self, key: str) -> AsyncEventFlow[Any]:
        """Get an asynchronous EventFlow for changes to a specific key.

        Args:
            key: The context key to watch for changes

        Returns:
            AsyncEventFlow that emits new values when the key changes
        """
        if key not in self._async_events:
            self._async_events[key] = AsyncEventFlow[Any](
                f"context.{key}", self._async_emitter
            )
        return self._async_events[key]

    def as_flow(self, key: str, use_async: bool = True) -> Flow[None, Any]:
        """Convert context key changes to a Flow stream.

        Args:
            key: The context key to watch for changes
            use_async: Whether to use async or sync event flow

        Returns:
            Flow that yields new values when the key changes
        """
        if use_async:
            return self.subscribe_async(key).as_flow()
        else:
            return self.subscribe_sync(key).as_flow()

    def global_changes_sync(self) -> SyncEventFlow[dict[str, Any]]:
        """Get a synchronous EventFlow for all context changes.

        Returns:
            SyncEventFlow that emits change data for any key modification
        """
        return self._global_sync_events

    def global_changes_async(self) -> AsyncEventFlow[dict[str, Any]]:
        """Get an asynchronous EventFlow for all context changes.

        Returns:
            AsyncEventFlow that emits change data for any key modification
        """
        return self._global_async_events

    def global_changes_as_flow(
        self, use_async: bool = True
    ) -> Flow[None, dict[str, Any]]:
        """Convert all context changes to a Flow stream.

        Args:
            use_async: Whether to use async or sync event flow

        Returns:
            Flow that yields change data for any key modification
        """
        if use_async:
            return self._global_async_events.as_flow()
        else:
            return self._global_sync_events.as_flow()

    def dump(self) -> str:
        """Dump the context as a JSON string, merging all frames."""
        merged = {}
        for frame in self.frames:
            merged.update(frame.data)
        return json.dumps(merged, indent=2)

    def __repr__(self) -> str:
        """Return a string representation of the context."""
        return f"<Context frames={len(self.frames)} keys={list(self.keys())}>"

    def _apply_transformations(self, key: str, value: Any) -> Any:
        """Apply all transformations for a given key to the value."""
        if key not in self._transformations:
            return value

        transformed_value = value
        for transformation in self._transformations[key]:
            try:
                transformed_value = transformation.apply(transformed_value)
            except Exception:
                # If transformation fails, use original value
                pass

        return transformed_value

    def _invalidate_dependent_computed_properties(self, key: str) -> None:
        """Invalidate computed properties that depend on the given key."""
        if self._dependency_graph.has_dependents(key):
            for computed_key in self._dependency_graph.get_dependents(key):
                if computed_key in self._computed_properties:
                    computed_prop = self._computed_properties[computed_key]
                    computed_prop.invalidate()
                    computed_prop.notify_change()

    def _handle_computed_property_change(self, computed_prop: ComputedProperty) -> None:
        """Handle when a computed property has changed."""
        # Find the key for this computed property and emit change event
        for key, prop in self._computed_properties.items():
            if prop is computed_prop:
                old_value = prop._cached_value if prop._is_cached else None
                new_value = prop.compute(self)
                self._emit_change_event(key, new_value, old_value)

                # Also invalidate any computed properties that depend on this one
                self._invalidate_dependent_computed_properties(key)
                break

    def add_computed_property(
        self,
        key: str,
        func: Callable[[Context], Any],
        dependencies: list[str] | None = None,
    ) -> None:
        """Add a computed property to the context.

        Args:
            key: The key where the computed value will be accessible
            func: Function that computes the value, takes Context as parameter
            dependencies: List of context keys this property depends on
        """
        computed_prop = ComputedProperty(func, dependencies)
        computed_prop.subscribe(self)
        self._computed_properties[key] = computed_prop

        # Build dependency graph
        for dep_key in computed_prop.dependencies:
            self._dependency_graph.add_dependency(dep_key, key)

    def remove_computed_property(self, key: str) -> None:
        """Remove a computed property from the context."""
        if key not in self._computed_properties:
            return

        computed_prop = self._computed_properties[key]

        # Clean up dependency graph
        for dep_key in computed_prop.dependencies:
            self._dependency_graph.remove_dependency(dep_key, key)

        del self._computed_properties[key]

    def add_transformation(self, key: str, func: Callable[[Any], Any]) -> None:
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
        """Remove all transformations for a specific key."""
        if key in self._transformations:
            del self._transformations[key]

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
        """Check if a key represents a computed property."""
        return key in self._computed_properties

    def computed_properties(self) -> dict[str, ComputedProperty]:
        """Get all computed properties in this context."""
        return self._computed_properties.copy()

    def transformations(self) -> dict[str, list[Transformation]]:
        """Get all transformations in this context."""
        return {k: v.copy() for k, v in self._transformations.items()}

    def query(
        self,
        pattern: str | None = None,
        key_filter: Callable[[str], bool] | None = None,
        value_filter: Callable[[Any], bool] | None = None,
        include_computed: bool = True,
    ) -> dict[str, Any]:
        """Query context data with various filtering options.

        Args:
            pattern: Regex pattern to match against keys
            key_filter: Function to filter keys
            value_filter: Function to filter values
            include_computed: Whether to include computed properties in results

        Returns:
            Dictionary of filtered key-value pairs
        """
        results = {}

        # Compile regex pattern if provided
        regex = re.compile(pattern) if pattern else None

        # Get all keys to check
        all_keys = list(self.keys())

        for key in all_keys:
            # Skip computed properties if not included
            if not include_computed and self.is_computed_property(key):
                continue

            # Apply key filters
            if regex and not regex.search(key):
                continue
            if key_filter and not key_filter(key):
                continue

            # Get value and apply value filter
            try:
                value = self[key]
                if value_filter and not value_filter(value):
                    continue
                results[key] = value
            except Exception:
                # Skip keys that can't be accessed
                continue

        return results

    def find_keys(self, pattern: str) -> list[str]:
        """Find all keys matching a regex pattern.

        Args:
            pattern: Regex pattern to match against keys

        Returns:
            List of matching keys
        """
        regex = re.compile(pattern)
        return [key for key in self.keys() if regex.search(key)]

    def find_values(self, predicate: Callable[[Any], bool]) -> dict[str, Any]:
        """Find all key-value pairs where the value matches a predicate.

        Args:
            predicate: Function that returns True for matching values

        Returns:
            Dictionary of matching key-value pairs
        """
        return self.query(value_filter=predicate)

    def filter_by_type(self, value_type: type) -> dict[str, Any]:
        """Filter context entries by value type.

        Args:
            value_type: Type to filter by

        Returns:
            Dictionary of entries with values of the specified type
        """
        return self.query(value_filter=lambda v: isinstance(v, value_type))

    def search(self, search_term: str, case_sensitive: bool = False) -> dict[str, Any]:
        """Search for keys or values containing a term.

        Args:
            search_term: Term to search for
            case_sensitive: Whether search should be case sensitive

        Returns:
            Dictionary of matching key-value pairs
        """
        if not case_sensitive:
            search_term = search_term.lower()

        def matches_search(key: str, value: Any) -> bool:
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

        results = {}
        for key in self.keys():
            try:
                value = self[key]
                if matches_search(key, value):
                    results[key] = value
            except Exception:
                continue

        return results

    def get_nested(self, path: str, delimiter: str = ".") -> Any:
        """Get a nested value using dot notation or custom delimiter.

        Args:
            path: Dot-separated path to the value (e.g., "user.profile.name")
            delimiter: Path delimiter (default: ".")

        Returns:
            The nested value

        Raises:
            KeyError: If any part of the path is not found
        """
        parts = path.split(delimiter)
        current = self[parts[0]]  # This will raise KeyError if first part not found

        for part in parts[1:]:
            if isinstance(current, dict):
                if part not in current:
                    raise KeyError(
                        f"Path '{path}' not found - missing '{part}' in {current}"
                    )
                current = current[part]
            elif hasattr(current, part):
                current = getattr(current, part)
            else:
                raise KeyError(
                    f"Path '{path}' not found - '{part}' not accessible in {type(current)}"
                )

        return current

    def set_nested(
        self, path: str, value: Any, delimiter: str = ".", create_missing: bool = True
    ) -> None:
        """Set a nested value using dot notation or custom delimiter.

        Args:
            path: Dot-separated path to set (e.g., "user.profile.name")
            value: Value to set
            delimiter: Path delimiter (default: ".")
            create_missing: Whether to create missing intermediate dictionaries
        """
        parts = path.split(delimiter)

        if len(parts) == 1:
            # Simple case - just set the value
            self[parts[0]] = value
            return

        # Navigate to parent and set final key
        current_value = self.get(parts[0])
        if current_value is None:
            if not create_missing:
                raise KeyError(f"Cannot set '{path}' - '{parts[0]}' does not exist")
            current_dict: dict[str, Any] = {}
            self[parts[0]] = current_dict
            current_value = current_dict

        # Navigate through intermediate parts
        for part in parts[1:-1]:
            if not isinstance(current_value, dict):
                if not create_missing:
                    raise KeyError(
                        f"Cannot set '{path}' - '{part}' is not a dictionary"
                    )
                # Cannot replace non-dict with dict, this is an error condition
                raise KeyError(f"Cannot set '{path}' - parent is not a dictionary")

            if part not in current_value:
                if not create_missing:
                    raise KeyError(f"Cannot set '{path}' - '{part}' does not exist")
                current_value[part] = {}

            current_value = current_value[part]

        # Set final value
        if not isinstance(current_value, dict):
            raise KeyError(f"Cannot set '{path}' - parent is not a dictionary")

        current_value[parts[-1]] = value

    def has_nested(self, path: str, delimiter: str = ".") -> bool:
        """Check if a nested path exists.

        Args:
            path: Dot-separated path to check
            delimiter: Path delimiter (default: ".")

        Returns:
            True if path exists, False otherwise
        """
        try:
            self.get_nested(path, delimiter)
            return True
        except KeyError:
            return False

    def flatten(
        self, delimiter: str = ".", max_depth: int | None = None
    ) -> dict[str, Any]:
        """Flatten nested dictionaries into dot-separated keys.

        Args:
            delimiter: Delimiter to use for flattened keys
            max_depth: Maximum depth to flatten (None for unlimited)

        Returns:
            Flattened dictionary
        """

        def _flatten_dict(
            obj: dict[str, Any], prefix: str = "", depth: int = 0
        ) -> dict[str, Any]:
            items = {}

            for key, value in obj.items():
                new_key = f"{prefix}{delimiter}{key}" if prefix else key

                if isinstance(value, dict) and (max_depth is None or depth < max_depth):
                    items.update(_flatten_dict(value, new_key, depth + 1))
                else:
                    items[new_key] = value

            return items

        # Get all regular values
        regular_data = {}
        for key in self.keys():
            if not self.is_computed_property(key):
                try:
                    value = self[key]
                    regular_data[key] = value
                except Exception:
                    continue

        return _flatten_dict(regular_data)
