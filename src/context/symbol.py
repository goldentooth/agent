"""Symbol system for hierarchical context keys.

This module provides the Symbol class for representing hierarchical symbolic keys
used throughout the context system. Symbols are string-based keys that support
dot-notation for hierarchical navigation (e.g., 'agent.intent.task').
"""

from __future__ import annotations


class Symbol(str):
    """Hierarchical symbolic key with dot-notation support.

    A Symbol is a string-based key that represents hierarchical data structures
    using dot-notation. It inherits from str for full string compatibility while
    providing additional functionality for hierarchical navigation.

    Symbols are commonly used in the context system for representing nested
    data structures and providing a consistent way to access hierarchical
    information.

    Examples:
        Basic usage:
            >>> symbol = Symbol("agent.intent")
            >>> str(symbol)
            'agent.intent'
            >>> symbol == "agent.intent"
            True

        Hierarchical navigation:
            >>> symbol = Symbol("agent.task.execution.status")
            >>> symbol.parts()
            ['agent', 'task', 'execution', 'status']

        String compatibility:
            >>> symbol = Symbol("test.key")
            >>> f"Context key: {symbol}"
            'Context key: test.key'
            >>> symbol in ["test.key", "other.key"]
            True

    Attributes:
        The Symbol class inherits all string attributes and methods from str.
        No additional instance attributes are defined.
    """

    def __new__(cls, value: str) -> Symbol:
        """Create a new Symbol instance from a string value.

        Args:
            value: The string value to create a Symbol from. Should follow
                   dot-notation conventions for hierarchical keys.

        Returns:
            A new Symbol instance that behaves like a string but with
            additional hierarchical functionality.

        Examples:
            >>> symbol = Symbol("agent.intent")
            >>> isinstance(symbol, str)
            True
            >>> isinstance(symbol, Symbol)
            True
        """
        return super().__new__(cls, value)

    def parts(self) -> list[str]:
        """Split the symbol into its hierarchical parts.

        Splits the symbol string on the dot ('.') delimiter to return a list
        of the individual parts that make up the hierarchical key.

        Returns:
            A list of string parts representing the hierarchical components.
            Returns a new list on each call to prevent mutation.

        Examples:
            Simple hierarchy:
                >>> symbol = Symbol("agent.intent")
                >>> symbol.parts()
                ['agent', 'intent']

            Deep hierarchy:
                >>> symbol = Symbol("agent.task.execution.status")
                >>> symbol.parts()
                ['agent', 'task', 'execution', 'status']

            Edge cases:
                >>> Symbol("").parts()
                ['']
                >>> Symbol("single").parts()
                ['single']
                >>> Symbol("agent..intent").parts()
                ['agent', '', 'intent']
        """
        return self.split(".")
