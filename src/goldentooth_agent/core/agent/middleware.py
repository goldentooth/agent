from antidote import inject
from goldentooth_agent.core.agent import AgentBase
from atomic_agents.lib.base.base_io_schema import BaseIOSchema
from goldentooth_agent.core.pipeline import Middleware, NextMiddleware, middleware
from goldentooth_agent.core.thunk import Thunk
from typing import Any, Type, TypeVar
from ..pipeline import Pipeline
from ..schema import SchemaBase

@inject
def get_agent_th(agent: AgentBase = inject.me()) -> Thunk[Any, AgentBase]:
  """Generator to handle getting the agent."""
  async def _thunk(_nil) -> AgentBase:
    """Thunk to return the agent instance."""
    return agent
  return Thunk(_thunk)

def add_message_mw(role: str, message: SchemaBase) -> Middleware:
  """Generator to handle injecting a message into the agent."""
  @middleware
  @inject
  async def _middleware(agent: AgentBase, next: NextMiddleware) -> None:
    schema = type(message)
    agent.output_schema = schema
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

def print_message_mw(message: SchemaBase):
  """Generator to handle printing a message to the console."""
  @middleware
  @inject
  async def _middleware(_nil, next: NextMiddleware) -> None:
    message.print()
    await next()
  return _middleware

def inject_message_pl(role: str, message: SchemaBase, agent: AgentBase = inject.me()) -> Pipeline[AgentBase]:
  """Generator to handle injecting a message into the pipeline."""
  pipeline = Pipeline()
  pipeline.use(add_message_mw(role, message))
  pipeline.use(print_agent_mw())
  pipeline.use(print_message_mw(message))
  return pipeline

def inject_message_th(role: str, message: SchemaBase) -> Thunk[AgentBase, AgentBase]:
  """Generator to handle injecting a message into the pipeline as a thunk."""
  pipeline = inject_message_pl(role, message)
  return pipeline.as_thunk()

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
    if not isinstance(input, agent.input_schema):
      raise TypeError(f"Input must be of type {input_type.__name__}, got {type(input).__name__}")
    agent.input_schema = input_type
    agent.output_schema = output_type
    result = agent.run(input)
    if not isinstance(result, agent.output_schema):
      raise TypeError(f"Output must be of type {output_type.__name__}, got {type(result).__name__}")
    return result
  return Thunk(_thunk)
