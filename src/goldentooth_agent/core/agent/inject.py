from atomic_agents.agents.base_agent import BaseAgent, BaseAgentConfig
from antidote import inject, lazy
from goldentooth_agent.core.agent_config import get_default_agent_config

@lazy
@inject
def get_default_agent(config: BaseAgentConfig = inject[get_default_agent_config()]) -> BaseAgent:
  """Create an instance of AgentBase with the default configuration."""
  return BaseAgent(config=config)
