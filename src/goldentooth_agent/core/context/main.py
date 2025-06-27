from __future__ import annotations

import json
import time
from collections.abc import Iterator
from typing import Any, TypeVar

from pyee import EventEmitter
from pyee.asyncio import AsyncIOEventEmitter

from goldentooth_agent.core.event import AsyncEventFlow, SyncEventFlow
from goldentooth_agent.core.flow import Flow

from .frame import ContextFrame

T = TypeVar("T")


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

    def get(self, key: str, default: T | None = None) -> T | None:
        """Get the value for a key, searching through all frames."""
        for frame in reversed(self.frames):
            if key in frame:
                return frame[key]  # type: ignore[no-any-return]
        return default

    def __getitem__(self, key: str) -> Any:
        """Get the value for a key, raising KeyError if not found."""
        for frame in reversed(self.frames):
            if key in frame:
                return frame[key]
        raise KeyError(f"Context key '{key}' not found")

    def __setitem__(self, key: str, value: Any) -> None:
        """Set a value for a key in the current frame and notify subscribers/emit events."""
        old_value = self.get(key)
        self.frames[-1][key] = value

        # Emit events through EventFlow system
        self._emit_change_event(key, value, old_value)

    def __contains__(self, key: str) -> bool:
        """Check if a key exists in any of the frames."""
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
        """Create a fork of the current context with copies of the frames."""
        return Context([frame.copy() for frame in self.frames])

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

    def keys(self) -> Iterator[str]:
        """Yield all unique keys from the context, starting from the most recent frame."""
        seen = set()
        for frame in reversed(self.frames):
            for k in frame.data:
                if k not in seen:
                    yield k
                    seen.add(k)

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
