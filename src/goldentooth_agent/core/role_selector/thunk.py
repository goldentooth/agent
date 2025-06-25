from antidote import inject
from goldentooth_agent.core.context import Context, context_autothunk
from goldentooth_agent.core.logging import get_logger
from goldentooth_agent.core.role import Role, ROLE_KEY
from goldentooth_agent.core.thunk import Thunk, compose_chain
from logging import Logger
from typing import Annotated
from .context import ROLE_SELECTOR_STRATEGY_KEY
from .main import RoleSelector
from .strategy_registry import RoleSelectorStrategyRegistry
from .strategy import RoleSelectorStrategy

def inject_role_selector_strategy() -> Thunk[Context, Context]:
  """Create a thunk to inject a role selector strategy based on the current context."""
  @context_autothunk(name="inject_role_selector_strategy")
  @inject
  async def _inject_role_selector_strategy(
    context: Context,
    role_selector_registry: RoleSelectorStrategyRegistry = inject.me(),
    logger: Logger = inject[get_logger(__name__)],
  ) -> Annotated[RoleSelectorStrategy, ROLE_SELECTOR_STRATEGY_KEY]:
    """Thunk to select a role selector strategy."""
    logger.debug("Injecting role selector strategy")
    if context.has(ROLE_SELECTOR_STRATEGY_KEY):
      logger.debug("Using existing role selector strategy from context")
      return context.get(ROLE_SELECTOR_STRATEGY_KEY)
    default_strategy = role_selector_registry.get('default')
    logger.debug("Using default role selector strategy: %s", default_strategy.id)
    return default_strategy
  return _inject_role_selector_strategy

def inject_role() -> Thunk[Context, Context]:
  """Create a thunk to inject a role based on the current context."""
  @context_autothunk(name="inject_role")
  @inject
  async def _inject_role(
    context: Context,
    role_selector_strategy: Annotated[RoleSelectorStrategy, ROLE_SELECTOR_STRATEGY_KEY],
    role_selector: RoleSelector = inject.me(),
    logger: Logger = inject[get_logger(__name__)],
  ) -> Annotated[Role, ROLE_KEY]:
    """Thunk to inject a role into the context."""
    logger.debug("Injecting role into context")
    if context.has(ROLE_KEY):
      logger.debug("Using existing role from context")
      return context.get(ROLE_KEY)
    role_selector.strategy_id = role_selector_strategy.id
    logger.debug("Selecting role using strategy: %s", role_selector.strategy_id)
    role = role_selector.select_role(context)
    logger.debug("Selected role: %s", role.id)
    return role
  return _inject_role

def select_role_chain() -> Thunk[Context, Context]:
  """Create a thunk to select a role based on the current context."""
  return compose_chain(
    inject_role_selector_strategy(),
    inject_role(),
  )
