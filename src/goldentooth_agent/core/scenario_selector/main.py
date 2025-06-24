from __future__ import annotations
from antidote import inject, injectable
from goldentooth_agent.core.context import Context
from goldentooth_agent.core.scenario import Scenario
from typing import Optional
from .strategy import ScenarioSelectorStrategy
from .strategy_registry import ScenarioSelectorStrategyRegistry

@injectable(factory_method="create")
class ScenarioSelector:
  """Class to select a scenario based on the current context."""

  def __init__(self, strategy_id: Optional[str] = None) -> None:
    """Initialize the ScenarioSelector."""
    self.strategy_id = strategy_id

  @classmethod
  def create(cls) -> ScenarioSelector:
    """Factory method to create an instance of ScenarioSelector."""
    return cls()

  @inject.method
  def get_strategy(
    self,
    strategy_registry: ScenarioSelectorStrategyRegistry = inject.me(),
  ) -> ScenarioSelectorStrategy:
    """Get the currently set strategy."""
    if self.strategy_id is None:
      raise ValueError("Strategy ID must be set before getting the strategy.")
    return strategy_registry.get(self.strategy_id)

  def select_scenario(self, context: Context) -> Scenario:
    """Select a scenario based on the current context."""
    return self.get_strategy().select_scenario(context)
