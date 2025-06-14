from __future__ import annotations
from typing import Any, AsyncIterator, Awaitable, Callable, Generic, overload, TypeVar

TIn = TypeVar('TIn')
TOut = TypeVar('TOut')
TNew = TypeVar('TNew')

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
      """Call the synchronous function in an async context."""
      return fn(ctx)
    return cls(_async_fn)

  @classmethod
  def from_thunks(cls, *thunks) -> Thunk[TIn, TOut]:
    """Create a thunk that runs multiple thunks in sequence."""
    return compose_chain(*thunks)

  def map(self, fn: Callable[[TOut], TNew]) -> Thunk[TIn, TNew]:
    """Map a function over the result of the thunk."""
    async def _mapped(ctx: TIn) -> TNew:
      """Call the thunk and apply the function to its result."""
      return fn(await self(ctx))
    return Thunk(_mapped)

  def filter(self, predicate: Callable[[TOut], bool]) -> Thunk[TIn, TOut | None]:
    """Filter the result of the thunk based on a predicate."""
    async def _filtered(ctx: TIn) -> TOut | None:
      """Call the thunk and return the result if it matches the predicate."""
      result = await self(ctx)
      return result if predicate(result) else None
    return Thunk(_filtered)

  def flat_map(self, fn: Callable[[TOut], Thunk[TIn, TNew]]) -> Thunk[TIn, TNew]:
    """Flat-map a function over the result of the thunk."""
    async def _flat(ctx: TIn) -> TNew:
      """Call the thunk, get the result, and apply the function to it."""
      return await fn(await self(ctx))(ctx)
    return Thunk(_flat)

  def then(self, next_thunk: Thunk[TIn, TNew]) -> Thunk[TIn, TNew]:
    """Run the next thunk, discarding the result of the current one."""
    async def _thunk(ctx: TIn) -> TNew:
      """Call this thunk, then run the next thunk with the same context."""
      _ = await self(ctx)
      return await next_thunk(ctx)
    return Thunk(_thunk)

  def flatten(self: Thunk[TIn, Thunk[TIn, TNew]]) -> Thunk[TIn, TNew]:
    """Collapse a thunk-of-thunks into a single thunk."""
    async def _flattened(ctx: TIn) -> TNew:
      """Call this thunk, which returns another thunk, and execute it."""
      inner = await self(ctx)
      return await inner(ctx)
    return Thunk(_flattened)

  def __rshift__(self, other: Thunk[TOut, TNew]) -> Thunk[TIn, TNew]:
    """Compose this thunk with another, where the output of this is the input to the other."""
    async def _thunk(ctx: TIn) -> TNew:
      """Call self, then pass its result to the second thunk."""
      result = await self(ctx)
      return await other(result)
    return Thunk(_thunk)

  from .event_thunk import EventThunk
  def events(self) -> EventThunk[TIn, TOut]:
    """Convert this thunk to an event thunk."""
    from .event_thunk import EventThunk
    async def _fn(ctx: TIn) -> AsyncIterator[TOut]:
      """Call the thunk with the context and yield its results."""
      yield await self(ctx)
    return EventThunk(_fn)

  from .stream_thunk import StreamThunk
  def stream(self) -> StreamThunk[TIn, TOut]:
    """Convert this thunk to a stream thunk."""
    from .stream_thunk import StreamThunk
    async def _fn(stream: AsyncIterator[TIn]) -> AsyncIterator[TOut]:
      """Call the thunk with a stream and yield its results."""
      async for ctx in stream:
        yield await self(ctx)
    return StreamThunk(_fn)

def thunk(fn: Callable[[TIn], Awaitable[TOut]]) -> Thunk[TIn, TOut]:
  """Decorator to mark a function as a thunk."""
  return Thunk(fn)

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
    """Run a series of thunks in sequence, passing the context through each."""
    value = await thunks[0](ctx)
    for thunk in thunks[1:]:
      value = await thunk(value)
    return value
  return Thunk(_composed)
