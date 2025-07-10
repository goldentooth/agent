"""Tests for Context observer system."""

import time
from unittest.mock import Mock, call

import pytest

from context.main import Context
from context.observers import (
    ChangeNotifier,
    CompositeObserver,
    ContextChangeEvent,
    ContextObserver,
    FilteringObserver,
    FunctionObserver,
    LoggingObserver,
)


class TestContextChangeEvent:
    """Test suite for ContextChangeEvent."""

    def test_change_event_creation(self) -> None:
        """Test basic change event creation."""
        timestamp = time.time()
        event = ContextChangeEvent(
            key="test_key",
            old_value="old",
            new_value="new",
            timestamp=timestamp,
            context_id=12345,
            change_type="set",
            metadata={"source": "test"},
        )

        assert event.key == "test_key"
        assert event.old_value == "old"
        assert event.new_value == "new"
        assert event.timestamp == timestamp
        assert event.context_id == 12345
        assert event.change_type == "set"
        assert event.metadata == {"source": "test"}

    def test_change_event_immutable(self) -> None:
        """Test that change events are immutable."""
        event = ContextChangeEvent(
            key="test",
            old_value=None,
            new_value="value",
            timestamp=time.time(),
            context_id=1,
            change_type="set",
            metadata={},
        )

        with pytest.raises(AttributeError):
            event.key = "modified"  # type: ignore[misc]

    def test_change_event_validation(self) -> None:
        """Test change event validation."""
        with pytest.raises(ValueError, match="Event timestamp must be positive"):
            ContextChangeEvent(
                key="test",
                old_value=None,
                new_value="value",
                timestamp=-1.0,
                context_id=1,
                change_type="set",
                metadata={},
            )


class TestFunctionObserver:
    """Test suite for FunctionObserver."""

    def test_function_observer_on_change(self) -> None:
        """Test function observer calls the provided function."""
        mock_fn = Mock()
        observer = FunctionObserver(mock_fn)

        event = ContextChangeEvent(
            key="test",
            old_value=None,
            new_value="value",
            timestamp=time.time(),
            context_id=1,
            change_type="set",
            metadata={},
        )

        observer.on_change(event)
        mock_fn.assert_called_once_with(event)

    def test_function_observer_on_error(self) -> None:
        """Test function observer error handling."""
        on_change_fn = Mock()
        on_error_fn = Mock()
        observer = FunctionObserver(on_change_fn, on_error_fn)

        event = ContextChangeEvent(
            key="test",
            old_value=None,
            new_value="value",
            timestamp=time.time(),
            context_id=1,
            change_type="set",
            metadata={},
        )
        error = Exception("test error")

        observer.on_error(event, error)
        on_error_fn.assert_called_once_with(event, error)

    def test_function_observer_no_error_handler(self) -> None:
        """Test function observer without error handler."""
        on_change_fn = Mock()
        observer = FunctionObserver(on_change_fn)

        event = ContextChangeEvent(
            key="test",
            old_value=None,
            new_value="value",
            timestamp=time.time(),
            context_id=1,
            change_type="set",
            metadata={},
        )
        error = Exception("test error")

        # Should not raise even without error handler
        observer.on_error(event, error)


