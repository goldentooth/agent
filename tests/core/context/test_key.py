"""Tests for ContextKey class and context_key function."""

from __future__ import annotations

from typing import Any

import pytest

from goldentooth_agent.core.context import ContextKey, Symbol, context_key


class TestContextKey:
    """Test suite for ContextKey class."""

    def test_context_key_creation_basic(self) -> None:
        """Test basic ContextKey creation."""
        key: ContextKey[str] = ContextKey("user.name", str, "User's display name")

        assert key.path == "user.name"
        assert key.type_ is str
        assert key.description == "User's display name"

    def test_context_key_creation_defaults(self) -> None:
        """Test ContextKey creation with default values."""
        # With type and description defaults
        key: ContextKey[str] = ContextKey("simple.key")
        assert key.path == "simple.key"
        assert key.type_ is str
        assert key.description == ""

        # With description default
        key2: ContextKey[int] = ContextKey("typed.key", int)
        assert key2.path == "typed.key"
        assert key2.type_ is int
        assert key2.description == ""

    def test_context_key_create_classmethod(self) -> None:
        """Test ContextKey.create() classmethod."""
        key: ContextKey[int] = ContextKey.create("user.age", int, "User's age in years")

        assert key.path == "user.age"
        assert key.type_ is int
        assert key.description == "User's age in years"
        assert isinstance(key, ContextKey)

    def test_context_key_symbol_property(self) -> None:
        """Test the symbol cached property."""
        key: ContextKey[str] = ContextKey("agent.intent", str, "Agent's current intent")

        # Test symbol property
        symbol = key.symbol
        assert isinstance(symbol, Symbol)
        assert symbol == "agent.intent"
        assert str(symbol) == "agent.intent"

        # Test it's cached (same object)
        symbol2 = key.symbol
        assert symbol is symbol2

    def test_context_key_string_methods(self) -> None:
        """Test string representation methods."""
        key: ContextKey[dict[str, Any]] = ContextKey(
            "user.preferences", dict, "User preference settings"
        )

        # Test __str__
        assert str(key) == "user.preferences"

        # Test __repr__
        assert repr(key) == "ContextKey(user.preferences<dict>)"

    def test_context_key_equality(self) -> None:
        """Test ContextKey equality based on path only."""
        key1: ContextKey[str] = ContextKey("user.name", str, "First description")
        key2: ContextKey[int] = ContextKey(
            "user.name", int, "Different type and description"
        )
        key3: ContextKey[str] = ContextKey("different.path", str, "First description")

        # Equal keys (same path, different type/description)
        assert key1 == key2
        assert key2 == key1

        # Different keys (different path)
        assert key1 != key3
        assert key2 != key3

        # Not equal to non-ContextKey objects
        assert key1 != "user.name"
        assert key1 != 42
        assert key1 is not None

    def test_context_key_equality_returns_not_implemented(self) -> None:
        """Test that equality returns NotImplemented for non-ContextKey objects."""
        key: ContextKey[str] = ContextKey("test.key", str)

        # These should return NotImplemented, not False
        result = key.__eq__("string")
        assert result is NotImplemented

        result = key.__eq__(42)
        assert result is NotImplemented

    def test_context_key_hashing(self) -> None:
        """Test ContextKey hashing based on path."""
        key1: ContextKey[str] = ContextKey("user.name", str, "Description 1")
        key2: ContextKey[int] = ContextKey("user.name", int, "Description 2")
        key3: ContextKey[str] = ContextKey("different.path", str, "Description 1")

        # Same path = same hash
        assert hash(key1) == hash(key2)

        # Different path = likely different hash
        assert hash(key1) != hash(key3)

        # Hash consistency
        assert hash(key1) == hash(key1)

    def test_context_key_as_dict_key(self) -> None:
        """Test ContextKey can be used as dictionary keys."""
        key1: ContextKey[str] = ContextKey("user.name", str)
        key2: ContextKey[int] = ContextKey(
            "user.name", int
        )  # Same path, different type
        key3: ContextKey[int] = ContextKey("user.age", int)

        # Use as dictionary keys
        data = {key1: "John", key3: 25}

        # key2 should access same value as key1 (same path)
        assert data[key2] == "John"

        # Update via different key with same path
        data[key2] = "Jane"
        assert data[key1] == "Jane"

        # Different path
        assert data[key3] == 25

    def test_context_key_in_set(self) -> None:
        """Test ContextKey in sets."""
        key1: ContextKey[str] = ContextKey("user.name", str)
        key2: ContextKey[int] = ContextKey("user.name", int)  # Same path
        key3: ContextKey[int] = ContextKey("user.age", int)

        key_set = {key1, key2, key3}

        # Only 2 unique keys (key1 and key2 are considered equal)
        assert len(key_set) == 2
        assert key1 in key_set
        assert key2 in key_set
        assert key3 in key_set

    def test_context_key_frozen_dataclass(self) -> None:
        """Test that ContextKey is immutable (frozen dataclass)."""
        key: ContextKey[str] = ContextKey("user.name", str, "User's name")

        # Cannot modify fields (these will raise AttributeError, not FrozenInstanceError)
        with pytest.raises(AttributeError):
            key.path = "new.path"  # type: ignore

        with pytest.raises(AttributeError):
            key.type_ = int  # type: ignore

        with pytest.raises(AttributeError):
            key.description = "New description"  # type: ignore

    def test_context_key_with_various_types(self) -> None:
        """Test ContextKey with various Python types."""
        # Basic types
        str_key: ContextKey[str] = ContextKey("string.key", str)
        int_key: ContextKey[int] = ContextKey("int.key", int)
        float_key: ContextKey[float] = ContextKey("float.key", float)
        bool_key: ContextKey[bool] = ContextKey("bool.key", bool)

        # Collection types
        list_key: ContextKey[list[Any]] = ContextKey("list.key", list)
        dict_key: ContextKey[dict[Any, Any]] = ContextKey("dict.key", dict)
        set_key: ContextKey[set[Any]] = ContextKey("set.key", set)

        # Verify types are stored correctly
        assert str_key.type_ is str
        assert int_key.type_ is int
        assert float_key.type_ is float
        assert bool_key.type_ is bool
        assert list_key.type_ is list
        assert dict_key.type_ is dict
        assert set_key.type_ is set

    def test_context_key_with_generic_types(self) -> None:
        """Test ContextKey with generic types."""
        # This tests the generic type parameter T
        list_str_key: ContextKey[list[str]] = ContextKey("list.str", list[str])
        dict_any_key: ContextKey[dict[str, Any]] = ContextKey(
            "dict.any", dict[str, Any]
        )

        assert list_str_key.path == "list.str"
        assert dict_any_key.path == "dict.any"

        # Note: The actual generic type info is erased at runtime in Python
        # but the type annotation helps with static type checking

    def test_context_key_empty_and_special_paths(self) -> None:
        """Test ContextKey with empty and special path values."""
        # Empty path
        empty_key: ContextKey[str] = ContextKey("", str)
        assert empty_key.path == ""
        assert str(empty_key) == ""

        # Single character
        single_key: ContextKey[str] = ContextKey("a", str)
        assert single_key.path == "a"

        # Path with special characters
        special_key: ContextKey[str] = ContextKey("user:name@domain.com", str)
        assert special_key.path == "user:name@domain.com"

        # Path with spaces
        space_key: ContextKey[str] = ContextKey("user name", str)
        assert space_key.path == "user name"

    def test_context_key_symbol_parts_integration(self) -> None:
        """Test integration between ContextKey symbol and Symbol.parts()."""
        key: ContextKey[dict[str, Any]] = ContextKey(
            "agent.context.user.preferences", dict
        )

        symbol = key.symbol
        parts = symbol.parts()

        assert parts == ["agent", "context", "user", "preferences"]
        assert len(parts) == 4


