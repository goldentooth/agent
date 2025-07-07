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


class TestSymbolParts:
    """Test the Symbol.parts method."""

    def test_simple_symbol_parts(self):
        """Test splitting simple symbol with dots."""
        symbol = Symbol("agent.intent")
        parts = symbol.parts()
        assert parts == ["agent", "intent"]
        assert isinstance(parts, list)
        assert all(isinstance(part, str) for part in parts)

    def test_multiple_dots_symbol_parts(self):
        """Test splitting symbol with multiple dots."""
        symbol = Symbol("agent.task.execution.status")
        parts = symbol.parts()
        assert parts == ["agent", "task", "execution", "status"]
        assert len(parts) == 4

    def test_single_part_symbol(self):
        """Test symbol with no dots returns single part."""
        symbol = Symbol("agent")
        parts = symbol.parts()
        assert parts == ["agent"]
        assert len(parts) == 1

    def test_empty_symbol_parts(self):
        """Test empty symbol returns empty list."""
        symbol = Symbol("")
        parts = symbol.parts()
        assert parts == [""]
        assert len(parts) == 1

    def test_symbol_with_empty_parts(self):
        """Test symbol with empty parts from consecutive dots."""
        symbol = Symbol("agent..intent")
        parts = symbol.parts()
        assert parts == ["agent", "", "intent"]
        assert len(parts) == 3

    def test_symbol_starting_with_dot(self):
        """Test symbol starting with dot."""
        symbol = Symbol(".agent.intent")
        parts = symbol.parts()
        assert parts == ["", "agent", "intent"]
        assert len(parts) == 3

    def test_symbol_ending_with_dot(self):
        """Test symbol ending with dot."""
        symbol = Symbol("agent.intent.")
        parts = symbol.parts()
        assert parts == ["agent", "intent", ""]
        assert len(parts) == 3

    def test_symbol_only_dots(self):
        """Test symbol with only dots."""
        symbol = Symbol("...")
        parts = symbol.parts()
        assert parts == ["", "", "", ""]
        assert len(parts) == 4

    def test_parts_method_returns_new_list(self):
        """Test that parts() returns a new list each time."""
        symbol = Symbol("agent.intent")
        parts1 = symbol.parts()
        parts2 = symbol.parts()
        assert parts1 == parts2
        assert parts1 is not parts2  # Different list objects

    def test_parts_immutability(self):
        """Test that modifying returned parts doesn't affect symbol."""
        symbol = Symbol("agent.intent")
        parts = symbol.parts()
        parts.append("modified")

        # Original symbol should be unchanged
        assert symbol == "agent.intent"
        assert symbol.parts() == ["agent", "intent"]