class TestLoggingObserver:
    """Test suite for LoggingObserver."""

    def test_logging_observer_with_print(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Test logging observer using print."""
        observer = LoggingObserver()

        event = ContextChangeEvent(
            key="test_key",
            old_value="old",
            new_value="new",
            timestamp=time.time(),
            context_id=1,
            change_type="set",
            metadata={},
        )

        observer.on_change(event)

        captured = capsys.readouterr()
        assert "Context change: test_key = new (was: old) [set]" in captured.out

    def test_logging_observer_with_logger(self) -> None:
        """Test logging observer with a mock logger."""
        mock_logger = Mock()
        observer = LoggingObserver(mock_logger, "DEBUG")

        event = ContextChangeEvent(
            key="test_key",
            old_value="old",
            new_value="new",
            timestamp=time.time(),
            context_id=1,
            change_type="set",
            metadata={},
        )

        observer.on_change(event)

        mock_logger.debug.assert_called_once()
        call_args = mock_logger.debug.call_args[0][0]
        assert "Context change: test_key = new (was: old) [set]" in call_args

    def test_logging_observer_error_handling(self) -> None:
        """Test logging observer error handling."""
        mock_logger = Mock()
        observer = LoggingObserver(mock_logger)

        event = ContextChangeEvent(
            key="test",
            old_value=None,
            new_value="value",
            timestamp=time.time(),
            context_id=1,
            change_type="set",
            metadata={},
        )
        error = Exception("test error")

        observer.on_error(event, error)

        mock_logger.error.assert_called_once()
        call_args = mock_logger.error.call_args[0][0]
        assert "Error processing change for test: test error" in call_args


class TestFilteringObserver:
    """Test suite for FilteringObserver."""

    def test_filtering_observer_key_filter(self) -> None:
        """Test filtering observer with key filter."""
        delegate = Mock(spec=ContextObserver)
        observer = FilteringObserver(
            delegate, key_filter=lambda key: key.startswith("allowed_")
        )

        # This event should be filtered out
        event1 = ContextChangeEvent(
            key="blocked_key",
            old_value=None,
            new_value="value",
            timestamp=time.time(),
            context_id=1,
            change_type="set",
            metadata={},
        )

        # This event should pass through
        event2 = ContextChangeEvent(
            key="allowed_key",
            old_value=None,
            new_value="value",
            timestamp=time.time(),
            context_id=1,
            change_type="set",
            metadata={},
        )

        observer.on_change(event1)
        observer.on_change(event2)

        # Only the allowed event should reach the delegate
        delegate.on_change.assert_called_once_with(event2)

    def test_filtering_observer_change_type_filter(self) -> None:
        """Test filtering observer with change type filter."""
        delegate = Mock(spec=ContextObserver)
        observer = FilteringObserver(
            delegate, change_type_filter=["set", "computed_update"]
        )

        # This event should pass through
        event1 = ContextChangeEvent(
            key="test",
            old_value=None,
            new_value="value",
            timestamp=time.time(),
            context_id=1,
            change_type="set",
            metadata={},
        )

        # This event should be filtered out
        event2 = ContextChangeEvent(
            key="test",
            old_value=None,
            new_value="value",
            timestamp=time.time(),
            context_id=1,
            change_type="transformation_applied",
            metadata={},
        )

        observer.on_change(event1)
        observer.on_change(event2)

        # Only the set event should reach the delegate
        delegate.on_change.assert_called_once_with(event1)

    def test_filtering_observer_error_delegation(self) -> None:
        """Test that filtering observer delegates errors."""
        delegate = Mock(spec=ContextObserver)
        observer = FilteringObserver(delegate)

        event = ContextChangeEvent(
            key="test",
            old_value=None,
            new_value="value",
            timestamp=time.time(),
            context_id=1,
            change_type="set",
            metadata={},
        )
        error = Exception("test error")

        observer.on_error(event, error)

        delegate.on_error.assert_called_once_with(event, error)


class TestCompositeObserver:
    """Test suite for CompositeObserver."""

    def test_composite_observer_delegates_to_all(self) -> None:
        """Test that composite observer delegates to all child observers."""
        observer1 = Mock(spec=ContextObserver)
        observer2 = Mock(spec=ContextObserver)
        composite = CompositeObserver([observer1, observer2])

        event = ContextChangeEvent(
            key="test",
            old_value=None,
            new_value="value",
            timestamp=time.time(),
            context_id=1,
            change_type="set",
            metadata={},
        )

        composite.on_change(event)

        observer1.on_change.assert_called_once_with(event)
        observer2.on_change.assert_called_once_with(event)

    def test_composite_observer_handles_observer_errors(self) -> None:
        """Test that composite observer handles errors from child observers."""
        observer1 = Mock(spec=ContextObserver)
        observer2 = Mock(spec=ContextObserver)

        # Make observer1 raise an exception
        error = Exception("observer1 error")
        observer1.on_change.side_effect = error

        composite = CompositeObserver([observer1, observer2])

        event = ContextChangeEvent(
            key="test",
            old_value=None,
            new_value="value",
            timestamp=time.time(),
            context_id=1,
            change_type="set",
            metadata={},
        )

        composite.on_change(event)

        # Both observers should be called
        observer1.on_change.assert_called_once_with(event)
        observer2.on_change.assert_called_once_with(event)

        # Error handler should be called for observer1
        observer1.on_error.assert_called_once_with(event, error)

    def test_composite_observer_add_remove(self) -> None:
        """Test adding and removing observers from composite."""
        observer1 = Mock(spec=ContextObserver)
        observer2 = Mock(spec=ContextObserver)
        composite = CompositeObserver([observer1])

        # Add observer2
        composite.add_observer(observer2)
        assert len(composite.observers) == 2

        # Remove observer1
        composite.remove_observer(observer1)
        assert len(composite.observers) == 1
        assert observer2 in composite.observers


class TestChangeNotifier:
    """Test suite for ChangeNotifier."""

    def test_change_notifier_add_remove_observers(self) -> None:
        """Test adding and removing observers."""
        notifier = ChangeNotifier()
        observer = Mock(spec=ContextObserver)

        assert not notifier.has_observers()
        assert notifier.observer_count() == 0

        notifier.add_observer(observer)
        assert notifier.has_observers()
        assert notifier.observer_count() == 1

        notifier.remove_observer(observer)
        assert not notifier.has_observers()
        assert notifier.observer_count() == 0

    def test_change_notifier_no_duplicate_observers(self) -> None:
        """Test that observers are not added multiple times."""
        notifier = ChangeNotifier()
        observer = Mock(spec=ContextObserver)

        notifier.add_observer(observer)
        notifier.add_observer(observer)  # Add same observer again

        assert notifier.observer_count() == 1

    def test_change_notifier_emit_change(self) -> None:
        """Test emitting change events."""
        notifier = ChangeNotifier()
        observer1 = Mock(spec=ContextObserver)
        observer2 = Mock(spec=ContextObserver)

        notifier.add_observer(observer1)
        notifier.add_observer(observer2)

        notifier.emit_change(
            key="test_key",
            old_value="old",
            new_value="new",
            context_id=12345,
            change_type="set",
            metadata={"test": True},
        )

        self._verify_observers_received_event(observer1, observer2)
        self._verify_event_details(observer1)

    def _verify_observers_received_event(
        self, observer1: Mock, observer2: Mock
    ) -> None:
        """Verify both observers received the event."""
        assert observer1.on_change.call_count == 1
        assert observer2.on_change.call_count == 1

    def _verify_event_details(self, observer: Mock) -> None:
        """Verify the event details are correct."""
        event = observer.on_change.call_args[0][0]
        assert event.key == "test_key"
        assert event.old_value == "old"
        assert event.new_value == "new"
        assert event.context_id == 12345
        assert event.change_type == "set"
        assert event.metadata == {"test": True}

    def test_change_notifier_handles_observer_errors(self) -> None:
        """Test that notifier handles observer errors gracefully."""
        notifier = ChangeNotifier()
        observer1 = Mock(spec=ContextObserver)
        observer2 = Mock(spec=ContextObserver)

        # Make observer1 raise an exception
        error = Exception("observer error")
        observer1.on_change.side_effect = error

        notifier.add_observer(observer1)
        notifier.add_observer(observer2)

        notifier.emit_change(
            key="test",
            old_value=None,
            new_value="value",
            context_id=1,
            change_type="set",
        )

        # Both observers should be called
        observer1.on_change.assert_called_once()
        observer2.on_change.assert_called_once()

        # Error handler should be called for observer1
        observer1.on_error.assert_called_once()

    def test_change_notifier_clear_observers(self) -> None:
        """Test clearing all observers."""
        notifier = ChangeNotifier()
        observer1 = Mock(spec=ContextObserver)
        observer2 = Mock(spec=ContextObserver)

        notifier.add_observer(observer1)
        notifier.add_observer(observer2)
        assert notifier.observer_count() == 2

        notifier.clear_observers()
        assert notifier.observer_count() == 0
        assert not notifier.has_observers()


class TestContextObserverIntegration:
    """Test suite for Context and observer integration."""

    def test_context_observer_registration(self) -> None:
        """Test registering observers with Context."""
        context = Context()
        observer = Mock(spec=ContextObserver)

        assert not context.has_observers()

        context.add_observer(observer)
        assert context.has_observers()

        context.remove_observer(observer)
        assert not context.has_observers()

    def test_context_observer_notification_on_set(self) -> None:
        """Test that observers are notified when values are set."""
        context = Context()
        observer = Mock(spec=ContextObserver)
        context.add_observer(observer)

        context.set("test_key", "test_value")

        observer.on_change.assert_called_once()
        event = observer.on_change.call_args[0][0]
        assert event.key == "test_key"
        assert event.old_value is None
        assert event.new_value == "test_value"
        assert event.change_type == "set"

    def test_context_observer_notification_on_update(self) -> None:
        """Test that observers are notified when values are updated."""
        context = Context()
        observer = Mock(spec=ContextObserver)

        # Set initial value
        context.set("test_key", "initial_value")

        # Add observer after initial set
        context.add_observer(observer)

        # Update the value
        context.set("test_key", "updated_value")

        observer.on_change.assert_called_once()
        event = observer.on_change.call_args[0][0]
        assert event.key == "test_key"
        assert event.old_value == "initial_value"
        assert event.new_value == "updated_value"
        assert event.change_type == "set"

    def test_context_observer_with_transformations(self) -> None:
        """Test observer notifications with transformations applied."""
        context = Context()
        observer = Mock(spec=ContextObserver)
        context.add_observer(observer)

        # Add a transformation
        context.add_transformation("test_key", str.upper)

        # Set a value that will be transformed
        context.set("test_key", "lowercase")

        observer.on_change.assert_called_once()
        event = observer.on_change.call_args[0][0]
        assert event.key == "test_key"
        assert event.old_value is None
        assert event.new_value == "LOWERCASE"  # Transformed value
        assert event.change_type == "set"

    def test_context_observer_computed_properties(self) -> None:
        """Test observer notifications for computed property changes."""
        context = Context()
        observer = Mock(spec=ContextObserver)
        context.add_observer(observer)

        # Add a computed property
        def compute_full_name(ctx: Context) -> str:
            first = ctx.get("first_name", "")
            last = ctx.get("last_name", "")
            return f"{first} {last}".strip()

        context.add_computed_property(
            "full_name", compute_full_name, ["first_name", "last_name"]
        )

        # Set values that the computed property depends on
        context.set("first_name", "John")

        # Access the computed property to trigger computation
        _ = context.get("full_name")

        # Should have notifications for both the set and computed update
        assert observer.on_change.call_count == 2

        # Check the computed property notification
        calls = observer.on_change.call_args_list
        computed_event = calls[1][0][0]  # Second call
        assert computed_event.key == "full_name"
        assert computed_event.change_type == "computed_update"
        assert computed_event.metadata["computed_property"] is True

    def test_context_multiple_observers(self) -> None:
        """Test that multiple observers all receive notifications."""
        context = Context()
        observer1 = Mock(spec=ContextObserver)
        observer2 = Mock(spec=ContextObserver)

        context.add_observer(observer1)
        context.add_observer(observer2)

        context.set("test_key", "test_value")

        observer1.on_change.assert_called_once()
        observer2.on_change.assert_called_once()

        # Both should receive the same event
        event1 = observer1.on_change.call_args[0][0]
        event2 = observer2.on_change.call_args[0][0]
        assert event1.key == event2.key
        assert event1.new_value == event2.new_value

    def test_context_clear_observers(self) -> None:
        """Test clearing all observers from context."""
        context = Context()
        observer1 = Mock(spec=ContextObserver)
        observer2 = Mock(spec=ContextObserver)

        context.add_observer(observer1)
        context.add_observer(observer2)
        assert context.has_observers()

        context.clear_observers()
        assert not context.has_observers()

        # No notifications should be sent after clearing
        context.set("test_key", "test_value")
        observer1.on_change.assert_not_called()
        observer2.on_change.assert_not_called()


class TestObserverUsageExamples:
    """Test suite showing practical observer usage examples."""

    def test_logging_observer_integration(self) -> None:
        """Test practical usage of logging observer."""
        context = Context()
        mock_logger = Mock()

        logging_observer = LoggingObserver(mock_logger, "INFO")
        context.add_observer(logging_observer)

        context.set("user_id", 12345)
        context.set("user_name", "Alice")

        # Should have logged both changes
        assert mock_logger.info.call_count == 2

    def test_filtering_observer_integration(self) -> None:
        """Test practical usage of filtering observer."""
        context = Context()
        important_changes = []

        def capture_important(event: ContextChangeEvent) -> None:
            important_changes.append(event.key)

        # Only capture changes to keys starting with "important_"
        filtering_observer = FilteringObserver(
            FunctionObserver(capture_important),
            key_filter=lambda key: key.startswith("important_"),
        )
        context.add_observer(filtering_observer)

        context.set("important_config", "value1")
        context.set("debug_info", "value2")
        context.set("important_setting", "value3")

        # Only important keys should be captured
        assert important_changes == ["important_config", "important_setting"]

    def test_composite_observer_integration(self) -> None:
        """Test practical usage of composite observer."""
        context = Context()
        log_calls = []
        audit_calls = []

        def log_change(event: ContextChangeEvent) -> None:
            log_calls.append(f"LOG: {event.key} = {event.new_value}")

        def audit_change(event: ContextChangeEvent) -> None:
            audit_calls.append(f"AUDIT: {event.key} changed")

        # Combine multiple observers
        composite = CompositeObserver(
            [FunctionObserver(log_change), FunctionObserver(audit_change)]
        )
        context.add_observer(composite)

        context.set("user_action", "login")

        assert log_calls == ["LOG: user_action = login"]
        assert audit_calls == ["AUDIT: user_action changed"]
