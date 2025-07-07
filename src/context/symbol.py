from __future__ import annotations


class Symbol(str):
    """
    Represents a symbolic key like 'agent.intent'.
    You can use Symbol('agent.intent') or just strings interchangeably.
    """

    def __new__(cls, value: str) -> Symbol:
        """Create a new Symbol instance."""
        return super().__new__(cls, value)

    def parts(self) -> list[str]:
        """Split the symbol into its parts based on the '.' delimiter."""
        return self.split(".")
