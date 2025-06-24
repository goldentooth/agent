from __future__ import annotations
from antidote import inject, injectable
from goldentooth_agent.core.logging import get_logger
from goldentooth_agent.core.named_registry import NamedRegistry, make_register_fn
from logging import Logger
from rich.pretty import Pretty
from rich.table import Table
from .base import Scenario

@injectable()
class ScenarioRegistry(NamedRegistry[Scenario]):
  """Registry for managing scenarios."""

  @inject.method
  def dump(self, logger: Logger = inject[get_logger(__name__)]) -> Table:
    """Dump all registered scenarios to a table."""
    logger.debug("Dumping all registered scenarios to a table")
    table = Table(title="Registered Scenarios")
    table.add_column("Name", justify="left", style="cyan", no_wrap=True)
    table.add_column("Hidden", justify="center", style="yellow")
    table.add_column("Info", justify="left", style="magenta")
    table.add_column("Tags", justify="left", style="green")
    for name, scenario in self.items():
      table.add_row(
        name,
        str(scenario.hidden),
        Pretty(scenario.info),
        Pretty(scenario.tags),
      )
    return table

register_scenario = make_register_fn(ScenarioRegistry)
