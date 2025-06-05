from antidote import inject
from rich.console import Console
from goldentooth_agent.foundation.console import get_console
from goldentooth_agent.foundation.pipeline import NextMiddleware, middleware
from goldentooth_agent.core.chat_session import ChatSessionContext

def print_message_middleware(message: str, style: str = ""):
  @middleware
  @inject
  async def _middleware(context: ChatSessionContext, next: NextMiddleware, console: Console = inject[get_console]):
    console.print(f"[{style}]{message}[/{style}]" if style else message)
    await next()
  return _middleware
