from antidote import inject
from rich.console import Console
from ...console import get_console
from ...pipeline import NextMiddleware, middleware
from ..session import ChatSessionContext

@middleware
@inject
async def greeting_mw(
  context: ChatSessionContext,
  next: NextMiddleware,
  console: Console = inject[get_console],
):
  console.print("Welcome to Goldentooth!")
  console.print(context)
  await next()

