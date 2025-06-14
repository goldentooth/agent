from antidote import inject, lazy
from atomic_agents.agents.base_agent import BaseAgent
from goldentooth_agent.core.agent import get_agent
from .context import ChatContext

@lazy
@inject
def get_chat_context(
  agent: BaseAgent = inject[get_agent()],
) -> ChatContext:
  """Create an instance of ChatContext."""
  return ChatContext(
    agent=agent,
  )
