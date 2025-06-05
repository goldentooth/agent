from .context import ChatSessionLoopContext

async def empty(context: ChatSessionLoopContext) -> ChatSessionLoopContext:
  """Empty action for the chat loop, which does nothing."""
  print("Empty action executed in chat loop.")
  return ChatSessionLoopContext()
