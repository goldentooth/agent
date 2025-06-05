from antidote import inject, instanceOf, world
from rich.console import Console
from goldentooth_agent.foundation.console import get_console
from goldentooth_agent.foundation.message_provider import MessageProvider
from goldentooth_agent.foundation.persona import get_persona
from goldentooth_agent.foundation.pipeline import NextMiddleware, middleware
from goldentooth_agent.core.agent import AgentBase
from goldentooth_agent.core.chat_session.loop import ChatSessionLoopContext
from .schema import GreetingSchema

@middleware
@inject
async def greeting(
  context: ChatSessionLoopContext,
  next: NextMiddleware,
  console: Console = inject[get_console],
  agent: AgentBase = inject.me(),
  persona = inject[get_persona()]
):
  greeting_provider = world[instanceOf(MessageProvider).single(qualified_by=["greeting", persona])]
  greeting_message = await greeting_provider.get_message()
  agent.output_schema = GreetingSchema
  agent.memory.add_message('assistant', GreetingSchema(chat_message=greeting_message))
  console.print(f"[bold yellow]{greeting_message}[/bold yellow]")
  console.print(context)
  await next()

