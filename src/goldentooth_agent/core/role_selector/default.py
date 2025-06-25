from __future__ import annotations
from antidote import inject
from goldentooth_agent.core.context import Context
from goldentooth_agent.core.role import Role, RoleRegistry
from .strategy import RoleSelectorStrategy
from .strategy_registry import register_role_selector_strategy

class DefaultRoleSelectorStrategy(RoleSelectorStrategy):
  """Default strategy for selecting roles."""
  id = "default"
  description = "Default strategy for selecting roles based on the current context."

  @inject
  def select_role(self, context: Context, role_registry: RoleRegistry = inject.me()) -> Role: # type: ignore
    """Select a role based on the current context."""
    return role_registry.get('default')

register_role_selector_strategy(obj=DefaultRoleSelectorStrategy())
