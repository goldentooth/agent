"""Tests for Context._record_change private method."""

from context.main import Context


class TestContextRecordChange:
    """Test suite for Context._record_change private method."""

    def test_record_change_basic(self) -> None:
        """Test basic change recording functionality."""
        context = Context()

        # Record a change
        context._record_change("test_key", None, "new_value")

        # Verify change was recorded in history
        history = context.get_change_history()
        assert len(history) == 1
        assert history[0].key == "test_key"
        assert history[0].old_value is None
        assert history[0].new_value == "new_value"
        assert history[0].context_id == id(context)

    def test_record_change_with_old_value(self) -> None:
        """Test recording change with existing old value."""
        context = Context()

        # Record a change with old value
        context._record_change("key", "old_value", "new_value")

        # Verify change was recorded correctly
        history = context.get_change_history()
        assert len(history) == 1
        assert history[0].key == "key"
        assert history[0].old_value == "old_value"
        assert history[0].new_value == "new_value"

    def test_record_change_multiple_calls(self) -> None:
        """Test multiple change recordings."""
        context = Context()

        # Record multiple changes
        context._record_change("key1", None, "value1")
        context._record_change("key2", "old", "new")
        context._record_change("key1", "value1", "updated")

        # Verify all changes were recorded
        history = context.get_change_history()
        assert len(history) == 3

        # Verify the most recent changes in order
        expected_changes = [
            ("key1", "value1", "updated"),
            ("key2", "old", "new"),
            ("key1", None, "value1"),
        ]

        for i, (key, old_val, new_val) in enumerate(expected_changes):
            assert history[i].key == key
            assert history[i].old_value == old_val
            assert history[i].new_value == new_val

    def test_record_change_with_complex_values(self) -> None:
        """Test recording changes with complex data types."""
        context = Context()

        old_dict = {"a": 1, "b": [1, 2, 3]}
        new_dict = {"a": 2, "b": [1, 2, 3, 4], "c": "new"}

        context._record_change("complex", old_dict, new_dict)

        history = context.get_change_history()
        assert len(history) == 1
        assert history[0].key == "complex"
        assert history[0].old_value == old_dict
        assert history[0].new_value == new_dict

    def test_record_change_with_none_values(self) -> None:
        """Test recording changes with None values."""
        context = Context()

        # Test old value as None (new key)
        context._record_change("new_key", None, "value")

        # Test new value as None (deletion)
        context._record_change("deleted_key", "old_value", None)

        # Test both as None
        context._record_change("both_none", None, None)

        history = context.get_change_history()
        assert len(history) == 3

        assert history[2].old_value is None
        assert history[2].new_value == "value"

        assert history[1].old_value == "old_value"
        assert history[1].new_value is None

        assert history[0].old_value is None
        assert history[0].new_value is None

    def test_record_change_preserves_context_id(self) -> None:
        """Test that context ID is correctly recorded."""
        context1 = Context()
        context2 = Context()

        context1._record_change("key", "old", "new")
        context2._record_change("key", "old", "new")

        history1 = context1.get_change_history()
        history2 = context2.get_change_history()

        assert len(history1) == 1
        assert len(history2) == 1

        assert history1[0].context_id == id(context1)
        assert history2[0].context_id == id(context2)
        assert history1[0].context_id != history2[0].context_id

    def test_record_change_with_timestamps(self) -> None:
        """Test that timestamps are recorded for changes."""
        import time

        context = Context()

        start_time = time.time()
        context._record_change("key", "old", "new")
        end_time = time.time()

        history = context.get_change_history()
        assert len(history) == 1

        # Verify timestamp is within expected range
        assert start_time <= history[0].timestamp <= end_time

    def test_record_change_with_special_characters(self) -> None:
        """Test recording changes with special characters in keys and values."""
        context = Context()

        special_key = "key.with-special@chars[0]"
        special_value = "value with unicode: 测试 🔑"

        context._record_change(special_key, None, special_value)

        history = context.get_change_history()
        assert len(history) == 1
        assert history[0].key == special_key
        assert history[0].new_value == special_value

    def test_record_change_respects_history_size_limit(self) -> None:
        """Test that change recording respects history size limits."""
        context = Context()

        # Set a small history size limit
        context.set_max_history_size(3)

        # Record more changes than the limit
        for i in range(5):
            context._record_change(f"key_{i}", None, f"value_{i}")

        # Verify only the most recent changes are kept
        history = context.get_change_history()
        assert len(history) == 3

        # Verify the most recent changes are preserved
        assert history[0].key == "key_4"
        assert history[1].key == "key_3"
        assert history[2].key == "key_2"

    def test_record_change_with_empty_strings(self) -> None:
        """Test recording changes with empty string values."""
        context = Context()

        context._record_change("empty_key", "", "value")
        context._record_change("key_to_empty", "value", "")
        context._record_change("both_empty", "", "")

        history = context.get_change_history()
        assert len(history) == 3

        assert history[2].old_value == ""
        assert history[2].new_value == "value"

        assert history[1].old_value == "value"
        assert history[1].new_value == ""

        assert history[0].old_value == ""
        assert history[0].new_value == ""

    def test_record_change_delegation_to_history_tracker(self) -> None:
        """Test that _record_change properly delegates to history tracker."""
        context = Context()

        # Record a change
        context._record_change("test", "old", "new")

        # Verify it shows up in history tracker
        tracker_history = context._history_tracker.get_history()
        assert len(tracker_history) == 1
        assert tracker_history[0].key == "test"
        assert tracker_history[0].old_value == "old"
        assert tracker_history[0].new_value == "new"

    def test_record_change_with_nested_data_structures(self) -> None:
        """Test recording changes with deeply nested data structures."""
        context = Context()

        nested_old = {"level1": {"level2": {"level3": ["a", "b", {"level4": "deep"}]}}}

        nested_new = {
            "level1": {"level2": {"level3": ["a", "b", {"level4": "deeper"}]}}
        }

        context._record_change("nested", nested_old, nested_new)

        history = context.get_change_history()
        assert len(history) == 1
        assert history[0].old_value == nested_old
        assert history[0].new_value == nested_new

    def test_record_change_method_signature(self) -> None:
        """Test that _record_change method has correct signature."""
        context = Context()

        # Verify method exists and is callable
        assert hasattr(context, "_record_change")
        assert callable(context._record_change)

        # Test with all required parameters
        context._record_change("key", "old", "new")

        # Verify it worked
        history = context.get_change_history()
        assert len(history) == 1

    def test_record_change_return_type(self) -> None:
        """Test that _record_change returns None."""
        context = Context()

        # Method should return None
        context._record_change("key", "old", "new")

        # Verify it worked (implicit None return)
        history = context.get_change_history()
        assert len(history) == 1

    def test_record_change_with_boolean_values(self) -> None:
        """Test recording changes with boolean values."""
        context = Context()

        context._record_change("bool_key", False, True)
        context._record_change("false_key", True, False)

        history = context.get_change_history()
        assert len(history) == 2

        assert history[1].old_value is False
        assert history[1].new_value is True

        assert history[0].old_value is True
        assert history[0].new_value is False

    def test_record_change_with_numeric_values(self) -> None:
        """Test recording changes with various numeric types."""
        context = Context()

        context._record_change("int_key", 1, 2)
        context._record_change("float_key", 1.5, 2.7)
        context._record_change("zero_key", 0, 1)
        context._record_change("negative_key", -1, -2)

        history = context.get_change_history()
        assert len(history) == 4

        assert history[3].old_value == 1
        assert history[3].new_value == 2

        assert history[2].old_value == 1.5
        assert history[2].new_value == 2.7
