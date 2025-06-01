from antidote import injectable, inject
from ..agent import AgentBase

@injectable(factory_method='create')
class ChatSession:
  """Base class for chat sessions with agents."""

  @classmethod
  def create(cls) -> 'ChatSession':
    """Create a new chat session instance."""
    return cls()

  @inject
  async def start(self, agent: AgentBase = inject.me()) -> None:
    """Start a chat session with the agent."""
    print("Hello, world!")
