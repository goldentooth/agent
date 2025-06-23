from __future__ import annotations
from antidote import inject, injectable
from atomic_agents.lib.components.system_prompt_generator import SystemPromptGenerator
from goldentooth_agent.core.logging import get_logger
from goldentooth_agent.core.named_registry import NamedRegistry
from logging import Logger
from rich.pretty import Pretty
from rich.table import Table
from rich.table import Table

@injectable()
class SystemPromptRegistry(NamedRegistry[SystemPromptGenerator]):
  """Registry for managing system prompts."""

  @inject.method
  def dump(self, logger: Logger = inject[get_logger(__name__)]) -> Table:
    """Dump all registered prompts to a table."""
    logger.debug("Dumping all registered system prompts to a table")
    table = Table(title="Registered System Prompts")
    table.add_column("Name", justify="left", style="cyan", no_wrap=True)
    table.add_column("Data", justify="left", style="magenta")
    for name, generator in self.items():
      generator_dict = {
        "background": generator.background if generator.background else None,
        "steps": generator.steps if generator.steps else None,
        "output_instructions": generator.output_instructions if generator.output_instructions else None,
        "context_providers": list(generator.context_providers.keys()) if generator.context_providers else None,
      }
      table.add_row(name, Pretty(generator_dict))
    return table
