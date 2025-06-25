from goldentooth_agent.core.context import Context
from goldentooth_agent.core.persona import Persona
from goldentooth_agent.core.role import Role
from typing import Protocol, runtime_checkable

@runtime_checkable
class PlayerSelectorStrategy(Protocol):
  """Protocol for player selection strategies."""
  id: str
  description: str

  def select_persona(self, context: Context, role: Role) -> Persona:
    """Select a persona based on the current context and role."""
    ...

  def select_role(self, context: Context, persona: Persona) -> Role:
    """Select a role based on the current context and persona."""
    ...
