from antidote import inject, instanceOf, world
from rich.console import Console
from pydantic import BaseModel
from goldentooth_agent.core.agent import AgentBase
from goldentooth_agent.foundation.console import get_console
from goldentooth_agent.foundation.pipeline import NextMiddleware, middleware
from .context import ChatSessionLoopContext

def schema_message_middleware(
  schema: type[BaseModel],
  role: str = 'assistant',
  style: str = "greeting",
  type: str = "message"
):
  """Middleware generator to print a message from a schema."""
  @middleware
  @inject
  async def _middleware(
    context: ChatSessionLoopContext,
    next: NextMiddleware,
    console: Console = inject[get_console()],
    agent: AgentBase = inject.me(),
  ):
    message = "Hello, world!"
    schema_instance = schema(chat_message=message)
    agent.output_schema = schema
    agent.memory.add_message(role, schema_instance) # type: ignore
    if style:
      console.print(f"[{style}]{message}[/{style}]")
    else:
      console.print(message)
    await next()
  return _middleware
