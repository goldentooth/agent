from __future__ import annotations
from antidote import inject, injectable
from goldentooth_agent.core.context import Context
from goldentooth_agent.core.persona import Persona
from goldentooth_agent.core.role import Role
from typing import Optional
from .strategy import PlayerSelectorStrategy
from .strategy_registry import PlayerSelectorStrategyRegistry

@injectable(factory_method="create")
class PlayerSelector:
  """Class to select a player based on the current context."""

  def __init__(self, strategy_id: Optional[str] = None) -> None:
    """Initialize the PlayerSelector."""
    self.strategy_id = strategy_id

  @classmethod
  def create(cls) -> PlayerSelector:
    """Factory method to create an instance of PlayerSelector."""
    return cls()

  @inject.method
  def get_strategy(
    self,
    strategy_registry: PlayerSelectorStrategyRegistry = inject.me(),
  ) -> PlayerSelectorStrategy:
    """Get the currently set strategy."""
    if self.strategy_id is None:
      raise ValueError("Strategy ID must be set before getting the strategy.")
    return strategy_registry.get(self.strategy_id)

  def select_persona(self, context: Context, role: Role) -> Persona:
    """Select a player based on the current context."""
    return self.get_strategy().select_persona(context, role)

  def select_role(self, context: Context, persona: Persona) -> Role:
    """Select a role based on the current context."""
    return self.get_strategy().select_role(context, persona)
