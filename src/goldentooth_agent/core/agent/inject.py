from atomic_agents.agents.base_agent import BaseAgent, BaseAgentConfig
from antidote import inject, lazy
from goldentooth_agent.core.agent_config import get_agent_config

@inject
@lazy
def get_agent(config: BaseAgentConfig = inject[get_agent_config()]) -> BaseAgent:
  """Create an instance of AgentBase with the default configuration."""
  return BaseAgent(config=config)