class TestContextKeyFunction:
    """Test suite for context_key convenience function."""

    def test_context_key_function_basic(self) -> None:
        """Test basic usage of context_key function."""
        key = context_key("user.name", str, "User's display name")

        assert isinstance(key, ContextKey)
        assert key.path == "user.name"
        assert key.type_ is str
        assert key.description == "User's display name"

    def test_context_key_function_default_description(self) -> None:
        """Test context_key function with default description."""
        key = context_key("user.age", int)

        assert key.path == "user.age"
        assert key.type_ is int
        assert key.description == ""

    def test_context_key_function_with_various_types(self) -> None:
        """Test context_key function with various types."""
        str_key = context_key("str.key", str)
        int_key = context_key("int.key", int)
        list_key = context_key("list.key", list)
        dict_key = context_key("dict.key", dict)

        assert str_key.type_ is str
        assert int_key.type_ is int
        assert list_key.type_ is list
        assert dict_key.type_ is dict

    def test_context_key_function_returns_same_as_create(self) -> None:
        """Test that context_key function returns same result as ContextKey.create."""
        path = "test.key"
        key_type = str
        description = "Test description"

        func_key: ContextKey[str] = context_key(path, key_type, description)
        class_key: ContextKey[str] = ContextKey.create(path, key_type, description)

        assert func_key == class_key
        assert func_key.path == class_key.path
        assert func_key.type_ == class_key.type_
        assert func_key.description == class_key.description

    def test_context_key_function_generic_typing(self) -> None:
        """Test context_key function with generic type annotations."""
        # These test static typing support
        str_key: ContextKey[str] = context_key("name", str)
        int_key: ContextKey[int] = context_key("age", int)
        list_key: ContextKey[list[str]] = context_key("items", list[str])

        assert str_key.type_ is str
        assert int_key.type_ is int
        assert list_key.type_ == list[str]


