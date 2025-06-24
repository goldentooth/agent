from __future__ import annotations
import anthropic
from antidote import inject, injectable
from atomic_agents.agents.base_agent import BaseAgentConfig
from atomic_agents.lib.components.agent_memory import AgentMemory
from goldentooth_agent.core.logging import get_logger
from goldentooth_agent.core.named_registry import NamedRegistry, make_register_fn
import instructor
from logging import Logger
from rich.table import Table

DEFAULT_MODEL_VERSION = 'claude-3-5-sonnet-20240620'

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

def register_default_agent_config() -> None:
  """Create an instance of BaseAgentConfig with the default configuration."""
  agent_config = BaseAgentConfig(
    client=instructor.from_anthropic(anthropic.Anthropic()),
    memory=AgentMemory(),
    model=DEFAULT_MODEL_VERSION,
    max_tokens=4096,
  )
  register_agent_config(name='default', obj=agent_config)

register_default_agent_config()
