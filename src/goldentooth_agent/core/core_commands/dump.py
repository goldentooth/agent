from antidote import inject
from goldentooth_agent.core.command import get_command_typer, enroll_command
from goldentooth_agent.core.console import get_console
from goldentooth_agent.core.context import Context
from goldentooth_agent.core.logging import get_logger
from logging import Logger
from rich.console import Console
import typer
from typer import Typer, Context as TyperContext
from typing import Annotated, Protocol

@enroll_command
@inject
def enroll_dump_command(
  app: Typer = inject[get_command_typer()],
  console: Console = inject[get_console()],
  logger: Logger = inject[get_logger(__name__)],
) -> None:
  """Enroll the dump command."""
  logger.debug("Enrolling dump command...")
  @app.command("dump", help="Dump some thing that is dumpable.")
  def _command(
    typer_context: TyperContext,
    thing: Annotated[str, typer.Argument(help="Name of the thing to dump, e.g. 'context'")],
  ) -> None:
    """Dump the context."""
    logger.debug("Executing dump-context command...")
    context: Context = typer_context.obj
    values = get_dumpables()
    values["context"] = context
    dumpable = dumpable_from_string(thing, values)
    console.print(dumpable.dump())

class Dumpable(Protocol):
  """An object that can be dumped to a table."""
  from rich.table import Table
  def dump(self) -> Table:
    """Dump the object to a table."""
    ...

def get_dumpables() -> dict[str, Dumpable]:
  """Get all dumpable objects."""
  from antidote import world
  from goldentooth_agent.core.agent import AgentRegistry
  from goldentooth_agent.core.command import CommandRegistry
  from goldentooth_agent.core.context_provider import ContextProviderRegistry, YamlContextProviderStore
  from goldentooth_agent.core.system_prompt import SystemPromptRegistry, YamlSystemPromptStore
  from goldentooth_agent.core.tool import ToolRegistry
  result: dict[str, Dumpable] = {}
  result["agent_registry"] = world[AgentRegistry]
  result["command_registry"] = world[CommandRegistry]
  result["context_provider_registry"] = world[ContextProviderRegistry]
  result["context_provider_store"] = world[YamlContextProviderStore]
  result["system_prompt_registry"] = world[SystemPromptRegistry]
  result["system_prompt_store"] = world[YamlSystemPromptStore]
  result["tool_registry"] = world[ToolRegistry]
  return result

def dumpable_from_string(thing: str, values: dict[str, Dumpable]) -> Dumpable:
  """Convert a string to a Dumpable object."""
  if thing in values:
    return values[thing]
  else:
    raise ValueError(f"Unknown dumpable: {thing}. Available dumpables: {', '.join(values.keys())}")