class TestContextKeyEdgeCases:
    """Test edge cases and error conditions."""

    def test_context_key_with_none_values(self) -> None:
        """Test ContextKey behavior with None values where allowed."""
        # path cannot be None (dataclass field requirement)
        # type has default of str
        # description has default of ""

        # These should work
        key1: ContextKey[str] = ContextKey("test", str, "")
        key2: ContextKey[str] = ContextKey("test", str)

        assert key1.description == ""
        assert key2.description == ""

    def test_context_key_comparison_edge_cases(self) -> None:
        """Test comparison edge cases."""
        key: ContextKey[str] = ContextKey("test.key", str)

        # Comparison with None
        assert key is not None
        assert key is not None

        # Comparison with other types should not raise
        assert key != "string"
        assert key != 42
        assert key != []
        assert key != {}

    def test_context_key_symbol_caching(self) -> None:
        """Test that symbol property is properly cached."""
        key: ContextKey[str] = ContextKey("test.key", str)

        # First access
        symbol1 = key.symbol

        # Second access should return same object
        symbol2 = key.symbol

        assert symbol1 is symbol2
        assert id(symbol1) == id(symbol2)

    def test_context_key_with_custom_classes(self) -> None:
        """Test ContextKey with custom classes as types."""

        class CustomClass:
            pass

        class AnotherClass:
            def __init__(self, value: int):
                self.value = value

        # Use custom classes as types
        custom_key: ContextKey[Any] = ContextKey(
            "custom", CustomClass, "Custom class key"
        )
        another_key: ContextKey[Any] = ContextKey(
            "another", AnotherClass, "Another class key"
        )

        assert custom_key.type_ == CustomClass
        assert another_key.type_ == AnotherClass
        assert repr(custom_key) == "ContextKey(custom<CustomClass>)"
        assert repr(another_key) == "ContextKey(another<AnotherClass>)"

    def test_context_key_repr_with_long_names(self) -> None:
        """Test __repr__ with long class names."""

        class VeryLongClassNameForTesting:
            pass

        key: ContextKey[Any] = ContextKey("test", VeryLongClassNameForTesting)
        expected = "ContextKey(test<VeryLongClassNameForTesting>)"
        assert repr(key) == expected

    @pytest.mark.parametrize(
        "path,type_cls,description",
        [
            ("simple", str, "Simple test"),
            ("a.b.c.d.e", int, "Deep nested path"),
            ("", str, "Empty path"),
            ("special!@#$%^&*()", dict, "Special characters"),
            ("unicode_∑∆π", list, "Unicode characters"),
            ("spaces in path", set, "Path with spaces"),
            ("UPPERCASE.PATH", bool, "Uppercase path"),
            ("numbers123.path456", float, "Numbers in path"),
        ],
    )
    def test_context_key_various_inputs(
        self, path: str, type_cls: type, description: str
    ) -> None:
        """Test ContextKey with various path inputs."""
        key: ContextKey[Any] = ContextKey(path, type_cls, description)

        assert key.path == path
        assert key.type_ == type_cls
        assert key.description == description
        assert str(key) == path


class TestContextKeyIntegration:
    """Integration tests combining Symbol and ContextKey."""

    def test_context_key_symbol_integration(self) -> None:
        """Test integration between ContextKey and Symbol."""
        key: ContextKey[dict[str, Any]] = ContextKey(
            "agent.context.user.profile", dict, "User profile data"
        )

        # Get symbol
        symbol = key.symbol
        assert isinstance(symbol, Symbol)
        assert symbol == "agent.context.user.profile"

        # Use symbol parts
        parts = symbol.parts()
        assert parts == ["agent", "context", "user", "profile"]

        # Symbol should be usable as string
        assert symbol.startswith("agent")
        assert symbol.endswith("profile")
        assert "context" in symbol

    def test_context_key_in_real_world_scenario(self) -> None:
        """Test ContextKey in a realistic usage scenario."""
        # Create various context keys that might be used in an agent system
        user_name_key = context_key("user.name", str, "User's display name")
        user_age_key = context_key("user.age", int, "User's age")
        agent_intent_key = context_key("agent.intent", str, "Current agent intent")
        session_data_key = context_key("session.data", dict, "Session storage")

        # Simulate a context dictionary
        context = {
            user_name_key: "Alice",
            user_age_key: 30,
            agent_intent_key: "greeting",
            session_data_key: {"started": True, "messages": []},
        }

        # Access values
        assert context[user_name_key] == "Alice"
        assert context[user_age_key] == 30
        assert context[agent_intent_key] == "greeting"
        session_data = context[session_data_key]
        assert session_data["started"] is True  # type: ignore

        # Keys with same path should access same value
        duplicate_name_key: ContextKey[str] = ContextKey(
            "user.name", str, "Different description"
        )
        assert context[duplicate_name_key] == "Alice"

        # Test symbol access
        assert user_name_key.symbol.parts() == ["user", "name"]
        assert agent_intent_key.symbol.parts() == ["agent", "intent"]
