from __future__ import annotations
from antidote import inject, injectable
from atomic_agents.lib.components.system_prompt_generator import SystemPromptGenerator
from goldentooth_agent.core.logging import get_logger
from logging import Logger
from rich.pretty import Pretty
from rich.table import Table
from antidote import injectable
from atomic_agents.lib.base.base_io_schema import BaseIOSchema
from atomic_agents.lib.base.base_tool import BaseTool
from goldentooth_agent.core.named_registry import NamedRegistry, make_register_fn
from goldentooth_agent.core.thunk import Thunk
from rich.table import Table
from .base import Role

@injectable()
class RoleRegistry(NamedRegistry[Role]):
  """Registry for managing roles."""

  @inject.method
  def dump(self, logger: Logger = inject[get_logger(__name__)]) -> Table:
    """Dump all registered roles to a table."""
    logger.debug("Dumping all registered roles to a table")
    table = Table(title="Registered Roles")
    table.add_column("Name", justify="left", style="cyan", no_wrap=True)
    table.add_column("Data", justify="left", style="magenta")
    for name, role in self.items():
      role_dict = {
        "name": role.name,
        "context_providers": role.context_provider_ids,
        "tools": role.tool_ids,
      }
      table.add_row(name, Pretty(role_dict))
    return table
