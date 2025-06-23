from goldentooth_agent.core.context import Context
from goldentooth_agent.core.role import Role
from typing import Protocol

class RoleSelectorStrategy(Protocol):
  """Protocol for role selection strategies."""
  name: str
  description: str

  def select_role(self, context: Context) -> Role:
    """Select a role based on the current context."""
    ...
