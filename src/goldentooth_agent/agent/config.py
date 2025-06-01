from atomic_agents.agents.base_agent import BaseAgentConfig
from antidote import interface

@interface
class AgentConfigBase(BaseAgentConfig):
  """Abstract base class for all agent configs."""
