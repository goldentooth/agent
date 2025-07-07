"""Tests for ContextChangeEvent class."""

import time
from unittest.mock import patch

import pytest

from context.history_tracker import ContextChangeEvent


class TestContextChangeEvent:
    """Test suite for ContextChangeEvent class."""

    def test_init_basic(self) -> None:
        """Test basic initialization of ContextChangeEvent."""
        key = "test_key"
        old_value = "old"
        new_value = "new"
        context_id = 123

        # Mock time.time() to ensure consistent timestamp
        with patch("time.time", return_value=1000.0):
            event = ContextChangeEvent(key, old_value, new_value, context_id)

        assert event.key == key
        assert event.old_value == old_value
        assert event.new_value == new_value
        assert event.context_id == context_id
        assert event.timestamp == 1000.0

    def test_init_with_none_values(self) -> None:
        """Test initialization with None values."""
        event = ContextChangeEvent("key", None, None, 0)

        assert event.key == "key"
        assert event.old_value is None
        assert event.new_value is None
        assert event.context_id == 0
        assert isinstance(event.timestamp, float)

    def test_init_with_complex_values(self) -> None:
        """Test initialization with complex data types."""
        key = "complex_key"
        old_value = {"nested": {"data": [1, 2, 3]}}
        new_value = [{"item": 1}, {"item": 2}]
        context_id = 456

        event = ContextChangeEvent(key, old_value, new_value, context_id)

        assert event.key == key
        assert event.old_value == old_value
        assert event.new_value == new_value
        assert event.context_id == context_id

    def test_init_with_empty_string_key(self) -> None:
        """Test initialization with empty string key."""
        event = ContextChangeEvent("", "old", "new", 789)

        assert event.key == ""
        assert event.old_value == "old"
        assert event.new_value == "new"
        assert event.context_id == 789

    def test_init_with_negative_context_id(self) -> None:
        """Test initialization with negative context ID."""
        event = ContextChangeEvent("key", "old", "new", -1)

        assert event.context_id == -1
        assert event.key == "key"

    def test_timestamp_is_current_time(self) -> None:
        """Test that timestamp is set to current time."""
        before_creation = time.time()
        event = ContextChangeEvent("key", "old", "new", 1)
        after_creation = time.time()

        assert before_creation <= event.timestamp <= after_creation

    def test_init_multiple_events_have_different_timestamps(self) -> None:
        """Test that multiple events created in sequence have different timestamps."""
        event1 = ContextChangeEvent("key1", "old1", "new1", 1)
        time.sleep(0.001)  # Small delay to ensure different timestamps
        event2 = ContextChangeEvent("key2", "old2", "new2", 2)

        assert event1.timestamp < event2.timestamp

    def test_init_with_various_types(self) -> None:
        """Test initialization with various Python types."""
        test_cases = [
            ("string_key", "str_old", "str_new"),
            ("int_key", 42, 43),
            ("float_key", 3.14, 2.71),
            ("bool_key", True, False),
            ("list_key", [1, 2], [3, 4]),
            ("tuple_key", (1, 2), (3, 4)),
            ("dict_key", {"a": 1}, {"b": 2}),
            ("set_key", {1, 2}, {3, 4}),
        ]

        for key, old_val, new_val in test_cases:
            event = ContextChangeEvent(key, old_val, new_val, 100)
            assert event.key == key
            assert event.old_value == old_val
            assert event.new_value == new_val
            assert event.context_id == 100

    def test_repr_basic(self) -> None:
        """Test basic string representation of ContextChangeEvent."""
        event = ContextChangeEvent("test_key", "old_val", "new_val", 123)
        repr_str = repr(event)

        assert "ContextChangeEvent" in repr_str
        assert "key='test_key'" in repr_str
        assert "old_val -> new_val" in repr_str
        assert f"t={event.timestamp}" in repr_str

    def test_repr_with_none_values(self) -> None:
        """Test string representation with None values."""
        event = ContextChangeEvent("key", None, None, 0)
        repr_str = repr(event)

        assert "ContextChangeEvent" in repr_str
        assert "key='key'" in repr_str
        assert "None -> None" in repr_str

    def test_repr_with_complex_values(self) -> None:
        """Test string representation with complex data types."""
        old_value = {"nested": {"data": [1, 2, 3]}}
        new_value = [{"item": 1}, {"item": 2}]
        event = ContextChangeEvent("complex", old_value, new_value, 456)
        repr_str = repr(event)

        assert "ContextChangeEvent" in repr_str
        assert "key='complex'" in repr_str
        assert str(old_value) in repr_str
        assert str(new_value) in repr_str

    def test_repr_with_string_containing_quotes(self) -> None:
        """Test string representation with values containing quotes."""
        event = ContextChangeEvent("key", "old'value", 'new"value', 789)
        repr_str = repr(event)

        assert "ContextChangeEvent" in repr_str
        assert "key='key'" in repr_str
        assert "old'value" in repr_str
        assert 'new"value' in repr_str

    def test_repr_format_consistency(self) -> None:
        """Test that repr format is consistent and parseable."""
        event = ContextChangeEvent("test", 42, 43, 100)
        repr_str = repr(event)

        # Check the expected format
        expected_pattern = r"ContextChangeEvent\(key='test', 42 -> 43, t=\d+\.\d+\)"
        import re

        assert re.match(expected_pattern, repr_str)

    def test_repr_with_empty_string_key(self) -> None:
        """Test string representation with empty string key."""
        event = ContextChangeEvent("", "old", "new", 1)
        repr_str = repr(event)

        assert "key=''" in repr_str
        assert "old -> new" in repr_str

    def test_repr_with_numeric_values(self) -> None:
        """Test string representation with various numeric types."""
        test_cases = [
            (42, 43, "42 -> 43"),
            (3.14, 2.71, "3.14 -> 2.71"),
            (True, False, "True -> False"),
        ]

        for old_val, new_val, expected_transition in test_cases:
            event = ContextChangeEvent("key", old_val, new_val, 1)
            repr_str = repr(event)
            assert expected_transition in repr_str
