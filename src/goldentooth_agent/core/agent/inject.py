from atomic_agents.agents.base_agent import BaseAgent, BaseAgentConfig
from antidote import inject, lazy
from goldentooth_agent.core.agent_config import get_default_agent_config
from .registry import AgentRegistry

@lazy
def get_default_agent(
  config: BaseAgentConfig = inject[get_default_agent_config()],
  registry: AgentRegistry = inject.me()
) -> BaseAgent:
  """Create an instance of AgentBase with the default configuration."""
  result = BaseAgent(config=config)
  registry.set_default(result)
  return result
