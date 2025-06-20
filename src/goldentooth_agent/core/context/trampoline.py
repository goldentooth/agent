from antidote import inject
from goldentooth_agent.core.logging import get_logger
from goldentooth_agent.core.thunk import Thunk, thunk
from logging import Logger
from .key import context_key
from .main import Context

SHOULD_BREAK_KEY = context_key("should_break", bool)
SHOULD_EXIT_KEY = context_key("should_exit", bool)

@inject
def set_should_break(value: bool = True, logger: Logger = inject[get_logger(__name__)]) -> Thunk[Context, Context]:
  """Set the should_break flag in the context."""
  @thunk(name="set_should_break")
  async def _set_should_break(ctx: Context) -> Context:
    logger.debug(f"Setting should_break to {value}")
    ctx.set(SHOULD_BREAK_KEY, value)
    return ctx
  return _set_should_break

@inject
def set_should_exit(value: bool = True, logger: Logger = inject[get_logger(__name__)]) -> Thunk[Context, Context]:
  """Set the should_exit flag in the context."""
  @thunk(name="set_should_exit")
  async def _set_should_exit(ctx: Context) -> Context:
    logger.debug(f"Setting should_continue to {value}")
    ctx.set(SHOULD_EXIT_KEY, value)
    return ctx
  return _set_should_exit

@inject
async def trampoline(ctx: Context, thunk: Thunk[Context, Context], logger: Logger = inject[get_logger(__name__)]) -> Context:
  """Run a thunk in a trampoline style until an exit signal is returned."""
  while True:
    ctx = await thunk(ctx)
    if ctx.get_or_default(SHOULD_EXIT_KEY, lambda: False):
      logger.debug("Exit requested, breaking trampoline loop.")
      return ctx
    if ctx.get_or_default(SHOULD_BREAK_KEY, lambda: False):
      logger.debug("Break requested, resetting should_break flag and restarting the loop.")
      ctx.set(SHOULD_BREAK_KEY, False)
      continue

@inject
def exitable_chain(*steps: Thunk[Context, Context], logger: Logger = inject[get_logger(__name__)]) -> Thunk[Context, Context]:
  """Execute each thunk in sequence, checking for exit after each step."""
  @thunk(name=f"exitable_chain({', '.join(step.name for step in steps)})")
  async def _loop(ctx: Context) -> Context:
    for step in steps:
      ctx = await step(ctx)
      if ctx.get_or_default(SHOULD_EXIT_KEY, lambda: False):
        logger.debug("Exit requested, breaking chain loop.")
        break
      if ctx.get_or_default(SHOULD_BREAK_KEY, lambda: False):
        logger.debug("Break requested, resetting should_break flag and restarting the loop.")
        ctx.set(SHOULD_BREAK_KEY, False)
        continue
    return ctx
  return _loop

@inject
def trampoline_chain(*steps: Thunk[Context, Context], logger: Logger = inject[get_logger(__name__)]) -> Thunk[Context, Context]:
  """Repeat the chain in trampoline style until exit is requested."""
  chain = exitable_chain(*steps)
  @thunk(name=f"trampoline_chain({', '.join(step.name for step in steps)})")
  async def _loop(ctx: Context) -> Context:
    logger.debug("Starting trampoline chain loop...")
    return await trampoline(ctx, chain)
  return _loop
