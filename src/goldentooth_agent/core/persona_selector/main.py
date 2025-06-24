from __future__ import annotations
from antidote import inject, injectable
from goldentooth_agent.core.context import Context
from goldentooth_agent.core.persona import Persona
from typing import Optional
from .strategy import PersonaSelectorStrategy
from .strategy_registry import PersonaSelectorStrategyRegistry

@injectable(factory_method="create")
class PersonaSelector:
  """Class to select a persona based on the current context."""

  def __init__(self, strategy_id: Optional[str] = None) -> None:
    """Initialize the PersonaSelector."""
    self.strategy_id = strategy_id

  @classmethod
  def create(cls) -> PersonaSelector:
    """Factory method to create an instance of PersonaSelector."""
    return cls()

  @inject.method
  def get_strategy(
    self,
    strategy_registry: PersonaSelectorStrategyRegistry = inject.me(),
  ) -> PersonaSelectorStrategy:
    """Get the currently set strategy."""
    if self.strategy_id is None:
      raise ValueError("Strategy ID must be set before getting the strategy.")
    return strategy_registry.get(self.strategy_id)

  def select_persona(self, context: Context) -> Persona:
    """Select a persona based on the current context."""
    return self.get_strategy().select_persona(context)
