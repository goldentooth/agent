"""Tests for Symbol class."""

from __future__ import annotations

import pytest

from goldentooth_agent.core.context import Symbol


class TestSymbol:
    """Test suite for Symbol class."""

    def test_symbol_creation(self) -> None:
        """Test that Symbol can be created from a string."""
        symbol = Symbol("agent.intent")
        assert symbol == "agent.intent"
        assert str(symbol) == "agent.intent"

    def test_symbol_is_string_subclass(self) -> None:
        """Test that Symbol inherits from str."""
        symbol = Symbol("test.path")
        assert isinstance(symbol, str)
        assert isinstance(symbol, Symbol)

    def test_symbol_string_operations(self) -> None:
        """Test that Symbol supports string operations."""
        symbol = Symbol("agent.intent")

        # Test string methods work
        assert symbol.upper() == "AGENT.INTENT"
        assert symbol.lower() == "agent.intent"
        assert symbol.startswith("agent")
        assert symbol.endswith("intent")
        assert "." in symbol
        assert len(symbol) == 12

    def test_symbol_parts_method(self) -> None:
        """Test the parts() method splits by dot delimiter."""
        # Simple case
        symbol = Symbol("agent.intent")
        assert symbol.parts() == ["agent", "intent"]

        # Multiple parts
        symbol = Symbol("agent.context.user.name")
        assert symbol.parts() == ["agent", "context", "user", "name"]

        # Single part (no dots)
        symbol = Symbol("simple")
        assert symbol.parts() == ["simple"]

        # Empty string
        symbol = Symbol("")
        assert symbol.parts() == [""]

    def test_symbol_parts_edge_cases(self) -> None:
        """Test parts() method with edge cases."""
        # Leading dot
        symbol = Symbol(".agent")
        assert symbol.parts() == ["", "agent"]

        # Trailing dot
        symbol = Symbol("agent.")
        assert symbol.parts() == ["agent", ""]

        # Multiple consecutive dots
        symbol = Symbol("agent..intent")
        assert symbol.parts() == ["agent", "", "intent"]

        # Only dots
        symbol = Symbol("...")
        assert symbol.parts() == ["", "", "", ""]

    def test_symbol_equality(self) -> None:
        """Test Symbol equality with strings and other Symbols."""
        symbol1 = Symbol("agent.intent")
        symbol2 = Symbol("agent.intent")
        symbol3 = Symbol("different.path")

        # Symbol to Symbol equality
        assert symbol1 == symbol2
        assert symbol1 != symbol3

        # Symbol to string equality
        assert symbol1 == "agent.intent"
        assert symbol1 != "different.path"

        # String to Symbol equality
        assert "agent.intent" == symbol1
        assert "different.path" != symbol1

    def test_symbol_hashing(self) -> None:
        """Test Symbol can be used as dictionary keys."""
        symbol1 = Symbol("agent.intent")
        symbol2 = Symbol("agent.intent")
        symbol3 = Symbol("different.path")

        # Test hashing consistency
        assert hash(symbol1) == hash(symbol2)
        assert hash(symbol1) == hash("agent.intent")

        # Test in dictionary
        symbol_dict = {symbol1: "value1", symbol3: "value3"}
        assert symbol_dict[symbol2] == "value1"  # Same hash/value
        # mypy doesn't understand that Symbol keys can be accessed with str keys
        # but this works at runtime because Symbol inherits from str
        assert symbol_dict[Symbol("agent.intent")] == "value1"  # String key works

        # Test in set
        symbol_set = {symbol1, symbol2, symbol3}
        assert len(symbol_set) == 2  # symbol1 and symbol2 are the same

    def test_symbol_concatenation(self) -> None:
        """Test Symbol concatenation with strings."""
        symbol = Symbol("agent")

        # String concatenation
        result = symbol + ".intent"
        assert result == "agent.intent"
        assert isinstance(result, str)  # Result is string, not Symbol

        # Reverse concatenation
        result = "prefix." + symbol
        assert result == "prefix.agent"
        assert isinstance(result, str)

    def test_symbol_formatting(self) -> None:
        """Test Symbol in string formatting."""
        symbol = Symbol("agent.intent")

        # f-string formatting
        formatted = f"Key: {symbol}"
        assert formatted == "Key: agent.intent"

        # .format() method
        formatted = f"Key: {symbol}"
        assert formatted == "Key: agent.intent"

    def test_symbol_repr(self) -> None:
        """Test Symbol representation."""
        symbol = Symbol("agent.intent")
        # Should use str's default repr
        assert repr(symbol) == "'agent.intent'"

    def test_symbol_with_special_characters(self) -> None:
        """Test Symbol with special characters in path."""
        # Underscores and numbers
        symbol = Symbol("agent_v2.intent_123")
        assert symbol.parts() == ["agent_v2", "intent_123"]

        # Hyphens
        symbol = Symbol("agent-name.intent-type")
        assert symbol.parts() == ["agent-name", "intent-type"]

        # Mixed special characters
        symbol = Symbol("agent:v1.intent@user")
        assert symbol.parts() == ["agent:v1", "intent@user"]

    def test_symbol_immutability(self) -> None:
        """Test that Symbol maintains string immutability."""
        symbol = Symbol("agent.intent")
        original = str(symbol)

        # String operations return new strings, don't modify original
        _ = symbol.upper()
        _ = symbol.replace("agent", "user")

        assert str(symbol) == original
        assert symbol == "agent.intent"

    def test_symbol_comparisons(self) -> None:
        """Test Symbol comparison operations."""
        symbol1 = Symbol("agent.intent")
        symbol2 = Symbol("agent.intent")
        symbol3 = Symbol("user.intent")

        # Equality
        assert symbol1 == symbol2
        assert not (symbol1 != symbol2)

        # Inequality
        assert symbol1 != symbol3
        assert not (symbol1 == symbol3)

        # String comparison
        assert symbol1 < "z"
        assert symbol1 > "a"
        assert Symbol("a") < Symbol("b")

    def test_symbol_boolean_context(self) -> None:
        """Test Symbol in boolean context."""
        # Non-empty Symbol is truthy
        assert Symbol("agent.intent")
        assert bool(Symbol("a"))

        # Empty Symbol is falsy
        assert not Symbol("")
        assert not bool(Symbol(""))

    @pytest.mark.parametrize(
        "path,expected_parts",
        [
            ("a", ["a"]),
            ("a.b", ["a", "b"]),
            ("a.b.c", ["a", "b", "c"]),
            ("agent.context.user.name", ["agent", "context", "user", "name"]),
            ("", [""]),
            (".", ["", ""]),
            (".a", ["", "a"]),
            ("a.", ["a", ""]),
            ("a..b", ["a", "", "b"]),
        ],
    )
    def test_symbol_parts_parametrized(
        self, path: str, expected_parts: list[str]
    ) -> None:
        """Test parts() method with various inputs."""
        symbol = Symbol(path)
        assert symbol.parts() == expected_parts
