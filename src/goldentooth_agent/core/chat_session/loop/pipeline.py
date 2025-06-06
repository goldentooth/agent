from __future__ import annotations
from antidote import injectable
from .context import ChatSessionLoopContext
from ...pipeline import Pipeline

@injectable
class ChatSessionLoopPipeline(Pipeline):
  """Pipeline for executing middleware in the core chat loop."""

  def __init__(self) -> None:
    super().__init__(ChatSessionLoopContext)
