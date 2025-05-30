import instructor
import anthropic
from atomic_agents.lib.components.agent_memory import AgentMemory
from atomic_agents.agents.base_agent import BaseAgent, BaseAgentConfig
from .context_provider_discovery import ContextProviderDiscovery
from .initial_context import InitialContext

MODEL = "claude-sonnet-4-20250514"

class AgentFactory:
  """A factory class for creating a chat agent with a specific initial context."""

  @staticmethod
  def create_agent(initial_context: InitialContext) -> BaseAgent:
    """Create and return a chat agent with the given initial context."""

    agent = BaseAgent(
      config=BaseAgentConfig(
        client=instructor.from_anthropic(anthropic.AsyncClient()),
        memory=AgentMemory(),
        model=MODEL,
        system_prompt_generator=initial_context.get_system_prompt_generator(),
        model_api_parameters={
          "max_tokens": 2048,
        },
      )
    )

    context_provider_discovery = ContextProviderDiscovery()
    context_provider_discovery.populate(agent, initial_context)

    return agent
