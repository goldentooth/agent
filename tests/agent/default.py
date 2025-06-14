from antidote import implements, inject
from .base import AgentBase
from .config import AgentConfigBase

@implements(AgentBase)
class DefaultAgent(AgentBase):
  """Default agent implementation that extends the AgentBase class."""

  @inject
  def __init__(self, config: AgentConfigBase = inject.me()):
    """Initialize the default agent with the provided configuration."""
    super().__init__(config=config)
