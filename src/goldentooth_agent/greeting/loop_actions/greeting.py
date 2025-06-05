from ...chat.loop import ChatLoopContext, ChatLoopPipeline
from ..loop_middlewares import greeting as greeting_mw

async def greeting(context: ChatLoopContext) -> ChatLoopContext:
  """Greeting action for the chat loop, which greets the user."""
  pipeline = ChatLoopPipeline()
  pipeline.use(greeting_mw)
  await pipeline.run(context)
  context.next_action = None
  return context
