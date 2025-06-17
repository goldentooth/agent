from goldentooth_agent.core.thunk import Thunk, thunk, compose_chain
from typing import Awaitable, Callable
from .key import context_key
from .main import Context

SHOULD_EXIT_KEY = context_key("should_exit", bool)

async def trampoline(ctx: Context, fn: Callable[[Context], Awaitable[Context]]) -> Context:
  """Run a thunk in a trampoline style until an exit signal is returned."""
  while True:
    ctx = await fn(ctx)
    if ctx.get_or_default(SHOULD_EXIT_KEY, lambda: False):
      return ctx

def trampoline_chain(*steps: Thunk[Context, Context]) -> Thunk[Context, Context]:
  """Execute each thunk in sequence, checking for exit after each step."""
  @thunk
  async def _loop(ctx: Context) -> Context:
    for step in steps:
      ctx = await step(ctx)
      if ctx.get_or_default(SHOULD_EXIT_KEY, lambda: False):
        break
    return ctx
  return _loop
