from antidote import inject
from goldentooth_agent.core.agent import AgentBase
from goldentooth_agent.core.pipeline import Middleware, NextMiddleware, middleware
from ..pipeline import Pipeline
from ..schema import SchemaBase

def add_message_mw(role: str, message: SchemaBase) -> Middleware:
  """Generator to handle injecting a message into the agent."""
  @middleware
  @inject
  async def _middleware(context: object, next: NextMiddleware, agent: AgentBase = inject.me()):
    schema = type(message)
    agent.output_schema = schema
    agent.memory.add_message(role, message)
    await next()
  return _middleware

def print_agent_mw():
  """Generator to handle printing the agent's information to the console."""
  @middleware
  @inject
  async def _middleware(context: object, next: NextMiddleware, agent: AgentBase = inject.me()):
    agent.print()
    await next()
  return _middleware

def print_message_mw(message: SchemaBase):
  """Generator to handle printing a message to the console."""
  @middleware
  @inject
  async def _middleware(context: object, next: NextMiddleware):
    message.print()
    await next()
  return _middleware

def inject_message_pl(role: str, message: SchemaBase):
  """Generator to handle injecting a message into the pipeline."""
  pipeline = Pipeline()
  pipeline.use(add_message_mw(role, message))
  pipeline.use(print_agent_mw())
  pipeline.use(print_message_mw(message))
  return pipeline

def inject_message_th(role: str, message: SchemaBase):
  """Generator to handle injecting a message into the pipeline as a thunk."""
  pipeline = inject_message_pl(role, message)
  return pipeline.as_thunk()

def inject_greeting_pl(role: str, greeting: str):
  """Generator to handle injecting a greeting message into the pipeline."""
  from goldentooth_agent.core.schema import GreetingSchema
  message = GreetingSchema.from_greeting(greeting)
  return inject_message_pl(role, message)

def inject_greeting_th(role: str, greeting: str):
  """Generator to handle injecting a greeting message into the pipeline as a thunk."""
  from goldentooth_agent.core.schema import GreetingSchema
  message = GreetingSchema.from_greeting(greeting)
  return inject_message_th(role, message)
