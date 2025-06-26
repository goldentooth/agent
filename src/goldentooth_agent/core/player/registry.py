from __future__ import annotations
from antidote import inject, injectable
from goldentooth_agent.core.logging import get_logger
from goldentooth_agent.core.named_registry import NamedRegistry, make_register_fn

from rich.pretty import Pretty
from rich.table import Table
from .base import Player


@injectable()
class PlayerRegistry(NamedRegistry[Player]):
    """Registry for managing players."""

    @inject.method
    def dump(self, logger=inject[get_logger(__name__)]) -> Table:
        """Dump all registered players to a table."""
        logger.debug("Dumping all registered players to a table")
        table = Table(title="Registered Players")
        table.add_column("ID", justify="left", style="cyan", no_wrap=True)
        table.add_column("Role", justify="left", style="yellow")
        table.add_column("Persona", justify="left", style="magenta")
        table.add_column("Agent", justify="left", style="green")
        table.add_column("Label", justify="left", style="blue")
        for id, player in self.items():
            table.add_row(
                id,
                player.role_id,
                player.persona_id,
                player.agent_id,
                player.label.get_renderable(),
            )
        return table


register_player = make_register_fn(PlayerRegistry)
