from antidote import inject
from goldentooth_agent.core.agent import AgentBase
from atomic_agents.lib.base.base_io_schema import BaseIOSchema
from goldentooth_agent.core.console import get_console
from goldentooth_agent.core.log import get_logger
from goldentooth_agent.core.pipeline import Middleware, NextMiddleware, middleware
from goldentooth_agent.core.schema import InputSchema, OutputSchema
from goldentooth_agent.core.thunk import Thunk
from logging import Logger
from typing import Any, Type, TypeVar
from rich.console import Console
from .context import AgentContext
from ..pipeline import Pipeline
from ..schema import SchemaBase

def get_agent_th() -> Thunk[Any, AgentBase]:
  """Generator to handle getting the agent."""
  @inject
  async def _thunk(_nil, agent: AgentBase = inject.me()) -> AgentBase:
    """Thunk to return the agent instance."""
    return agent
  return Thunk(_thunk)

def add_message_mw(role: str, message: SchemaBase) -> Middleware:
  """Generator to handle injecting a message into the agent."""
  @middleware
  @inject
  async def _middleware(agent: AgentBase, next: NextMiddleware) -> None:
    agent.memory.add_message(role, message)
    await next()
  return _middleware

def print_agent_mw() -> Middleware:
  """Generator to handle printing the agent's information to the console."""
  @middleware
  @inject
  async def _middleware(agent: AgentBase, next: NextMiddleware) -> None:
    agent.print()
    await next()
  return _middleware

def print_agent_th() -> Thunk[AgentBase, AgentBase]:
  """Generator to handle printing the agent's information to the console as a thunk."""
  @inject
  async def _thunk(agent: AgentBase) -> AgentBase:
    """Thunk to print the agent's information to the console."""
    agent.print()
    return agent
  return Thunk(_thunk)

def print_message_mw(message: SchemaBase):
  """Generator to handle printing a message to the console."""
  @middleware
  @inject
  async def _middleware(_nil, next: NextMiddleware) -> None:
    message.print()
    await next()
  return _middleware

def inject_message_pl(role: str, message: SchemaBase) -> Pipeline[AgentBase]:
  """Generator to handle injecting a message into the pipeline."""
  pipeline = Pipeline()
  pipeline.use(add_message_mw(role, message))
  pipeline.use(print_agent_mw())
  pipeline.use(print_message_mw(message))
  return pipeline

def inject_message_th(role: str, message: SchemaBase) -> Thunk[AgentBase, AgentBase]:
  """Generator to handle injecting a message into the pipeline as a thunk."""
  async def _thunk(agent: AgentBase) -> AgentBase:
    """Thunk to inject a message into the agent's memory."""
    agent.memory.add_message(role, message)
    agent.print()
    message.print()
    return agent
  return Thunk(_thunk)

def inject_greeting_pl(role: str, greeting: str) -> Pipeline[AgentBase]:
  """Generator to handle injecting a greeting message into the pipeline."""
  from goldentooth_agent.core.schema import GreetingSchema
  message = GreetingSchema.from_greeting(greeting)
  return inject_message_pl(role, message)

def inject_greeting_th(role: str, greeting: str) -> Thunk[AgentBase, AgentBase]:
  """Generator to handle injecting a greeting message into the pipeline as a thunk."""
  from goldentooth_agent.core.schema import GreetingSchema
  message = GreetingSchema.from_greeting(greeting)
  return inject_message_th(role, message)

TIn = TypeVar('TIn', bound=BaseIOSchema)
TOut = TypeVar('TOut', bound=BaseIOSchema)

def run_agent_th(agent: AgentBase, input_type: Type[TIn], output_type: Type[TOut]) -> Thunk[TIn, TOut]:
  """Generator for thunk to print a message to the console."""
  @inject
  async def _thunk(input: TIn) -> TOut:
    """Thunk to run a tool and return the appropriate result."""
    agent.input_schema = input_type
    if not isinstance(input, agent.input_schema):
      raise TypeError(f"Input must be of type {agent.input_schema}, got {type(input).__name__}")
    agent.output_schema = output_type
    result = agent.run(input)
    if not isinstance(result, agent.output_schema):
      raise TypeError(f"Output must be of type {agent.output_schema}, got {type(result).__name__}")
    return result
  return Thunk(_thunk)

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
