from antidote import inject
from atomic_agents.agents.base_agent import BaseAgent
from atomic_agents.lib.base.base_io_schema import BaseIOSchema
from goldentooth_agent.core.context import Context, context_autothunk, move_context, copy_context, has_context_key
from goldentooth_agent.core.context_provider import AdHocContextProvider
from goldentooth_agent.core.display import DISPLAY_INPUT_KEY
from goldentooth_agent.core.logging import get_logger
from goldentooth_agent.core.system_prompt import enable_context_provider, disable_context_provider
from goldentooth_agent.core.thunk import Thunk, thunk, compose_chain, if_else
from logging import Logger
from rich.text import Text
from typing import Annotated, Callable, Optional
from .context import AGENT_KEY, AGENT_INPUT_KEY, AGENT_OUTPUT_KEY, AGENT_PREFIX_KEY, SHOULD_SKIP_AGENT_KEY
from .registry import AgentRegistry
from .schema import AgentInputConvertible

def thunkify_agent(agent: BaseAgent) -> Thunk[BaseIOSchema, BaseIOSchema]:
  """Convert an agent into a thunk."""
  @thunk(name=f"thunkify_agent({repr(agent)})")
  @inject
  async def _thunkify_agent(params: BaseIOSchema, logger: Logger = inject[get_logger(__name__)]) -> BaseIOSchema:
    """Run the agent with the given parameters."""
    logger.debug(f"Running agent {agent} with parameters: {params}")
    return agent.run(params)
  return _thunkify_agent

def set_should_skip_agent_key(value: bool = True) -> Thunk[Context, Context]:
  """Set the should_skip_agent flag in the context."""
  @thunk(name="set_should_skip_agent")
  @inject
  async def _set_should_exit(ctx: Context, logger: Logger = inject[get_logger(__name__)]) -> Context:
    logger.debug(f"Setting should_skip_agent to {value}")
    ctx.set(SHOULD_SKIP_AGENT_KEY, value)
    return ctx
  return _set_should_exit

def should_skip_agent() -> Callable[[Context], bool]:
  """Check if the agent should be skipped."""
  @inject
  def _should_skip_agent(ctx: Context, logger: Logger = inject[get_logger(__name__)]) -> bool:
    """Check if the agent should be skipped."""
    logger.debug("Checking if agent should be skipped.")
    return ctx.get_or_default(SHOULD_SKIP_AGENT_KEY, lambda: False)
  return _should_skip_agent

def enable_agent_context_provider(agent_name: str, agent_fn: Callable[[], str]) -> Thunk[Context, Context]:
  """Enable a agent's context provider in the system prompt generator."""
  dcp = AdHocContextProvider(title=agent_name, fn=agent_fn)
  return enable_context_provider(dcp)

def disable_agent_context_provider(agent_name: str) -> Thunk[Context, Context]:
  """Disable a agent's context provider in the context."""
  return disable_context_provider(agent_name)

def inject_agent_prefix() -> Thunk[Context, Context]:
  """Inject the agent's text representation into the context."""
  @context_autothunk(name="inject_agent_text")
  @inject
  async def _inject_agent_text(logger: Logger = inject[get_logger(__name__)]) -> Annotated[Text, AGENT_PREFIX_KEY]:
    """Inject the agent's text representation into the context."""
    logger.debug("Injecting agent text representation into the context.")
    return Text.assemble(("Goldentooth: ", "bold yellow"), end="")
  return _inject_agent_text

def prepare_agent_input() -> Thunk[Context, Context]:
  """Create a thunk that prepares the agent input."""
  @context_autothunk(name="prepare_agent_input")
  @inject
  async def _prepare_agent_input(
    input: Annotated[BaseIOSchema, AGENT_INPUT_KEY],
    logger: Logger = inject[get_logger(__name__)],
  ) -> Annotated[BaseIOSchema, AGENT_INPUT_KEY]:
    """Prepare the agent input by ensuring it is in the correct format."""
    logger.debug(f"Preparing agent input: {input}")
    if isinstance(input, AgentInputConvertible):
      return input.as_agent_input()
    return input
  return _prepare_agent_input

def run_agent() -> Thunk[Context, Context]:
  """Create a thunk that runs an agent with the provided input."""
  @context_autothunk(name="run_agent")
  @inject
  async def _run_agent(
    input: Annotated[BaseIOSchema, AGENT_INPUT_KEY],
    agent: Annotated[BaseAgent, AGENT_KEY],
    logger: Logger = inject[get_logger(__name__)],
  ) -> Annotated[Optional[BaseIOSchema], AGENT_OUTPUT_KEY]:
    """Run the agent with the provided input."""
    agent_thunk = thunkify_agent(agent)
    logger.debug(f"Running agent with provided input {input}")
    try:
      output = await agent_thunk(input)
      logger.debug("Agent executed successfully.")
      if isinstance(output, BaseIOSchema):
        logger.debug(f"Agent returned a valid output {output}")
        return output
      else:
        logger.warning("Agent did not return a valid output.")
        return None
    except Exception as e:
      logger.error(f"Error running agent: {e}")
      return None
  return _run_agent

def agent_chain() -> Thunk[Context, Context]:
  """Create a thunk chain for agent operations."""
  from goldentooth_agent.core.intake import INTAKE_KEY
  return if_else(
    should_skip_agent(),
    set_should_skip_agent_key(False),
    compose_chain(
      copy_context(INTAKE_KEY, AGENT_INPUT_KEY),
      inject_agent_prefix(),
      prepare_agent_input(),
      if_else(
        has_context_key(AGENT_INPUT_KEY),
        compose_chain(
          run_agent(),
          if_else(
            has_context_key(AGENT_OUTPUT_KEY),
            move_context(AGENT_OUTPUT_KEY, DISPLAY_INPUT_KEY),
          ),
        ),
      ),
    ),
  )
