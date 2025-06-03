from antidote import implements, inject
from ..agent import AgentBase
from ..agent_config import AgentConfigBase

@implements(AgentBase)
class DefaultAgent(AgentBase):
  """Default agent implementation that extends the AgentBase class."""

  @inject
  def __init__(self, config: AgentConfigBase = inject.me()):
    """Initialize the default agent with the provided configuration."""
    print("Default agent initialized with config:", config.model_dump())
    super().__init__(config=config)
