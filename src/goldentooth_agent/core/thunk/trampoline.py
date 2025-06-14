from __future__ import annotations
from dataclasses import dataclass
from typing import Awaitable, Callable, Generic, TypeVar
from .thunk import Thunk

Ctx = TypeVar("Ctx", covariant=True)

@dataclass
class ShouldExit(Generic[Ctx]):
  def __init__(self, ctx: Ctx):
    """Exception to signal that the trampoline should exit."""
    self.ctx = ctx

async def trampoline(ctx: Ctx, fn: Callable[[Ctx], Awaitable[Ctx]]) -> Ctx:
  """Run a thunk in a trampoline style, allowing for asynchronous execution."""
  while True:
    ctx = await fn(ctx)
    if isinstance(ctx, ShouldExit):
      return ctx

def trampoline_filter(predicate: Callable[[Ctx], bool]) -> Thunk[Ctx, Ctx | ShouldExit[Ctx]]:
  """Create a thunk that filters contexts based on a predicate."""
  async def _thunk(ctx):
    """Thunk to filter contexts based on a predicate."""
    return ctx if predicate(ctx) else ShouldExit(ctx)
  return Thunk(_thunk)
