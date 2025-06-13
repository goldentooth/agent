from antidote import inject
from dataclasses import dataclass
from goldentooth_agent.core.agent import AgentBase
from goldentooth_agent.core.console import get_console
from goldentooth_agent.core.log import get_logger
from goldentooth_agent.core.schema import InputSchema, OutputSchema
from goldentooth_agent.core.thunk import Thunk
from goldentooth_agent.core.tool import ToolRegistry
import logging
from logging import Logger
from rich.console import Console
from typing import Optional

@dataclass
class AgentContext:
  """The fold accumulator: all state needed for the next agent step."""
  agent: AgentBase
  tool_registry: ToolRegistry
  user_input: Optional[str] = None
  agent_output: Optional[str] = None

def agent_step_th() -> Thunk[AgentContext, AgentContext]:
  """Single step of the agent's loop: read, run, render, repeat."""
  @inject
  async def _thunk(
    ctx: AgentContext,
    console: Console = inject[get_console()],
    logger: Logger = inject[get_logger(__name__)],
  ) -> AgentContext:
    ctx.agent.input_schema = InputSchema
    ctx.agent.output_schema = OutputSchema
    ctx.user_input = console.input("\n[bold blue]You:[/bold blue] ")
    logger.debug(f"User input: {ctx.user_input}")
    input_schema = InputSchema.from_input(ctx.user_input)
    logger.debug(f"Input schema: {input_schema}")
    output_schema: OutputSchema = ctx.agent.run(input_schema) # type: ignore
    logger.debug(f"Output schema: {output_schema}")
    ctx.agent_output = output_schema.output
    logger.info(f"Agent output: {ctx.agent_output}")
    console.print(f"[bold yellow]Goldentooth:[/bold yellow] {ctx.agent_output}")
    return ctx
  return Thunk(_thunk)

def agent_chat_loop_th(initial_context: AgentContext) -> Thunk[None, None]:
  """Creates a thunk that runs the chat loop."""
  @inject
  async def _thunk(_: None, logger: Logger = inject[get_logger(__name__)]) -> None:
    ctx = initial_context
    while True:
      ctx = await agent_step_th()(ctx)
      logger.debug(f"Current context: {ctx}")
  return Thunk(_thunk)
