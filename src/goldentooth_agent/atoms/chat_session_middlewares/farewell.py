from antidote import inject
from rich.console import Console
from ...console import get_console
from ...pipeline import NextMiddleware, middleware
from ...chat_session import ChatSessionContext

@middleware
@inject
async def farewell(
  context: ChatSessionContext,
  next: NextMiddleware,
  console: Console = inject[get_console],
):
  console.print("✌️")
  await next()
