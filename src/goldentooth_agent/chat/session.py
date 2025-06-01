from antidote import injectable

@injectable(factory_method='create')
class ChatSession:
  """Base class for chat sessions with agents."""

  @classmethod
  def create(cls) -> 'ChatSession':
    """Create a new chat session instance."""
    return cls()

  async def start(self) -> None:
    """Start a chat session with the agent."""
    print("Hello, world!")
