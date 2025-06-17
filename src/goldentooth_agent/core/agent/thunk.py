from antidote import inject
from atomic_agents.agents.base_agent import BaseAgent
from atomic_agents.lib.base.base_io_schema import BaseIOSchema
from goldentooth_agent.core.context import Context, context_autothunk
from goldentooth_agent.core.dynamic_context_provider import DynamicContextProvider
from goldentooth_agent.core.system_prompt import enable_context_provider, disable_context_provider
from goldentooth_agent.core.thunk import Thunk
from rich.text import Text
from typing import Annotated, Callable
from .context import AGENT_INPUT_KEY, AGENT_OUTPUT_KEY, AGENT_KEY, AGENT_TEXT_KEY
from .inject import get_agent
from .schema import AgentInputConvertible

def thunkify_agent(agent: BaseAgent) -> Thunk[BaseIOSchema, BaseIOSchema]:
  """Convert an agent into a thunk."""
  async def _as_thunk(params: BaseIOSchema) -> BaseIOSchema:
    """Run the agent with the given parameters."""
    return agent.run(params)
  return Thunk(_as_thunk)

def enable_agent_context_provider(agent_name: str, agent_fn: Callable[[], str]) -> Thunk[Context, Context]:
  """Enable a agent's context provider in the system prompt generator."""
  dcp = DynamicContextProvider(title=agent_name, fn=agent_fn)
  return enable_context_provider(dcp)

def disable_agent_context_provider(agent_name: str) -> Thunk[Context, Context]:
  """Disable a agent's context provider in the context."""
  return disable_context_provider(agent_name)

def inject_agent() -> Thunk[Context, Context]:
  """Inject a agent into the context."""
  @context_autothunk
  @inject
  async def _inject_agent(
    agent: BaseAgent = inject[get_agent()],
  ) -> Annotated[BaseAgent, AGENT_KEY]:
    """Inject the agent into the context."""
    return agent
  return _inject_agent

def inject_agent_text() -> Thunk[Context, Context]:
  """Inject the agent's text representation into the context."""
  @context_autothunk
  @inject
  async def _inject_agent_text(
    agent: BaseAgent = inject[get_agent()],
  ) -> Annotated[Text, AGENT_TEXT_KEY]:
    """Inject the agent's text representation into the context."""
    return Text.assemble(("Goldentooth: ", "bold yellow"))
  return _inject_agent_text

def prepare_agent_input() -> Thunk[Context, Context]:
  """Create a thunk that prepares the agent input."""
  @context_autothunk
  async def _prepare_agent_input(
    input: Annotated[BaseIOSchema, AGENT_INPUT_KEY],
  ) -> Annotated[BaseIOSchema, AGENT_INPUT_KEY]:
    """Prepare the agent input by ensuring it is in the correct format."""
    if isinstance(input, AgentInputConvertible):
      return input.as_agent_input()
    return input
  return _prepare_agent_input

def run_agent() -> Thunk[Context, Context]:
  """Create a thunk that runs an agent with the provided input."""
  @context_autothunk
  async def _run_agent(
    input: Annotated[BaseIOSchema, AGENT_INPUT_KEY],
    agent: Annotated[BaseAgent, AGENT_KEY],
  ) -> Annotated[BaseIOSchema, AGENT_OUTPUT_KEY]:
    """Run the agent with the provided input."""
    return agent.run(input)
  return _run_agent
