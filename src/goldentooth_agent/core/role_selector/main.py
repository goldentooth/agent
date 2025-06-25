from __future__ import annotations
from antidote import inject, injectable
from goldentooth_agent.core.context import Context
from goldentooth_agent.core.role import Role, RoleRegistry
from typing import Optional
from .strategy import RoleSelectorStrategy
from .strategy_registry import RoleSelectorStrategyRegistry, register_role_selector_strategy

@injectable(factory_method="create")
class RoleSelector:
  """Class to select a role based on the current context."""

  def __init__(self, strategy_id: Optional[str] = None) -> None:
    """Initialize the RoleSelector."""
    self.strategy_id = strategy_id

  @classmethod
  def create(cls) -> RoleSelector:
    """Factory method to create an instance of RoleSelector."""
    return cls()

  @inject.method
  def get_strategy(
    self,
    strategy_registry: RoleSelectorStrategyRegistry = inject.me(),
  ) -> RoleSelectorStrategy:
    """Get the currently set strategy."""
    if self.strategy_id is None:
      raise ValueError("Strategy ID must be set before getting the strategy.")
    return strategy_registry.get(self.strategy_id)

  def select_role(self, context: Context) -> Role:
    """Select a role based on the current context."""
    return self.get_strategy().select_role(context)

class DefaultRoleSelectorStrategy(RoleSelectorStrategy):
  """Default strategy for selecting roles."""
  name = "default"
  description = "Default strategy for selecting roles based on the current context."

  @inject
  def select_role(self, context: Context, role_registry: RoleRegistry = inject.me()) -> Role: # type: ignore
    """Select a role based on the current context."""
    return role_registry.get('default')

register_role_selector_strategy(obj=DefaultRoleSelectorStrategy())
