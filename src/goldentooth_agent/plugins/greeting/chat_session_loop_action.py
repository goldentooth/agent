from goldentooth_agent.core.chat_session.loop import ChatSessionLoopContext, ChatSessionLoopPipeline
from .chat_session_loop_middleware import greeting as greeting_mw

async def greeting(context: ChatSessionLoopContext) -> ChatSessionLoopContext:
  """Greeting action for the chat loop, which greets the user."""
  pipeline = ChatSessionLoopPipeline()
  pipeline.use(greeting_mw)
  context.next_action = None
  await pipeline.run(context)
  return context
