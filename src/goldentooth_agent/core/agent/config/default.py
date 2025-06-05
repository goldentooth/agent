from antidote import implements, injectable, inject
from atomic_agents.lib.components.agent_memory import AgentMemory
from .base import AgentConfigBase
from .client import get_client
from .model import get_model_version
from .system_prompt_generator import get_system_prompt_generator

@implements(AgentConfigBase)
@injectable(factory_method='create')
class DefaultAgentConfig(AgentConfigBase):
  """Default agent config implementation that extends the AgentConfigBase class."""

  @classmethod
  @inject
  def create(cls,
    client = inject[get_client()],
    model_version = inject[get_model_version()],
    system_prompt_generator = inject[get_system_prompt_generator()],
  ):
    """Create an instance of DefaultAgentConfig."""
    return cls(
      client=client,
      model=model_version,
      system_prompt_generator=system_prompt_generator,
      memory=AgentMemory(),
    )
