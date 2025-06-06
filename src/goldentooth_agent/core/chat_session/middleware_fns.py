from antidote import inject
from rich.console import Console
from goldentooth_agent.core.console import get_console
from goldentooth_agent.core.pipeline import NextMiddleware, middleware
from .context import ChatSessionContext

def print_message_middleware(message: str, style: str = ""):
  """Middleware generator returning a middleware to print a message to the console with optional styling."""
  @middleware
  @inject
  async def _middleware(
    context: ChatSessionContext,
    next: NextMiddleware,
    console: Console = inject[get_console()]
  ):
    console.print(f"[{style}]{message}[/{style}]" if style else message)
    await next()
  return _middleware
