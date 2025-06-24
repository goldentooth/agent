from goldentooth_agent.core.context import Context
from goldentooth_agent.core.scenario import Scenario
from typing import Protocol

class ScenarioSelectorStrategy(Protocol):
  """Protocol for scenario selection strategies."""
  name: str
  description: str

  def select_scenario(self, context: Context) -> Scenario:
    """Select a scenario based on the current context."""
    ...
