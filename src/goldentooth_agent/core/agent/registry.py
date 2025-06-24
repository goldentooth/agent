from __future__ import annotations
from antidote import inject, injectable
from atomic_agents.agents.base_agent import BaseAgent
from atomic_agents.lib.base.base_io_schema import BaseIOSchema
from goldentooth_agent.core.agent_config import AgentConfigRegistry
from goldentooth_agent.core.logging import get_logger
from goldentooth_agent.core.named_registry import NamedRegistry, make_register_fn
from goldentooth_agent.core.thunk import Thunk
from logging import Logger
from rich.table import Table

@injectable()
class AgentRegistry(NamedRegistry[BaseAgent]):
  """Registry for managing agents."""

  def get_thunk(self, agent_name: str) -> Thunk[BaseIOSchema, BaseIOSchema]:
    """Get a thunk for the specified agent name."""
    from .thunk import thunkify_agent
    agent = self.get(agent_name)
    return thunkify_agent(agent)

  def get_by_input_schema(self, schema: type[BaseIOSchema]) -> BaseAgent:
    """Get an agent by its input schema."""
    for agent in self.all():
      if issubclass(schema, agent.input_schema):
        return agent
    raise LookupError(f"No agent found for input schema: {schema}")

  @inject.method
  def dump(self, logger: Logger = inject[get_logger(__name__)]) -> Table:
    """Dump the registry to the console."""
    logger.debug("Dumping agent registry")
    table = Table(title=f"Agent Registry Dump")
    table.add_column("Name")
    table.add_column("Agent", overflow="fold")
    for k, v in self.items():
      table.add_row(str(k), repr(v))
    return table

register_agent = make_register_fn(AgentRegistry)

@inject
def register_default_agent(agent_config_registry: AgentConfigRegistry = inject.me()) -> None:
  """Create an instance of BaseAgent with the default configuration."""
  config = agent_config_registry.get('default')
  register_agent(name='default', obj=BaseAgent(config=config))

register_default_agent()
