from antidote import inject, lazy
from atomic_agents.lib.components.agent_memory import AgentMemory
from atomic_agents.agents.base_agent import BaseAgentInputSchema, BaseAgentOutputSchema, BaseAgentConfig
from goldentooth_agent.core.client import get_client
from goldentooth_agent.core.model import get_model_version

@lazy
@inject
def get_agent_config(
  client = inject[get_client()],
  model_version = inject[get_model_version()],
) -> BaseAgentConfig:
  """Create an instance of DefaultAgentConfig."""
  return BaseAgentConfig(
    client=client,
    model=model_version,
    memory=AgentMemory(),
    input_schema=BaseAgentInputSchema,
    output_schema=BaseAgentOutputSchema,
    max_tokens=4096,
  )
