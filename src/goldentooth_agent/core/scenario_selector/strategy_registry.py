from __future__ import annotations
from antidote import inject, injectable
from goldentooth_agent.core.logging import get_logger
from logging import Logger
from rich.pretty import Pretty
from rich.table import Table
from antidote import injectable
from goldentooth_agent.core.named_registry import NamedRegistry, make_register_fn
from rich.table import Table
from .strategy import ScenarioSelectorStrategy

@injectable()
class ScenarioSelectorStrategyRegistry(NamedRegistry[ScenarioSelectorStrategy]):
  """Registry for managing scenario selector strategies."""

  @inject.method
  def dump(self, logger: Logger = inject[get_logger(__name__)]) -> Table:
    """Dump all registered scenario selector strategies to a table."""
    logger.debug("Dumping all registered scenario selector strategies to a table")
    table = Table(title="Registered Scenario Selector Strategies")
    table.add_column("Name", justify="left", style="cyan", no_wrap=True)
    table.add_column("Description", justify="left", style="magenta")
    for name, strategy in self.items():
      strategy_dict = {
        "name": strategy.name,
        "description": strategy.description,
      }
      table.add_row(name, Pretty(strategy_dict))
    return table

register_scenario_selector_strategy = make_register_fn(
  ScenarioSelectorStrategyRegistry,
  default_name_fn=lambda strategy: strategy.name,
)
