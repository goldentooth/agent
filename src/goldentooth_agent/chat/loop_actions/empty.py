from ..loop import ChatLoopContext

async def empty(context: ChatLoopContext) -> ChatLoopContext:
  """Empty action for the chat loop, which does nothing."""
  print("Empty action executed in chat loop.")
  return ChatLoopContext()
