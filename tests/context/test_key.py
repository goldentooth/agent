from typing import Any

import pytest

from context.key import ContextKey


class TestContextKeyInit:
    """Test the ContextKey.__init__ method and class structure."""

    def test_context_key_creation_basic(self):
        """Test creating ContextKey with path only."""
        key: ContextKey[str] = ContextKey("agent.intent")
        assert key.path == "agent.intent"
        assert key.type_ == str  # Default type
        assert key.description == ""  # Default description

    def test_context_key_creation_with_type(self):
        """Test creating ContextKey with path and type."""
        key: ContextKey[int] = ContextKey("user.age", int)
        assert key.path == "user.age"
        assert key.type_ == int
        assert key.description == ""

    def test_context_key_creation_with_description(self):
        """Test creating ContextKey with path and description."""
        key: ContextKey[str] = ContextKey("agent.status", str, "Current agent status")
        assert key.path == "agent.status"
        assert key.type_ == str
        assert key.description == "Current agent status"

    def test_context_key_creation_full(self):
        """Test creating ContextKey with all parameters."""
        key: ContextKey[dict[str, Any]] = ContextKey(
            "user.profile", dict, "User profile information"
        )
        assert key.path == "user.profile"
        assert key.type_ == dict
        assert key.description == "User profile information"

    def test_context_key_is_dataclass(self):
        """Test that ContextKey behaves as a frozen dataclass."""
        key: ContextKey[str] = ContextKey("test.key")

        # Test immutability (should raise error on assignment)
        with pytest.raises(AttributeError):
            key.path = "modified.path"  # type: ignore[misc]

        with pytest.raises(AttributeError):
            key.type_ = int  # type: ignore[misc]

        with pytest.raises(AttributeError):
            key.description = "modified"  # type: ignore[misc]

    def test_context_key_generic_typing(self):
        """Test that ContextKey supports generic typing."""
        # Test that we can create instances with proper typing
        str_key = ContextKey[str]("test.string", str)
        int_key = ContextKey[int]("test.int", int)

        assert str_key.path == "test.string"
        assert str_key.type_ == str
        assert int_key.path == "test.int"
        assert int_key.type_ == int

    def test_context_key_equality_by_path(self):
        """Test that ContextKey instances are equal if they have the same path."""
        key1: ContextKey[str] = ContextKey("agent.intent", str, "description1")
        key2: ContextKey[int] = ContextKey("agent.intent", int, "description2")

        # Keys should be equal despite different type and description
        assert key1 == key2

    def test_context_key_inequality(self):
        """Test that ContextKey instances with different paths are not equal."""
        key1: ContextKey[str] = ContextKey("agent.intent")
        key2: ContextKey[str] = ContextKey("agent.status")

        assert key1 != key2

    def test_context_key_hash_consistency(self):
        """Test that ContextKey instances hash consistently based on path."""
        key1: ContextKey[str] = ContextKey("agent.intent", str, "description1")
        key2: ContextKey[int] = ContextKey("agent.intent", int, "description2")

        # Should have same hash since path is the same
        assert hash(key1) == hash(key2)

        # Should work as dictionary keys
        d: dict[ContextKey[Any], str] = {key1: "value1"}
        assert d[key2] == "value1"  # key2 should find key1's value

    def test_context_key_with_empty_path(self):
        """Test ContextKey with empty path."""
        key: ContextKey[str] = ContextKey("")
        assert key.path == ""
        assert key.type_ == str
        assert key.description == ""

    def test_context_key_docstring_access(self):
        """Test that ContextKey has proper docstring."""
        assert ContextKey.__doc__ is not None
        assert "context keys" in ContextKey.__doc__.lower()
