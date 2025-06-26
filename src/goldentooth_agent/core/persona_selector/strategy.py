from goldentooth_agent.core.context import Context
from goldentooth_agent.core.persona import Persona
from typing import Protocol, runtime_checkable


@runtime_checkable
class PersonaSelectorStrategy(Protocol):
    """Protocol for persona selection strategies."""

    id: str
    description: str

    def select_persona(self, context: Context) -> Persona:
        """Select a persona based on the current context."""
        ...
