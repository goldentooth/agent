from __future__ import annotations
from antidote import inject, injectable
from atomic_agents.agents.base_agent import BaseAgentConfig
from goldentooth_agent.core.logging import get_logger
from goldentooth_agent.core.named_registry import NamedRegistry, make_register_fn
from logging import Logger
from rich.table import Table

@injectable()
class AgentConfigRegistry(NamedRegistry[BaseAgentConfig]):
  """Registry for managing agent configurations."""

  @inject.method
  def dump(self, logger: Logger = inject[get_logger(__name__)]) -> Table:
    """Dump the context to the console."""
    logger.debug("Dumping agent config registry")
    table = Table(title=f"Agent Config Registry Dump")
    table.add_column("Name")
    table.add_column("Agent Config", overflow="fold")
    for k, v in self.items():
      table.add_row(str(k), repr(v))
    return table

register_agent_config = make_register_fn(AgentConfigRegistry)
