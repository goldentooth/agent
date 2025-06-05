from antidote import inject, instanceOf, world
from rich.console import Console
from ...agent import AgentBase
from ...persona import get_persona
from ...console import get_console
from ...pipeline import NextMiddleware, middleware
from ...chat_loop import ChatLoopContext
from ..provider import GreetingProvider
from ..schemata import GreetingSchema

@middleware
@inject
async def greeting(
  context: ChatLoopContext,
  next: NextMiddleware,
  console: Console = inject[get_console],
  agent: AgentBase = inject.me(),
  persona = inject[get_persona()]
):
  greeting_provider = world[instanceOf(GreetingProvider).single(qualified_by=persona)]
  greeting_message = await greeting_provider.get_greeting()
  agent.output_schema = GreetingSchema
  agent.memory.add_message('assistant', GreetingSchema(chat_message=greeting_message))
  console.print(f"[bold yellow]{greeting_message}[/bold yellow]")
  console.print(context)
  await next()

