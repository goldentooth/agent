from antidote import implements, injectable, inject
import instructor
from ..agent import AgentConfigBase
from .client import get_client

@implements(AgentConfigBase)
@injectable(factory_method='create')
class DefaultAgentConfig(AgentConfigBase):
  """Default agent config implementation that extends the AgentConfigBase class."""

  @classmethod
  @inject
  def create(cls, get_client = inject[get_client]) -> 'DefaultAgentConfig':
    """Create an instance of DefaultAgentConfig."""
    return cls(
      client=get_client(),
    )
