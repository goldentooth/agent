from __future__ import annotations
from antidote import injectable, inject, world
from atomic_agents.agents.base_agent import BaseAgent
from rich.table import Table
from typing import Dict
from .inject import get_default_agent

@injectable(factory_method='create')
class AgentRegistry:
  """Registry for agents."""

  def __init__(self, default: BaseAgent):
    """Initialize the registry with an empty dictionary."""
    self.agents: Dict[str, BaseAgent] = {}
    self.set_default(default)

  @classmethod
  def create(cls) -> AgentRegistry:
    """Create a new AgentRegistry instance."""
    default = world[get_default_agent()]
    result = cls(default)
    return result

  @inject.method
  def register(self, name: str, agent: BaseAgent):
    """Register an agent with a given name."""
    if name in self.agents:
      raise ValueError(f"Agent '{name}' is already registered.")
    self.agents[name] = agent

  @inject.method
  def get(self, name: str) -> BaseAgent:
    """Retrieve an agent by its name."""
    if name not in self.agents:
      raise KeyError(f"Agent '{name}' is not registered.")
    return self.agents[name]

  @inject.method
  def has(self, name: str) -> bool:
    """Check if an agent is registered by its name."""
    return name in self.agents

  @inject.method
  def remove(self, name: str):
    """Remove an agent by its name."""
    if name not in self.agents:
      raise KeyError(f"Agent '{name}' is not registered.")
    del self.agents[name]

  @inject.method
  def get_default(self) -> BaseAgent:
    """Retrieve the default agent."""
    return self.get('default')

  @inject.method
  def set_default(self, agent: BaseAgent):
    """Set the default agent."""
    if 'default' in self.agents:
      raise ValueError("Default agent is already set.")
    self.agents['default'] = agent

  @inject.method
  def dump(self) -> Table:
    """Dump the context to the console."""
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
