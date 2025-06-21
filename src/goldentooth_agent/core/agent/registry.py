from __future__ import annotations
from antidote import injectable, inject, world
from atomic_agents.agents.base_agent import BaseAgent
from goldentooth_agent.core.logging import get_logger
from logging import Logger
from rich.table import Table
from typing import Dict
from .inject import get_default_agent

@injectable(factory_method='create')
class AgentRegistry:
  """Registry for agents."""

  @inject
  def __init__(self, default: BaseAgent = inject[get_default_agent()], logger: Logger = inject[get_logger(__name__)]) -> None:
    """Initialize the registry with an empty dictionary."""
    logger.debug("Initializing AgentRegistry")
    self.agents: Dict[str, BaseAgent] = {}
    self.set_default(default)

  @classmethod
  def create(cls) -> AgentRegistry:
    """Create a new AgentRegistry instance."""
    result = cls()
    return result

  @inject.method
  def register(self, name: str, agent: BaseAgent, logger: Logger = inject[get_logger(__name__)]) -> None:
    """Register an agent with a given name."""
    logger.debug(f"Registering agent '{name}'")
    if name in self.agents:
      raise ValueError(f"Agent '{name}' is already registered.")
    self.agents[name] = agent

  @inject.method
  def get(self, name: str, logger: Logger = inject[get_logger(__name__)]) -> BaseAgent:
    """Retrieve an agent by its name."""
    logger.debug(f"Retrieving agent '{name}'")
    if name not in self.agents:
      raise KeyError(f"Agent '{name}' is not registered.")
    return self.agents[name]

  @inject.method
  def has(self, name: str) -> bool:
    """Check if an agent is registered by its name."""
    return name in self.agents

  @inject.method
  def remove(self, name: str, logger: Logger = inject[get_logger(__name__)]) -> None:
    """Remove an agent by its name."""
    logger.debug(f"Removing agent '{name}'")
    if name not in self.agents:
      raise KeyError(f"Agent '{name}' is not registered.")
    del self.agents[name]

  @inject.method
  def get_default(self, logger: Logger = inject[get_logger(__name__)]) -> BaseAgent:
    """Retrieve the default agent."""
    logger.debug("Retrieving default agent")
    return self.get('default')

  @inject.method
  def set_default(self, agent: BaseAgent, logger: Logger = inject[get_logger(__name__)]) -> None:
    """Set the default agent."""
    logger.debug("Setting default agent")
    if 'default' in self.agents:
      raise ValueError("Default agent is already set.")
    self.agents['default'] = agent

  @inject.method
  def dump(self, logger: Logger = inject[get_logger(__name__)]) -> Table:
    """Dump the context to the console."""
    logger.debug("Dumping agent registry context")
    table = Table(title=f"Context Dump")
    table.add_column("Name")
    table.add_column("Agent", overflow="fold")
    for k in self.agents:
      table.add_row(str(k), repr(self.agents[k]))
    return table

@inject
def register_agent(*, name: str, registry: AgentRegistry = inject.me()):
  """Decorator to register an agent in the AgentRegistry."""
  def _decorator(agent_cls: type[BaseAgent]):
    """Decorator to register an agent class."""
    from antidote import world
    instance = world[agent_cls]
    registry.register(name, instance)
    return agent_cls
  return _decorator
