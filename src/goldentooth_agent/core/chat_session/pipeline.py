from antidote import injectable
from .context import ChatSessionContext
from ..pipeline import Pipeline

@injectable
class ChatSessionPipeline(Pipeline):
  """Pipeline for executing middleware in a chat session."""

  def __init__(self) -> None:
    super().__init__(ChatSessionContext)
