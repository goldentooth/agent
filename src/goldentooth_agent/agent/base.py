from atomic_agents.agents.base_agent import BaseAgent
from antidote import interface, inject
from .config import AgentConfigBase

@interface
class AgentBase(BaseAgent):
  """Abstract base class for all agents."""

  @inject
  def __init__(self, config: AgentConfigBase = inject.me()) -> None:
    """Initialize the agent with the provided configuration."""
    super().__init__(config=config)
