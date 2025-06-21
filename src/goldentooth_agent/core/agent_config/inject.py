from antidote import inject, lazy
from atomic_agents.lib.components.agent_memory import AgentMemory
from atomic_agents.lib.components.system_prompt_generator import SystemPromptGenerator
from atomic_agents.agents.base_agent import BaseAgentInputSchema, BaseAgentOutputSchema, BaseAgentConfig
from goldentooth_agent.core.client import get_client
from goldentooth_agent.core.system_prompt import get_system_prompt_generator
from instructor import Instructor

DEFAULT_MODEL_VERSION = 'claude-3-5-sonnet-20240620'

@lazy
def get_model_version() -> str:
  """Get the model version."""
  return DEFAULT_MODEL_VERSION

@lazy
def get_agent_memory() -> AgentMemory:
  """Get the agent memory instance."""
  return AgentMemory()

@lazy
def get_default_agent_config(
  client: Instructor = inject[get_client()],
  memory: AgentMemory = inject[get_agent_memory()],
  model_version: str = inject[get_model_version()],
  system_prompt_generator: SystemPromptGenerator = inject[get_system_prompt_generator()],
) -> BaseAgentConfig:
  """Create an instance of DefaultAgentConfig."""
  return BaseAgentConfig(
    client=client,
    memory=memory,
    model=model_version,
    system_prompt_generator=system_prompt_generator,
    input_schema=BaseAgentInputSchema,
    output_schema=BaseAgentOutputSchema,
    max_tokens=4096,
  )
