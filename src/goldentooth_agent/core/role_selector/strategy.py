from goldentooth_agent.core.context import Context
from goldentooth_agent.core.role import Role
from typing import Protocol, runtime_checkable


@runtime_checkable
class RoleSelectorStrategy(Protocol):
    """Protocol for role selection strategies."""

    id: str
    description: str

    def select_role(self, context: Context) -> Role:
        """Select a role based on the current context."""
        ...
