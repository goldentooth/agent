from antidote import injectable
from .context import ChatLoopContext
from ...pipeline import Pipeline

@injectable
class ChatLoopPipeline(Pipeline):
  """Pipeline for executing middleware in the core chat loop."""

  def __init__(self) -> None:
    super().__init__(ChatLoopContext)
