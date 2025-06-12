from __future__ import annotations
from typing import Any, Awaitable, Callable, Generic, overload, Protocol, TypeVar
from dataclasses import dataclass

Ctx = TypeVar("Ctx", covariant=True)
T = TypeVar("T", covariant=True)

class BounceBase(Protocol, Generic[Ctx, T]):
  """Base protocol for bounce types used in trampoline execution."""
  pass

@dataclass
class Done(Generic[Ctx, T], BounceBase[Ctx, T]):
  """Represents a completed thunk execution with a value."""
  value: T

@dataclass
class Call(Generic[Ctx, T], BounceBase[Ctx, T]):
  """Represents a thunk that needs to be called with a context."""
  thunk: Thunk[Ctx, BounceBase[Ctx, T]]
  ctx: Ctx

Bounce = BounceBase[Ctx, T]

TIn = TypeVar('TIn')
TOut = TypeVar('TOut')

class Thunk(Generic[TIn, TOut]):
  """A thunk is a callable that takes a context and returns an optional output."""

  def __init__(self, fn: Callable[[TIn], Awaitable[TOut]]):
    """Initialize the thunk with a function."""
    self.fn = fn

  async def __call__(self, ctx: TIn) -> TOut:
    """Call the thunk with the given context."""
    return await self.fn(ctx)

  @classmethod
  def from_callable(cls, fn: Callable[[TIn], Awaitable[TOut]]) -> Thunk[TIn, TOut]:
    """Create a thunk from a callable."""
    return cls(fn)

  @classmethod
  def from_sync_callable(cls, fn: Callable[[TIn], TOut]) -> Thunk[TIn, TOut]:
    """Create a thunk from a synchronous callable."""
    async def _async_fn(ctx: TIn) -> TOut:
      return fn(ctx)
    return cls(_async_fn)

  @classmethod
  def from_thunks(cls, *thunks) -> Thunk[TIn, TOut]:
    """Create a thunk that runs multiple thunks in sequence."""
    return compose_chain(*thunks)

  def as_done(self) -> Thunk[TIn, Done[TIn, TOut]]:
    """Convert the thunk to a thunk that returns a Done type."""
    async def _done_fn(ctx: TIn) -> Done[TIn, TOut]:
      value = await self.fn(ctx)
      return Done(value=value)
    return Thunk(_done_fn)

def thunk(fn: Callable[[TIn], Awaitable[TOut]]) -> Thunk[TIn, TOut]:
  """Decorator to mark a function as a thunk."""
  return Thunk(fn)

def final_thunk() -> Thunk[Ctx, Done[Ctx, Ctx]]:
  """Create a final thunk that returns a Done type."""
  async def _final(ctx: Ctx) -> Done[Ctx, Ctx]:
    return Done(value=ctx)
  return Thunk(_final)

async def trampoline(ctx: Ctx, thunk: Thunk[Ctx, BounceBase[Ctx, T]]) -> T:
  """Run a thunk in a trampoline style to avoid deep recursion."""
  current_thunk = thunk
  current_ctx = ctx
  while True:
    result = await current_thunk(current_ctx)
    if isinstance(result, Done):
      return result.value
    elif isinstance(result, Call):
      current_thunk = result.thunk
      current_ctx = result.ctx
    else:
      raise TypeError(f"Unexpected result: {result}")

A = TypeVar("A")
B = TypeVar("B")
C = TypeVar("C")
D = TypeVar("D")
E = TypeVar("E")

@overload
def compose_chain(*thunks: tuple[Thunk[A, B], Thunk[B, C]]) -> Thunk[A, C]: ...
@overload
def compose_chain(*thunks: tuple[Thunk[A, B], Thunk[B, C], Thunk[C, D]]) -> Thunk[A, D]: ...
@overload
def compose_chain(*thunks: tuple[Thunk[A, B], Thunk[B, C], Thunk[C, D], Thunk[D, E]]) -> Thunk[A, E]: ...
@overload
def compose_chain(*thunks: Thunk[Any, Any]) -> Thunk[Any, Any]: ...
def compose_chain(*thunks):
  """Compose multiple thunks in a chain, where the output of each is the input to the next."""
  if len(thunks) < 2:
    raise ValueError("compose_chain requires at least two thunks.")
  async def _composed(ctx):
    value = await thunks[0](ctx)
    for thunk in thunks[1:]:
      value = await thunk(value)
    return value
  return Thunk(_composed)

if __name__ == "__main__":
  import asyncio

  async def thunk1(ctx: str) -> int:
    print(f"Thunk1 processing: {ctx}")
    return len(ctx)

  async def thunk2(length: int) -> str:
    print(f"Thunk2 processing length: {length}")
    return f"Length is {length}"

  async def thunk3(result: str) -> str:
    print(f"Thunk3 processing result: {result}")
    return result.upper()

  composed = compose_chain(
    Thunk.from_callable(thunk1),
    Thunk.from_callable(thunk2),
    Thunk.from_callable(thunk3)
  )

  result = asyncio.run(composed("Hello, World!"))
  print("Final result:", result)

  composed = compose_chain(
    Thunk.from_callable(thunk1),
    Thunk.from_callable(thunk2),
    Thunk.from_callable(thunk3).as_done(),
  )

  result = asyncio.run(trampoline("Hello, World!", composed))
  print("Trampoline final result:", result)
