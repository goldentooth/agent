from antidote import inject
from ...pipeline import NextMiddleware, middleware
from ..session import ChatSessionContext
from ..loop import ChatLoopContext

@middleware
@inject
async def core_loop(
  context: ChatSessionContext,
  next: NextMiddleware,
  chat_loop_context: ChatLoopContext = inject.me()
):
  """Core loop for the chat session, executing the next pipeline until exit condition."""
  print("Starting core loop with context:", chat_loop_context)
  while chat_loop_context.next_action is not None:
    print("Current action:", chat_loop_context.next_action)
    chat_loop_context = await chat_loop_context.next_action(chat_loop_context)
  print("Exiting core loop, final context:", chat_loop_context)
  await next()
