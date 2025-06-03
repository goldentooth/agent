from antidote import inject
from .base import AgentBase
from ..agent_config import AgentConfigBase

class AgentFactory:
  """Factory class for creating agent instances."""

  @staticmethod
  @inject
  def create_agent(config: AgentConfigBase = inject.me()) -> AgentBase:
    """Create an agent instance based on the provided configuration."""
    if not isinstance(config, AgentConfigBase):
      raise TypeError("config must be an instance of AgentConfigBase")
    return AgentBase(config=config)
