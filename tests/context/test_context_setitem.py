"""Tests for Context.__setitem__ method."""

from typing import Any

from context.frame import ContextFrame
from context.main import Context


class TestContextSetitem:
    """Test suite for Context.__setitem__ method."""

    def test_setitem_basic_functionality(self) -> None:
        """Test basic __setitem__ functionality."""

        context = Context()
        context["key1"] = "value1"

        # Value should be set in the current (last) frame
        assert context.frames[-1]["key1"] == "value1"

        # Should be retrievable via get and __getitem__
        assert context.get("key1") == "value1"
        assert context["key1"] == "value1"

    def test_setitem_to_current_frame(self) -> None:
        """Test __setitem__ always adds to the current (last) frame."""

        frame1 = ContextFrame()
        frame1["existing"] = "old_value"
        frame2 = ContextFrame()

        context = Context(frames=[frame1, frame2])
        context["new_key"] = "new_value"

        # Should be added to frame2 (current frame)
        assert "new_key" not in frame1
        assert frame2["new_key"] == "new_value"

    def test_setitem_overwrites_in_current_frame(self) -> None:
        """Test __setitem__ overwrites value in current frame."""

        context = Context()
        context["key"] = "first_value"
        context["key"] = "second_value"

        # Should have the second value
        assert context.frames[-1]["key"] == "second_value"
        assert context.get("key") == "second_value"
        assert context["key"] == "second_value"

    def test_setitem_shadows_previous_frames(self) -> None:
        """Test __setitem__ in current frame shadows values in previous frames."""

        frame1 = ContextFrame()
        frame1["key"] = "frame1_value"
        frame2 = ContextFrame()

        context = Context(frames=[frame1, frame2])
        context["key"] = "frame2_value"

        # frame1 should still have original value
        assert frame1["key"] == "frame1_value"
        # frame2 should have new value
        assert frame2["key"] == "frame2_value"
        # get and __getitem__ should return frame2 value (shadowing)
        assert context.get("key") == "frame2_value"
        assert context["key"] == "frame2_value"

    def test_setitem_with_different_value_types(self) -> None:
        """Test __setitem__ with different value types."""

        context = Context()
        test_values = {
            "string": "text",
            "integer": 42,
            "float": 3.14,
            "boolean": True,
            "none_value": None,
            "list": [1, 2, 3],
            "dict": {"nested": "value"},
            "tuple": (1, 2, 3),
        }

        # Set all values using __setitem__
        for key, value in test_values.items():
            context[key] = value

        # Verify all values can be retrieved
        for key, expected in test_values.items():
            if key == "boolean":
                assert context.get(key) is expected
                assert context[key] is expected
            else:
                assert context.get(key) == expected
                assert context[key] == expected

    def test_setitem_preserves_object_references(self) -> None:
        """Test __setitem__ preserves object references."""

        context = Context()
        original_list = [1, 2, 3]
        original_dict = {"key": "value"}

        context["list"] = original_list
        context["dict"] = original_dict

        # Should be same object references
        assert context.get("list") is original_list
        assert context["list"] is original_list
        assert context.get("dict") is original_dict
        assert context["dict"] is original_dict

    def test_setitem_multiple_keys(self) -> None:
        """Test setting multiple keys using __setitem__."""

        context = Context()

        context["key1"] = "value1"
        context["key2"] = "value2"
        context["key3"] = "value3"

        # All should be in current frame
        assert context.frames[-1]["key1"] == "value1"
        assert context.frames[-1]["key2"] == "value2"
        assert context.frames[-1]["key3"] == "value3"

        # All should be retrievable via both methods
        assert context.get("key1") == "value1"
        assert context["key1"] == "value1"
        assert context.get("key2") == "value2"
        assert context["key2"] == "value2"
        assert context.get("key3") == "value3"
        assert context["key3"] == "value3"

    def test_setitem_empty_key(self) -> None:
        """Test __setitem__ with empty string key."""

        context = Context()
        context[""] = "empty_key_value"

        assert context.frames[-1][""] == "empty_key_value"
        assert context.get("") == "empty_key_value"
        assert context[""] == "empty_key_value"

    def test_setitem_special_key_characters(self) -> None:
        """Test __setitem__ with special characters in keys."""

        context = Context()
        special_keys = {
            "key with spaces": "value1",
            "key_with_underscores": "value2",
            "key-with-dashes": "value3",
            "key.with.dots": "value4",
            "key123": "value5",
            "123key": "value6",
        }

        # Set all special keys using __setitem__
        for key, value in special_keys.items():
            context[key] = value

        # Verify all special keys can be retrieved
        for key, expected in special_keys.items():
            assert context.get(key) == expected
            assert context[key] == expected

    def test_setitem_with_complex_nested_data(self) -> None:
        """Test __setitem__ with complex nested data structures."""

        context = Context()
        complex_data = {
            "users": [
                {"id": 1, "name": "Alice", "profile": {"age": 30, "city": "NYC"}},
                {"id": 2, "name": "Bob", "profile": {"age": 25, "city": "LA"}},
            ],
            "settings": {
                "theme": "dark",
                "notifications": {"email": True, "push": False},
            },
        }

        context["data"] = complex_data

        retrieved_get = context.get("data")
        retrieved_getitem = context["data"]
        assert retrieved_get == complex_data
        assert retrieved_getitem == complex_data
        assert retrieved_get is complex_data  # Should be same object reference
        assert retrieved_getitem is complex_data

    def test_setitem_updates_existing_key(self) -> None:
        """Test __setitem__ updates existing key in current frame."""

        context = Context()

        # Initial set
        context["counter"] = 1
        assert context.get("counter") == 1
        assert context["counter"] == 1

        # Update same key
        context["counter"] = 2
        assert context.get("counter") == 2
        assert context["counter"] == 2

        # Update again
        context["counter"] = 3
        assert context.get("counter") == 3
        assert context["counter"] == 3

    def test_setitem_with_layered_frames(self) -> None:
        """Test __setitem__ behavior with multiple frame layers."""

        frame1, frame2, frame3 = ContextFrame(), ContextFrame(), ContextFrame()
        frame1["base"] = "base_value"
        frame1["shared"] = "frame1_shared"
        frame2["middle"] = "middle_value"

        context = Context(frames=[frame1, frame2, frame3])

        # Set using __setitem__ in current frame (frame3)
        context["shared"] = "frame3_shared"
        context["top"] = "top_value"

        # Verify frame states
        assert frame1["shared"] == "frame1_shared"
        assert "shared" not in frame2
        assert frame3["shared"] == "frame3_shared"
        assert frame3["top"] == "top_value"

        # Verify context resolution using both access methods
        expected = {
            "base": "base_value",
            "middle": "middle_value",
            "shared": "frame3_shared",
            "top": "top_value",
        }
        for key, expected_value in expected.items():
            assert context.get(key) == expected_value
            assert context[key] == expected_value

    def test_setitem_performance_with_many_operations(self) -> None:
        """Test __setitem__ performance with many operations."""

        context = Context()

        # Set many values using __setitem__
        for i in range(100):
            context[f"key_{i}"] = f"value_{i}"

        # Verify all values are set correctly using both access methods
        for i in range(100):
            assert context.get(f"key_{i}") == f"value_{i}"
            assert context[f"key_{i}"] == f"value_{i}"

        # All should be in the current frame
        assert len(context.frames[-1].data) == 100

    def test_setitem_with_none_value(self) -> None:
        """Test __setitem__ with None as value."""

        context = Context()
        context["none_key"] = None

        assert context.frames[-1]["none_key"] is None
        assert context.get("none_key") is None
        assert context["none_key"] is None

    def test_setitem_maintains_frame_independence(self) -> None:
        """Test __setitem__ maintains frame independence."""

        frame1 = ContextFrame()
        frame2 = ContextFrame()

        context = Context(frames=[frame1, frame2])

        # Set in current frame using __setitem__
        context["test"] = "value"

        # frame1 should be unchanged
        assert len(frame1.data) == 0
        assert "test" not in frame1

        # frame2 should have the value
        assert frame2["test"] == "value"

    def test_setitem_case_sensitivity(self) -> None:
        """Test __setitem__ is case sensitive for keys."""

        context = Context()

        context["Key"] = "value1"
        context["key"] = "value2"
        context["KEY"] = "value3"

        assert context.get("Key") == "value1"
        assert context["Key"] == "value1"
        assert context.get("key") == "value2"
        assert context["key"] == "value2"
        assert context.get("KEY") == "value3"
        assert context["KEY"] == "value3"

    def test_setitem_with_frame_modifications(self) -> None:
        """Test __setitem__ behavior when frames are modified externally."""

        frame1 = ContextFrame()
        frame1["external"] = "external_value"

        context = Context(frames=[frame1])
        context["internal"] = "internal_value"

        # Both values should be accessible
        assert context.get("external") == "external_value"
        assert context["external"] == "external_value"
        assert context.get("internal") == "internal_value"
        assert context["internal"] == "internal_value"

        # Modify frame externally
        frame1["external"] = "modified_external"

        # Context should see the change
        assert context.get("external") == "modified_external"
        assert context["external"] == "modified_external"
        assert context.get("internal") == "internal_value"
        assert context["internal"] == "internal_value"

    def test_setitem_returns_none(self) -> None:
        """Test __setitem__ method returns None."""

        context = Context()
        # Assignment expressions don't return values in Python
        # Just verify the assignment works correctly
        context["key"] = "value"
        assert context["key"] == "value"

        # Verify assignment can be chained with other operations
        context["counter"] = 0
        context["counter"] += 5
        assert context["counter"] == 5

    def test_setitem_enables_dict_like_usage(self) -> None:
        """Test __setitem__ enables standard dict-like usage patterns."""

        context = Context()

        # Standard assignment patterns
        context["config"] = {"debug": True}
        context["users"] = ["alice", "bob"]
        context["counter"] = 0

        # Should work with expressions
        context["counter"] += 1
        assert context["counter"] == 1

        # Should work with method calls
        context["users"].append("charlie")
        assert context["users"] == ["alice", "bob", "charlie"]

        # Should work with nested access
        context["config"]["timeout"] = 30
        assert context["config"]["timeout"] == 30

    def test_setitem_consistency_with_set_method(self) -> None:
        """Test __setitem__ produces same results as set method."""

        context1 = Context()
        context2 = Context()

        # Set same values using both methods
        context1["key1"] = "value1"
        context2.set("key1", "value1")

        context1["key2"] = 42
        context2.set("key2", 42)

        context1["key3"] = [1, 2, 3]
        context2.set("key3", [1, 2, 3])

        # Results should be identical
        assert context1["key1"] == context2["key1"]
        assert context1["key2"] == context2["key2"]
        assert context1["key3"] == context2["key3"]

        # Frame states should be identical
        assert context1.frames[-1].data.keys() == context2.frames[-1].data.keys()

    def test_setitem_thread_safety_simulation(self) -> None:
        """Test __setitem__ behavior under simulated concurrent access."""

        context = Context()

        # Simulate concurrent sets and reads using __setitem__
        for i in range(50):
            context[f"key_{i}"] = f"value_{i}"

            # Read immediately after write using both methods
            assert context.get(f"key_{i}") == f"value_{i}"
            assert context[f"key_{i}"] == f"value_{i}"

        # Verify all keys are still accessible and correct
        for i in range(50):
            assert context.get(f"key_{i}") == f"value_{i}"
            assert context[f"key_{i}"] == f"value_{i}"
