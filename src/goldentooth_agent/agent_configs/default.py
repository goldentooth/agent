from antidote import implements, injectable, inject
from ..agent_config import AgentConfigBase
from ..agent_config.client import get_client
from ..agent_config.model import get_model_version
from ..agent_config.persona import get_persona
from ..agent_config.system_prompt_generator import get_system_prompt_generator

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
    persona = inject[get_persona()],
  ):
    """Create an instance of DefaultAgentConfig."""
    return cls(
      client=client,
      model=model_version,
      system_prompt_generator=system_prompt_generator,
      persona=persona,
    )
