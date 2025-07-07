import pytest

from context.symbol import Symbol


class TestSymbolNew:
    """Test the Symbol.__new__ method."""

    def test_symbol_creation(self):
        """Test creating Symbol from string and basic equality."""
        symbol = Symbol("agent.intent")
        assert symbol == "agent.intent"
        assert isinstance(symbol, Symbol)
        assert isinstance(symbol, str)

    def test_symbol_is_string_subclass(self):
        """Test that Symbol is a proper subclass of str."""
        symbol = Symbol("test.symbol")
        assert isinstance(symbol, str)
        assert isinstance(symbol, Symbol)
        assert issubclass(Symbol, str)

    def test_symbol_equality(self):
        """Test equality between Symbols and strings."""
        symbol1 = Symbol("agent.intent")
        symbol2 = Symbol("agent.intent")
        string_val = "agent.intent"

        assert symbol1 == symbol2
        assert symbol1 == string_val
        assert string_val == symbol1

    def test_symbol_hashing(self):
        """Test Symbol as dictionary keys and in sets."""
        symbol = Symbol("agent.intent")
        string_val = "agent.intent"

        # Test in dictionary
        d: dict[Symbol, str] = {symbol: "value"}
        assert d[Symbol(string_val)] == "value"

        # Test in set
        s = {symbol, string_val}
        assert len(s) == 1  # Should be deduplicated

    def test_symbol_boolean_context(self):
        """Test truthiness/falsiness of Symbol."""
        assert Symbol("test")
        assert not Symbol("")
