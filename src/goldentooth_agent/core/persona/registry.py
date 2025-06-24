from __future__ import annotations
from antidote import inject, injectable
from goldentooth_agent.core.logging import get_logger
from logging import Logger
from rich.pretty import Pretty
from rich.table import Table
from antidote import injectable
from goldentooth_agent.core.named_registry import NamedRegistry
from rich.table import Table
from .base import Persona

@injectable()
class PersonaRegistry(NamedRegistry[Persona]):
  """Registry for managing personas."""

  @inject.method
  def dump(self, logger: Logger = inject[get_logger(__name__)]) -> Table:
    """Dump all registered personas to a table."""
    logger.debug("Dumping all registered personas to a table")
    table = Table(title="Registered Personas")
    table.add_column("Name", justify="left", style="cyan", no_wrap=True)
    table.add_column("Data", justify="left", style="magenta")
    for name, persona in self.items():
      persona_dict = {
        "name": persona.name,
        "context_providers": persona.context_provider_ids,
      }
      table.add_row(name, Pretty(persona_dict))
    return table
