"""Tests for Context.get_history_size method."""

from context.main import Context


class TestContextGetHistorySize:
    """Test suite for Context.get_history_size method."""

    def test_get_history_size_empty_history(self) -> None:
        """Test get_history_size with empty history."""
        context = Context()

        assert context.get_history_size() == 0

    def test_get_history_size_after_single_change(self) -> None:
        """Test get_history_size after a single change."""
        context = Context()

        context.set("key1", "value1")

        assert context.get_history_size() == 1

    def test_get_history_size_after_multiple_changes(self) -> None:
        """Test get_history_size after multiple changes."""
        context = Context()

        context.set("key1", "value1")
        context.set("key2", "value2")
        context.set("key3", "value3")

        assert context.get_history_size() == 3

    def test_get_history_size_after_same_key_changes(self) -> None:
        """Test get_history_size after changing the same key multiple times."""
        context = Context()

        context.set("key1", "value1")
        context.set("key1", "value2")
        context.set("key1", "value3")

        # Each change should be recorded separately
        assert context.get_history_size() == 3

    def test_get_history_size_after_clear_history(self) -> None:
        """Test get_history_size after clearing history."""
        context = Context()

        context.set("key1", "value1")
        context.set("key2", "value2")
        assert context.get_history_size() == 2

        context.clear_history()
        assert context.get_history_size() == 0

    def test_get_history_size_with_setitem(self) -> None:
        """Test get_history_size with __setitem__ method."""
        context = Context()

        context["key1"] = "value1"
        context["key2"] = "value2"

        assert context.get_history_size() == 2

    def test_get_history_size_return_type(self) -> None:
        """Test that get_history_size returns an integer."""
        context = Context()

        context.set("key1", "value1")

        size = context.get_history_size()
        assert isinstance(size, int)
        assert size >= 0

    def test_get_history_size_idempotent(self) -> None:
        """Test that get_history_size is idempotent (no side effects)."""
        context = Context()

        context.set("key1", "value1")

        # Multiple calls should return same result
        size1 = context.get_history_size()
        size2 = context.get_history_size()
        size3 = context.get_history_size()

        assert size1 == size2 == size3 == 1

    def test_get_history_size_delegates_to_history_tracker(self) -> None:
        """Test that get_history_size delegates to the history tracker."""
        context = Context()

        # Direct comparison with history tracker
        assert context.get_history_size() == context._history_tracker.get_history_size()

        context.set("key1", "value1")
        assert context.get_history_size() == context._history_tracker.get_history_size()

        context.set("key2", "value2")
        assert context.get_history_size() == context._history_tracker.get_history_size()
