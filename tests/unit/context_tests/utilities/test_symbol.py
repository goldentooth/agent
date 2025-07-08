from context.symbol import Symbol


class TestSymbolNew:
    """Test the Symbol.__new__ method."""

    def test_symbol_creation(self) -> None:
        """Test creating Symbol from string and basic equality."""
        symbol = Symbol("agent.intent")
        assert symbol == "agent.intent"
        assert isinstance(symbol, Symbol)
        assert isinstance(symbol, str)

    def test_symbol_is_string_subclass(self) -> None:
        """Test that Symbol is a proper subclass of str."""
        symbol = Symbol("test.symbol")
        assert isinstance(symbol, str)
        assert isinstance(symbol, Symbol)
        assert issubclass(Symbol, str)

    def test_symbol_equality(self) -> None:
        """Test equality between Symbols and strings."""
        symbol1 = Symbol("agent.intent")
        symbol2 = Symbol("agent.intent")
        string_val = "agent.intent"

        assert symbol1 == symbol2
        assert symbol1 == string_val
        assert string_val == symbol1

    def test_symbol_hashing(self) -> None:
        """Test Symbol as dictionary keys and in sets."""
        symbol = Symbol("agent.intent")
        string_val = "agent.intent"

        # Test in dictionary
        d: dict[Symbol, str] = {symbol: "value"}
        assert d[Symbol(string_val)] == "value"

        # Test in set
        s = {symbol, string_val}
        assert len(s) == 1  # Should be deduplicated

    def test_symbol_boolean_context(self) -> None:
        """Test truthiness/falsiness of Symbol."""
        assert Symbol("test")
        assert not Symbol("")


class TestSymbolParts:
    """Test the Symbol.parts method."""

    def test_simple_symbol_parts(self) -> None:
        """Test splitting simple symbol with dots."""
        symbol = Symbol("agent.intent")
        parts = symbol.parts()
        assert parts == ["agent", "intent"]
        assert isinstance(parts, list)
        assert all(isinstance(part, str) for part in parts)

    def test_multiple_dots_symbol_parts(self) -> None:
        """Test splitting symbol with multiple dots."""
        symbol = Symbol("agent.task.execution.status")
        parts = symbol.parts()
        assert parts == ["agent", "task", "execution", "status"]
        assert len(parts) == 4

    def test_single_part_symbol(self) -> None:
        """Test symbol with no dots returns single part."""
        symbol = Symbol("agent")
        parts = symbol.parts()
        assert parts == ["agent"]
        assert len(parts) == 1

    def test_empty_symbol_parts(self) -> None:
        """Test empty symbol returns empty list."""
        symbol = Symbol("")
        parts = symbol.parts()
        assert parts == [""]
        assert len(parts) == 1

    def test_symbol_with_empty_parts(self) -> None:
        """Test symbol with empty parts from consecutive dots."""
        symbol = Symbol("agent..intent")
        parts = symbol.parts()
        assert parts == ["agent", "", "intent"]
        assert len(parts) == 3

    def test_symbol_starting_with_dot(self) -> None:
        """Test symbol starting with dot."""
        symbol = Symbol(".agent.intent")
        parts = symbol.parts()
        assert parts == ["", "agent", "intent"]
        assert len(parts) == 3

    def test_symbol_ending_with_dot(self) -> None:
        """Test symbol ending with dot."""
        symbol = Symbol("agent.intent.")
        parts = symbol.parts()
        assert parts == ["agent", "intent", ""]
        assert len(parts) == 3

    def test_symbol_only_dots(self) -> None:
        """Test symbol with only dots."""
        symbol = Symbol("...")
        parts = symbol.parts()
        assert parts == ["", "", "", ""]
        assert len(parts) == 4

    def test_parts_method_returns_new_list(self) -> None:
        """Test that parts() returns a new list each time."""
        symbol = Symbol("agent.intent")
        parts1 = symbol.parts()
        parts2 = symbol.parts()
        assert parts1 == parts2
        assert parts1 is not parts2  # Different list objects

    def test_parts_immutability(self) -> None:
        """Test that modifying returned parts doesn't affect symbol."""
        symbol = Symbol("agent.intent")
        parts = symbol.parts()
        parts.append("modified")

        # Original symbol should be unchanged
        assert symbol == "agent.intent"
        assert symbol.parts() == ["agent", "intent"]


class TestSymbolDocumentation:
    """Test the Symbol class documentation examples."""

    def test_basic_usage_examples(self) -> None:
        """Test basic usage examples from class docstring."""
        symbol = Symbol("agent.intent")
        assert str(symbol) == "agent.intent"
        assert symbol == "agent.intent"

    def test_hierarchical_navigation_examples(self) -> None:
        """Test hierarchical navigation examples from class docstring."""
        symbol = Symbol("agent.task.execution.status")
        assert symbol.parts() == ["agent", "task", "execution", "status"]

    def test_string_compatibility_examples(self) -> None:
        """Test string compatibility examples from class docstring."""
        symbol = Symbol("test.key")
        assert f"Context key: {symbol}" == "Context key: test.key"
        assert symbol in ["test.key", "other.key"]

    def test_new_method_examples(self) -> None:
        """Test __new__ method examples from docstring."""
        symbol = Symbol("agent.intent")
        assert isinstance(symbol, str)
        assert isinstance(symbol, Symbol)

    def test_parts_method_simple_hierarchy_example(self) -> None:
        """Test parts method simple hierarchy example from docstring."""
        symbol = Symbol("agent.intent")
        assert symbol.parts() == ["agent", "intent"]

    def test_parts_method_deep_hierarchy_example(self) -> None:
        """Test parts method deep hierarchy example from docstring."""
        symbol = Symbol("agent.task.execution.status")
        assert symbol.parts() == ["agent", "task", "execution", "status"]

    def test_parts_method_edge_cases_examples(self) -> None:
        """Test parts method edge cases examples from docstring."""
        assert Symbol("").parts() == [""]
        assert Symbol("single").parts() == ["single"]
        assert Symbol("agent..intent").parts() == ["agent", "", "intent"]

    def test_docstring_type_hints_consistency(self) -> None:
        """Test that type hints match documented behavior."""
        # Test that Symbol instances have proper type behavior
        symbol = Symbol("test.symbol")

        # Type hint verification through behavior
        assert isinstance(symbol, Symbol)
        assert isinstance(symbol, str)

        # Test method return types match hints
        parts = symbol.parts()
        assert isinstance(parts, list)
        assert all(isinstance(part, str) for part in parts)

    def test_symbol_as_string_interchangeability(self) -> None:
        """Test that Symbol and str are truly interchangeable."""
        symbol = Symbol("agent.intent")
        string_val = "agent.intent"

        # Test equality in both directions
        assert symbol == string_val
        assert string_val == symbol

        # Test string operations work the same
        assert symbol.startswith("agent")
        assert symbol.endswith("intent")
        assert symbol.replace(".", "_") == "agent_intent"
        assert len(symbol) == len(string_val)

        # Test in collections
        assert symbol in {"agent.intent", "other.key"}
        assert string_val in {symbol, "other.key"}
