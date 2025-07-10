"""Observer interfaces and implementations for Context change notifications."""

from __future__ import annotations

import time
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional

# Type aliases
ContextValue = Any


@dataclass(frozen=True)
class ContextChangeEvent:
    """Represents a change event in the context."""

    key: str
    old_value: ContextValue
    new_value: ContextValue
    timestamp: float
    context_id: int
    change_type: str  # 'set', 'computed_update', 'transformation_applied'
    metadata: Dict[str, Any]

    def __post_init__(self) -> None:
        """Validate the event data."""
        if self.timestamp <= 0:
            raise ValueError("Event timestamp must be positive")


class ContextObserver(ABC):
    """Abstract base class for context change observers."""

    @abstractmethod
    def on_change(self, event: ContextChangeEvent) -> None:
        """Handle a context change event.

        Args:
            event: The change event that occurred
        """
        pass

    def on_error(self, event: ContextChangeEvent, error: Exception) -> None:
        """Handle an error that occurred during change processing.

        Args:
            event: The change event that caused the error
            error: The exception that was raised

        Note:
            Default implementation does nothing. Override to handle errors.
        """
        pass


class FunctionObserver(ContextObserver):
    """Observer that wraps a simple function."""

    def __init__(
        self,
        on_change_fn: Callable[[ContextChangeEvent], None],
        on_error_fn: Optional[Callable[[ContextChangeEvent, Exception], None]] = None,
    ) -> None:
        """Initialize with callback functions.

        Args:
            on_change_fn: Function to call when a change occurs
            on_error_fn: Optional function to call when an error occurs
        """
        super().__init__()
        self._on_change_fn = on_change_fn
        self._on_error_fn = on_error_fn

    def on_change(self, event: ContextChangeEvent) -> None:
        """Handle change by calling the wrapped function."""
        self._on_change_fn(event)

    def on_error(self, event: ContextChangeEvent, error: Exception) -> None:
        """Handle error by calling the wrapped function if provided."""
        if self._on_error_fn:
            self._on_error_fn(event, error)


class LoggingObserver(ContextObserver):
    """Observer that logs change events."""

    def __init__(self, logger: Any = None, level: str = "INFO") -> None:
        """Initialize the logging observer.

        Args:
            logger: Logger instance to use (uses print if None)
            level: Log level for change events
        """
        super().__init__()
        self.logger = logger
        self.level = level.upper()

    def on_change(self, event: ContextChangeEvent) -> None:
        """Log the change event."""
        message = (
            f"Context change: {event.key} = {event.new_value} "
            f"(was: {event.old_value}) [{event.change_type}]"
        )

        if self.logger:
            log_method = getattr(self.logger, self.level.lower(), None)
            if log_method:
                log_method(message)
        else:
            print(f"[{self.level}] {message}")

    def on_error(self, event: ContextChangeEvent, error: Exception) -> None:
        """Log the error."""
        message = f"Error processing change for {event.key}: {error}"

        if self.logger:
            self.logger.error(message)
        else:
            print(f"[ERROR] {message}")


class FilteringObserver(ContextObserver):
    """Observer that filters events before delegating to another observer."""

    def __init__(
        self,
        delegate: ContextObserver,
        key_filter: Optional[Callable[[str], bool]] = None,
        value_filter: Optional[Callable[[ContextValue], bool]] = None,
        change_type_filter: Optional[List[str]] = None,
    ) -> None:
        """Initialize the filtering observer.

        Args:
            delegate: Observer to delegate filtered events to
            key_filter: Function to filter by key (return True to include)
            value_filter: Function to filter by new value (return True to include)
            change_type_filter: List of change types to include
        """
        super().__init__()
        self.delegate = delegate
        self.key_filter = key_filter
        self.value_filter = value_filter
        self.change_type_filter = (
            set(change_type_filter) if change_type_filter else None
        )

    def on_change(self, event: ContextChangeEvent) -> None:
        """Filter and delegate the change event."""
        if self._should_process(event):
            self.delegate.on_change(event)

    def on_error(self, event: ContextChangeEvent, error: Exception) -> None:
        """Delegate error handling."""
        self.delegate.on_error(event, error)

    def _should_process(self, event: ContextChangeEvent) -> bool:
        """Check if event should be processed based on filters."""
        if self.key_filter and not self.key_filter(event.key):
            return False

        if self.value_filter and not self.value_filter(event.new_value):
            return False

        if self.change_type_filter and event.change_type not in self.change_type_filter:
            return False

        return True


class CompositeObserver(ContextObserver):
    """Observer that delegates to multiple other observers."""

    def __init__(self, observers: List[ContextObserver]) -> None:
        """Initialize with a list of observers.

        Args:
            observers: List of observers to delegate to
        """
        super().__init__()
        self.observers = observers.copy()

    def add_observer(self, observer: ContextObserver) -> None:
        """Add an observer to the composite."""
        self.observers.append(observer)

    def remove_observer(self, observer: ContextObserver) -> None:
        """Remove an observer from the composite."""
        if observer in self.observers:
            self.observers.remove(observer)

    def on_change(self, event: ContextChangeEvent) -> None:
        """Notify all observers of the change."""
        for observer in self.observers:
            try:
                observer.on_change(event)
            except Exception as e:
                observer.on_error(event, e)

    def on_error(self, event: ContextChangeEvent, error: Exception) -> None:
        """Notify all observers of the error."""
        for observer in self.observers:
            try:
                observer.on_error(event, error)
            except Exception:
                # If error handling itself fails, we can't do much
                pass


class ChangeNotifier:
    """Manages observers and emits change events."""

    def __init__(self) -> None:
        """Initialize the change notifier."""
        super().__init__()
        self._observers: List[ContextObserver] = []

    def add_observer(self, observer: ContextObserver) -> None:
        """Add an observer to receive change notifications.

        Args:
            observer: Observer to add
        """
        if observer not in self._observers:
            self._observers.append(observer)

    def remove_observer(self, observer: ContextObserver) -> None:
        """Remove an observer from receiving change notifications.

        Args:
            observer: Observer to remove
        """
        if observer in self._observers:
            self._observers.remove(observer)

    def clear_observers(self) -> None:
        """Remove all observers."""
        self._observers.clear()

    def emit_change(
        self,
        key: str,
        old_value: ContextValue,
        new_value: ContextValue,
        context_id: int,
        change_type: str = "set",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Emit a change event to all observers.

        Args:
            key: The key that changed
            old_value: The previous value
            new_value: The new value
            context_id: ID of the context that changed
            change_type: Type of change that occurred
            metadata: Additional metadata about the change
        """
        if not self._observers:
            return

        event = ContextChangeEvent(
            key=key,
            old_value=old_value,
            new_value=new_value,
            timestamp=time.time(),
            context_id=context_id,
            change_type=change_type,
            metadata=metadata or {},
        )

        for observer in self._observers:
            try:
                observer.on_change(event)
            except Exception as e:
                try:
                    observer.on_error(event, e)
                except Exception:
                    # If error handling fails, we can't do much more
                    pass

    def has_observers(self) -> bool:
        """Check if there are any registered observers."""
        return len(self._observers) > 0

    def observer_count(self) -> int:
        """Get the number of registered observers."""
        return len(self._observers)
