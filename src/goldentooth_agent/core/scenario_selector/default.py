from __future__ import annotations
from antidote import inject
from goldentooth_agent.core.context import Context
from goldentooth_agent.core.scenario import Scenario, ScenarioRegistry
from .strategy import ScenarioSelectorStrategy
from .strategy_registry import register_scenario_selector_strategy

class DefaultScenarioSelectorStrategy(ScenarioSelectorStrategy):
  """Default strategy for selecting scenarios."""
  name = "default"
  description = "Default strategy for selecting scenarios based on the current context."

  @inject.method
  def select_scenario(self, context: Context, scenario_registry: ScenarioRegistry = inject.me()) -> Scenario: # type: ignore
    """Select a scenario based on the current context."""
    return scenario_registry.get('default')

register_scenario_selector_strategy(obj=DefaultScenarioSelectorStrategy())
