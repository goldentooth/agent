from antidote import implements, injectable, inject
from atomic_agents.lib.components.agent_memory import AgentMemory
from .base import AgentConfigBase
from .client import get_client
from .model import get_model_version
from goldentooth_agent.foundation.system_prompt import SystemPromptRegistry

@implements(AgentConfigBase)
@injectable(factory_method='create')
class DefaultAgentConfig(AgentConfigBase):
  """Default agent config implementation that extends the AgentConfigBase class."""

  @classmethod
  @inject
  def create(cls,
    client = inject[get_client()],
    model_version = inject[get_model_version()],
    system_prompt_registry: SystemPromptRegistry = inject.me(),
  ):
    """Create an instance of DefaultAgentConfig."""
    system_prompt_generator = system_prompt_registry.get_default()
    return cls(
      client=client,
      model=model_version,
      system_prompt_generator=system_prompt_generator,
      memory=AgentMemory(),
    )
