from goldentooth_agent.core.thunk import Thunk, thunk
from typing import Callable
from .context import ChatContext

def alter_chat_context(fn: Callable[[ChatContext], None]) -> Thunk[ChatContext, ChatContext]:
  """Modify the chat context using a provided function."""
  @thunk
  async def _alter(context: ChatContext) -> ChatContext:
    """Apply the modification function to the chat context."""
    fn(context)
    return context
  return _alter
