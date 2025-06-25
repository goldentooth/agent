from __future__ import annotations
from antidote import inject, injectable
from atomic_agents.lib.components.system_prompt_generator import SystemPromptContextProviderBase
from goldentooth_agent.core.logging import get_logger
from goldentooth_agent.core.named_registry import NamedRegistry, make_register_fn
from goldentooth_agent.core.util import camel_to_snake
from logging import Logger
from rich.table import Table

@injectable()
class ContextProviderRegistry(NamedRegistry[SystemPromptContextProviderBase]):
  """Registry for managing context providers."""

  @inject.method
  def dump(self, logger: Logger = inject[get_logger(__name__)]) -> Table:
    """Dump all registered context providers to a table."""
    logger.debug("Dumping all registered context providers to a table")
    table = Table(title="Registered Context Providers")
    table.add_column("Name", justify="left", style="cyan", no_wrap=True)
    table.add_column("Data", justify="left", style="magenta")
    for name, provider in self.items():
      table.add_row(name, provider.get_info())
    return table

register_context_provider = make_register_fn(ContextProviderRegistry, default_id_fn=lambda x: camel_to_snake(x.__class__.__name__))
