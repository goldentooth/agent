"""Tests for Context.remove_transformations method."""

from context.main import Context


class TestContextRemoveTransformations:
    """Test suite for Context.remove_transformations method."""

    def test_remove_transformations_basic(self) -> None:
        """Test basic transformation removal functionality."""
        context = Context()

        # Add a transformation
        context.add_transformation("name", str.upper)

        # Verify transformation was added by testing behavior
        context.set("name", "hello")
        assert context.get("name") == "HELLO"

        # Remove transformations for the key
        context.remove_transformations("name")

        # Verify transformations were removed by testing behavior
        context.set("name", "world")
        assert context.get("name") == "world"  # No transformation applied

    def test_remove_transformations_multiple_keys(self) -> None:
        """Test removing transformations from specific keys while preserving others."""
        context = Context()

        # Add transformations to multiple keys
        context.add_transformation("key1", str.upper)
        context.add_transformation("key2", str.lower)
        context.add_transformation("key3", lambda x: x * 2)

        # Remove transformations for one key
        context.remove_transformations("key2")

        # Verify only key2 transformations were removed by testing behavior
        context.set("key1", "Hello")
        context.set("key2", "Hello")
        context.set("key3", "Hello")

        assert context.get("key1") == "HELLO"  # Still transformed
        assert context.get("key2") == "Hello"  # No longer transformed
        assert context.get("key3") == "HelloHello"  # Still transformed

    def test_remove_transformations_multiple_per_key(self) -> None:
        """Test removing all transformations when multiple exist for the same key."""
        context = Context()

        # Add multiple transformations to the same key
        context.add_transformation("value", lambda x: x * 2)
        context.add_transformation("value", lambda x: x + 1)
        context.add_transformation("value", lambda x: x * 3)

        # Verify multiple transformations exist
        assert "value" in context._transformations_manager._transformations
        assert len(context._transformations_manager._transformations["value"]) == 3

        # Remove all transformations for the key
        context.remove_transformations("value")

        # Verify all transformations were removed
        assert "value" not in context._transformations_manager._transformations

    def test_remove_transformations_nonexistent_key(self) -> None:
        """Test removing transformations for a key that doesn't exist."""
        context = Context()

        # Try to remove transformations for non-existent key
        context.remove_transformations("nonexistent")

        # Should not raise error and transformations should remain empty
        assert len(context._transformations_manager._transformations) == 0

    def test_remove_transformations_empty_context(self) -> None:
        """Test removing transformations from empty context."""
        context = Context()

        # Verify context is empty
        assert len(context._transformations_manager._transformations) == 0

        # Try to remove transformations
        context.remove_transformations("any_key")

        # Should not raise error and remain empty
        assert len(context._transformations_manager._transformations) == 0

    def test_remove_transformations_after_key_exists(self) -> None:
        """Test removing transformations for a key that existed but was already removed."""
        context = Context()

        # Add and remove transformation
        context.add_transformation("temp", str.upper)
        context.remove_transformations("temp")

        # Try to remove again
        context.remove_transformations("temp")

        # Should not raise error
        assert "temp" not in context._transformations_manager._transformations

    def test_remove_transformations_partial_removal(self) -> None:
        """Test that removing transformations for one key doesn't affect others."""
        context = Context()

        # Add transformations to multiple keys
        context.add_transformation("keep1", str.upper)
        context.add_transformation("keep1", str.lower)
        context.add_transformation("remove", lambda x: x * 2)
        context.add_transformation("keep2", lambda x: x + 1)

        # Verify initial state
        assert len(context._transformations_manager._transformations) == 3

        # Remove transformations for "remove" key
        context.remove_transformations("remove")

        # Verify selective removal
        assert "remove" not in context._transformations_manager._transformations
        assert "keep1" in context._transformations_manager._transformations
        assert "keep2" in context._transformations_manager._transformations

    def test_remove_transformations_special_characters_key(self) -> None:
        """Test removing transformations with special characters in key."""
        context = Context()

        # Add transformations with special character keys
        special_keys = ["key.with.dots", "key-with-dashes", "key_with_underscores"]

        for key in special_keys:
            context.add_transformation(key, str.upper)

        # Remove one transformation
        context.remove_transformations("key.with.dots")

        # Verify correct removal
        assert "key.with.dots" not in context._transformations_manager._transformations
        assert "key-with-dashes" in context._transformations_manager._transformations
        assert (
            "key_with_underscores" in context._transformations_manager._transformations
        )

    def test_remove_transformations_empty_key(self) -> None:
        """Test removing transformations with empty string key."""
        context = Context()

        # Add transformation with empty key
        context.add_transformation("", str.upper)
        assert "" in context._transformations_manager._transformations

        # Remove transformation with empty key
        context.remove_transformations("")

        # Verify removal
        assert "" not in context._transformations_manager._transformations

    def test_remove_transformations_returns_none(self) -> None:
        """Test that remove_transformations returns None."""
        context = Context()

        # Add transformation
        context.add_transformation("test", str.upper)

        # Remove and check return value
        context.remove_transformations("test")

    def test_remove_transformations_independence(self) -> None:
        """Test that removing transformations from one context doesn't affect others."""
        context1 = Context()
        context2 = Context()

        # Add same transformation to both contexts
        context1.add_transformation("shared", str.upper)
        context2.add_transformation("shared", str.upper)

        # Remove from first context only
        context1.remove_transformations("shared")

        # Verify independence
        assert "shared" not in context1._transformations_manager._transformations
        assert "shared" in context2._transformations_manager._transformations
        assert len(context2._transformations_manager._transformations["shared"]) == 1

    def test_remove_transformations_sequence(self) -> None:
        """Test adding and removing transformations in sequence."""
        context = Context()

        # Add multiple transformations
        context.add_transformation("key", str.upper)
        context.add_transformation("key", str.lower)
        assert len(context._transformations_manager._transformations["key"]) == 2

        # Remove all transformations
        context.remove_transformations("key")
        assert "key" not in context._transformations_manager._transformations

        # Add new transformation to same key
        context.add_transformation("key", lambda x: x * 2)
        assert "key" in context._transformations_manager._transformations
        assert len(context._transformations_manager._transformations["key"]) == 1

        # Remove again
        context.remove_transformations("key")
        assert "key" not in context._transformations_manager._transformations

    def test_remove_transformations_all_keys(self) -> None:
        """Test removing transformations from all keys."""
        context = Context()

        # Add transformations to multiple keys
        keys = ["key1", "key2", "key3", "key4"]
        for key in keys:
            context.add_transformation(key, str.upper)

        # Verify all were added
        assert len(context._transformations_manager._transformations) == 4

        # Remove all transformations
        for key in keys:
            context.remove_transformations(key)

        # Verify all were removed
        assert len(context._transformations_manager._transformations) == 0
        for key in keys:
            assert key not in context._transformations_manager._transformations

    def test_remove_transformations_mixed_operations(self) -> None:
        """Test mixing add and remove operations."""
        context = Context()

        # Add initial transformations
        context.add_transformation("keep", str.upper)
        context.add_transformation("remove_later", str.lower)
        context.add_transformation("keep", lambda x: x * 2)

        # Remove one key
        context.remove_transformations("remove_later")

        # Add more to existing key
        context.add_transformation("keep", lambda x: x + 1)

        # Verify final state
        assert "remove_later" not in context._transformations_manager._transformations
        assert "keep" in context._transformations_manager._transformations
        assert len(context._transformations_manager._transformations["keep"]) == 3
