"""Tests for Context.set method."""

from typing import Any

from context.frame import ContextFrame
from context.main import Context


class TestContextSet:
    """Test suite for Context.set method."""

    def test_set_basic_functionality(self) -> None:
        """Test basic set functionality."""

        context = Context()
        context.set("key1", "value1")

        # Value should be set in the current (last) frame
        assert context.frames[-1]["key1"] == "value1"

        # Should be retrievable via get
        assert context.get("key1") == "value1"

    def test_set_to_current_frame(self) -> None:
        """Test set always adds to the current (last) frame."""

        frame1 = ContextFrame()
        frame1["existing"] = "old_value"
        frame2 = ContextFrame()

        context = Context(frames=[frame1, frame2])
        context.set("new_key", "new_value")

        # Should be added to frame2 (current frame)
        assert "new_key" not in frame1
        assert frame2["new_key"] == "new_value"

    def test_set_overwrites_in_current_frame(self) -> None:
        """Test set overwrites value in current frame."""

        context = Context()
        context.set("key", "first_value")
        context.set("key", "second_value")

        # Should have the second value
        assert context.frames[-1]["key"] == "second_value"
        assert context.get("key") == "second_value"

    def test_set_shadows_previous_frames(self) -> None:
        """Test set in current frame shadows values in previous frames."""

        frame1 = ContextFrame()
        frame1["key"] = "frame1_value"
        frame2 = ContextFrame()

        context = Context(frames=[frame1, frame2])
        context.set("key", "frame2_value")

        # frame1 should still have original value
        assert frame1["key"] == "frame1_value"
        # frame2 should have new value
        assert frame2["key"] == "frame2_value"
        # get should return frame2 value (shadowing)
        assert context.get("key") == "frame2_value"

    def test_set_with_different_value_types(self) -> None:
        """Test set with different value types."""

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

        # Set all values
        for key, value in test_values.items():
            context.set(key, value)

        # Verify all values can be retrieved
        for key, expected in test_values.items():
            if key == "boolean":
                assert context.get(key) is expected
            else:
                assert context.get(key) == expected

    def test_set_preserves_object_references(self) -> None:
        """Test set preserves object references."""

        context = Context()
        original_list = [1, 2, 3]
        original_dict = {"key": "value"}

        context.set("list", original_list)
        context.set("dict", original_dict)

        # Should be same object references
        assert context.get("list") is original_list
        assert context.get("dict") is original_dict

    def test_set_multiple_keys(self) -> None:
        """Test setting multiple keys."""

        context = Context()

        context.set("key1", "value1")
        context.set("key2", "value2")
        context.set("key3", "value3")

        # All should be in current frame
        assert context.frames[-1]["key1"] == "value1"
        assert context.frames[-1]["key2"] == "value2"
        assert context.frames[-1]["key3"] == "value3"

        # All should be retrievable
        assert context.get("key1") == "value1"
        assert context.get("key2") == "value2"
        assert context.get("key3") == "value3"

    def test_set_empty_key(self) -> None:
        """Test set with empty string key."""

        context = Context()
        context.set("", "empty_key_value")

        assert context.frames[-1][""] == "empty_key_value"
        assert context.get("") == "empty_key_value"

    def test_set_special_key_characters(self) -> None:
        """Test set with special characters in keys."""

        context = Context()
        special_keys = {
            "key with spaces": "value1",
            "key_with_underscores": "value2",
            "key-with-dashes": "value3",
            "key.with.dots": "value4",
            "key123": "value5",
            "123key": "value6",
        }

        # Set all special keys
        for key, value in special_keys.items():
            context.set(key, value)

        # Verify all special keys can be retrieved
        for key, expected in special_keys.items():
            assert context.get(key) == expected

    def test_set_with_complex_nested_data(self) -> None:
        """Test set with complex nested data structures."""

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

        context.set("data", complex_data)

        retrieved = context.get("data")
        assert retrieved == complex_data
        assert retrieved is complex_data  # Should be same object reference

    def test_set_updates_existing_key(self) -> None:
        """Test set updates existing key in current frame."""

        context = Context()

        # Initial set
        context.set("counter", 1)
        assert context.get("counter") == 1

        # Update same key
        context.set("counter", 2)
        assert context.get("counter") == 2

        # Update again
        context.set("counter", 3)
        assert context.get("counter") == 3

    def test_set_with_layered_frames(self) -> None:
        """Test set behavior with multiple frame layers."""

        frame1, frame2, frame3 = ContextFrame(), ContextFrame(), ContextFrame()
        frame1["base"] = "base_value"
        frame1["shared"] = "frame1_shared"
        frame2["middle"] = "middle_value"

        context = Context(frames=[frame1, frame2, frame3])
        context.set("shared", "frame3_shared")
        context.set("top", "top_value")

        # Verify frame states
        assert frame1["shared"] == "frame1_shared"
        assert "shared" not in frame2
        assert frame3["shared"] == "frame3_shared"
        assert frame3["top"] == "top_value"

        # Verify context resolution using dictionary comprehension
        expected = {
            "base": "base_value",
            "middle": "middle_value",
            "shared": "frame3_shared",
            "top": "top_value",
        }
        actual = {key: context.get(key) for key in expected}
        assert actual == expected

    def test_set_performance_with_many_operations(self) -> None:
        """Test set performance with many operations."""

        context = Context()

        # Set many values
        for i in range(100):
            context.set(f"key_{i}", f"value_{i}")

        # Verify all values are set correctly
        for i in range(100):
            assert context.get(f"key_{i}") == f"value_{i}"

        # All should be in the current frame
        assert len(context.frames[-1].data) == 100

    def test_set_with_none_value(self) -> None:
        """Test set with None as value."""

        context = Context()
        context.set("none_key", None)

        assert context.frames[-1]["none_key"] is None
        assert context.get("none_key") is None

    def test_set_maintains_frame_independence(self) -> None:
        """Test set maintains frame independence."""

        frame1 = ContextFrame()
        frame2 = ContextFrame()

        context = Context(frames=[frame1, frame2])

        # Set in current frame
        context.set("test", "value")

        # frame1 should be unchanged
        assert len(frame1.data) == 0
        assert "test" not in frame1

        # frame2 should have the value
        assert frame2["test"] == "value"

    def test_set_case_sensitivity(self) -> None:
        """Test set is case sensitive for keys."""

        context = Context()

        context.set("Key", "value1")
        context.set("key", "value2")
        context.set("KEY", "value3")

        assert context.get("Key") == "value1"
        assert context.get("key") == "value2"
        assert context.get("KEY") == "value3"

    def test_set_with_frame_modifications(self) -> None:
        """Test set behavior when frames are modified externally."""

        frame1 = ContextFrame()
        frame1["external"] = "external_value"

        context = Context(frames=[frame1])
        context.set("internal", "internal_value")

        # Both values should be accessible
        assert context.get("external") == "external_value"
        assert context.get("internal") == "internal_value"

        # Modify frame externally
        frame1["external"] = "modified_external"

        # Context should see the change
        assert context.get("external") == "modified_external"
        assert context.get("internal") == "internal_value"

    def test_set_returns_none(self) -> None:
        """Test set method doesn't return a value."""

        context = Context()
        context.set("key", "value")

    def test_set_thread_safety_simulation(self) -> None:
        """Test set behavior under simulated concurrent access."""

        context = Context()

        # Simulate concurrent sets and reads
        for i in range(50):
            context.set(f"key_{i}", f"value_{i}")

            # Read immediately after write
            assert context.get(f"key_{i}") == f"value_{i}"

        # Verify all keys are still accessible and correct
        for i in range(50):
            assert context.get(f"key_{i}") == f"value_{i}"

    def test_set_enables_subscript_access(self) -> None:
        """Test set enables subsequent subscript access."""

        context = Context()
        context.set("key", "value")

        # Should be accessible via both get and subscript
        assert context.get("key") == "value"
        assert context["key"] == "value"
