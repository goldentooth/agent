from antidote import inject, instanceOf, world
from rich.console import Console
from pydantic import BaseModel
from typing import Awaitable, Callable
from goldentooth_agent.core.agent import AgentBase
from goldentooth_agent.foundation.console import get_console
from goldentooth_agent.foundation.message_provider import MessageProvider
from goldentooth_agent.foundation.persona import Persona, get_persona
from goldentooth_agent.foundation.pipeline import NextMiddleware, middleware
from .context import ChatSessionLoopContext

@inject
def get_message_provider(type: str, persona: Persona = inject[get_persona()]) -> MessageProvider:
  """Get the message provider for a given type and persona."""
  return world[instanceOf(MessageProvider).single(qualified_by=[type, persona])]

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
    console: Console = inject[get_console],
    agent: AgentBase = inject.me(),
  ):
    message_provider: MessageProvider = get_message_provider(type)
    message = await message_provider.get_message()
    schema_instance = schema(chat_message=message)
    agent.output_schema = schema
    agent.memory.add_message(role, schema_instance) # type: ignore
    if style:
      console.print(f"[{style}]{message}[/{style}]")
    else:
      console.print(message)
    await next()
  return _middleware
