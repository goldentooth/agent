from antidote import injectable, inject
from .context import ChatSessionContext
from .pipeline import ChatSessionPipeline

@injectable(factory_method='create')
class ChatSession:
  """Base class for chat sessions with agents."""

  @inject
  def __init__(self) -> None:
    """Initialize the chat session."""
    self.should_exit = False

  @classmethod
  def create(cls) -> 'ChatSession':
    """Create a new chat session instance."""
    return cls()

  @inject
  async def start(
    self,
    session_context: ChatSessionContext = inject.me(),
    session_pipeline: ChatSessionPipeline = inject.me(),
  ) -> None:
    """Start a chat session with the agent."""
    await session_pipeline.run(session_context)
