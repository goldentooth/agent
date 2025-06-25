from __future__ import annotations
from antidote import inject, injectable
from goldentooth_agent.core.logging import get_logger
from logging import Logger
from rich.pretty import Pretty
from rich.table import Table
from antidote import injectable
from goldentooth_agent.core.named_registry import NamedRegistry, make_register_fn
from rich.table import Table
from .strategy import AgentSelectorStrategy

@injectable()
class AgentSelectorStrategyRegistry(NamedRegistry[AgentSelectorStrategy]):
  """Registry for managing agent selector strategies."""

  @inject.method
  def dump(self, logger: Logger = inject[get_logger(__name__)]) -> Table:
    """Dump all registered agent selector strategies to a table."""
    logger.debug("Dumping all registered agent selector strategies to a table")
    table = Table(title="Registered Agent Selector Strategies")
    table.add_column("ID", justify="left", style="cyan", no_wrap=True)
    table.add_column("Description", justify="left", style="magenta")
    for id, strategy in self.items():
      strategy_dict = {
        "id": strategy.id,
        "description": strategy.description,
      }
      table.add_row(id, Pretty(strategy_dict))
    return table

register_agent_selector_strategy = make_register_fn(
  AgentSelectorStrategyRegistry,
  default_id_fn=lambda strategy: strategy.id,
)
