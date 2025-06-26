from __future__ import annotations
from antidote import inject, injectable
from goldentooth_agent.core.logging import get_logger

from rich.pretty import Pretty
from rich.table import Table
from antidote import injectable
from goldentooth_agent.core.named_registry import NamedRegistry, make_register_fn
from rich.table import Table
from .strategy import PlayerSelectorStrategy


@injectable()
class PlayerSelectorStrategyRegistry(NamedRegistry[PlayerSelectorStrategy]):
    """Registry for managing player selector strategies."""

    @inject.method
    def dump(self, logger=inject[get_logger(__name__)]) -> Table:
        """Dump all registered player selector strategies to a table."""
        logger.debug("Dumping all registered player selector strategies to a table")
        table = Table(title="Registered Player Selector Strategies")
        table.add_column("ID", justify="left", style="cyan", no_wrap=True)
        table.add_column("Description", justify="left", style="magenta")
        for id, strategy in self.items():
            strategy_dict = {
                "id": strategy.id,
                "description": strategy.description,
            }
            table.add_row(id, Pretty(strategy_dict))
        return table


register_player_selector_strategy = make_register_fn(
    PlayerSelectorStrategyRegistry,
    default_id_fn=lambda strategy: strategy.id,
)
