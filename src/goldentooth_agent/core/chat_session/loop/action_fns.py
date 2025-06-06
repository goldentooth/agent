from goldentooth_agent.foundation.pipeline import Middleware
from .context import ChatSessionLoopContext
from .pipeline import ChatSessionLoopPipeline

def pipeline_as_action(middlewares: list[Middleware]):
  """Convert a list of middlewares into an action function for the chat session loop."""
  async def action(context: ChatSessionLoopContext) -> ChatSessionLoopContext:
    pipeline = ChatSessionLoopPipeline()
    for mw in middlewares:
      pipeline.use(mw)
    context.next_action = None
    await pipeline.run(context)
    return context
  return action
