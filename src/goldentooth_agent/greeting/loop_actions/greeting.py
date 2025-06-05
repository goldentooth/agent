from ...chat_loop import ChatLoopContext, ChatLoopPipeline
from ..loop_middlewares import greeting as greeting_mw

async def greeting(context: ChatLoopContext) -> ChatLoopContext:
  """Greeting action for the chat loop, which greets the user."""
  pipeline = ChatLoopPipeline()
  pipeline.use(greeting_mw)
  context.next_action = None
  await pipeline.run(context)
  return context
