from antidote import inject
from goldentooth_agent.foundation.pipeline import NextMiddleware, middleware
from goldentooth_agent.core.chat_session import ChatSessionContext
from goldentooth_agent.core.chat_session.loop import ChatSessionLoopContext

@middleware
@inject
async def core_loop(
  context: ChatSessionContext,
  next: NextMiddleware,
  chat_loop_context: ChatSessionLoopContext = inject.me()
):
  """Core loop for the chat session, executing the next pipeline until exit condition."""
  print("Starting core loop with context:", chat_loop_context)
  chat_loop_context.next_action = context.loop_action
  while chat_loop_context.next_action is not None:
    print("Current action:", chat_loop_context.next_action)
    chat_loop_context = await chat_loop_context.next_action(chat_loop_context)
  print("Exiting core loop, final context:", chat_loop_context)
  await next()
