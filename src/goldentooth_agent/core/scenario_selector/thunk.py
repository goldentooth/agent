from antidote import inject
from goldentooth_agent.core.context import Context, context_autothunk
from goldentooth_agent.core.logging import get_logger
from goldentooth_agent.core.scenario import Scenario, SCENARIO_KEY
from goldentooth_agent.core.thunk import Thunk, compose_chain
from logging import Logger
from typing import Annotated
from .context import SCENARIO_SELECTOR_STRATEGY_KEY
from .main import ScenarioSelector
from .strategy_registry import ScenarioSelectorStrategyRegistry
from .strategy import ScenarioSelectorStrategy

def inject_scenario_selector_strategy() -> Thunk[Context, Context]:
  """Create a thunk to inject a scenario selector strategy based on the current context."""
  @context_autothunk(name="inject_scenario_selector_strategy")
  @inject
  async def _inject_scenario_selector_strategy(
    context: Context,
    scenario_selector_registry: ScenarioSelectorStrategyRegistry = inject.me(),
    logger: Logger = inject[get_logger(__name__)],
  ) -> Annotated[ScenarioSelectorStrategy, SCENARIO_SELECTOR_STRATEGY_KEY]:
    """Thunk to select a scenario selector strategy."""
    logger.debug("Injecting scenario selector strategy")
    if context.has(SCENARIO_SELECTOR_STRATEGY_KEY):
      logger.debug("Using existing scenario selector strategy from context")
      return context.get(SCENARIO_SELECTOR_STRATEGY_KEY)
    default_strategy = scenario_selector_registry.get('default')
    logger.debug("Using default scenario selector strategy: %s", default_strategy.id)
    return default_strategy
  return _inject_scenario_selector_strategy

def inject_scenario() -> Thunk[Context, Context]:
  """Create a thunk to inject a scenario based on the current context."""
  @context_autothunk(name="inject_scenario")
  @inject
  async def _inject_scenario(
    context: Context,
    scenario_selector_strategy: Annotated[ScenarioSelectorStrategy, SCENARIO_SELECTOR_STRATEGY_KEY],
    scenario_selector: ScenarioSelector = inject.me(),
    logger: Logger = inject[get_logger(__name__)],
  ) -> Annotated[Scenario, SCENARIO_KEY]:
    """Thunk to inject a scenario into the context."""
    logger.debug("Injecting scenario into context")
    if context.has(SCENARIO_KEY):
      logger.debug("Using existing scenario from context")
      return context.get(SCENARIO_KEY)
    scenario_selector.strategy_id = scenario_selector_strategy.id
    logger.debug("Selecting scenario using strategy: %s", scenario_selector.strategy_id)
    scenario = scenario_selector.select_scenario(context)
    logger.debug("Selected scenario: %s", scenario.id)
    return scenario
  return _inject_scenario

def select_scenario_chain() -> Thunk[Context, Context]:
  """Create a thunk to select a scenario based on the current context."""
  return compose_chain(
    inject_scenario_selector_strategy(),
    inject_scenario(),
  )
