from typing import TypeVar, Generic, Callable, Awaitable, Optional

TIn = TypeVar('TIn')
TOut = TypeVar('TOut')

class Thunk(Generic[TIn, TOut]):
  """A thunk is a callable that takes a context and returns an optional output."""
  def __init__(self, fn: Callable[[TIn], Awaitable[Optional[TOut]]]):
    self.fn = fn

  async def __call__(self, ctx: TIn) -> Optional[TOut]:
    """Call the thunk with the given context."""
    return await self.fn(ctx)

def compose[A, B, C](
  f: Thunk[A, B],
  g: Thunk[B, C]
) -> Thunk[A, C]:
  """Compose two thunks, where the output of the first is the input to the second."""
  async def composed(ctx: A) -> Optional[C]:
    """Compose two thunks."""
    intermediate = await f(ctx)
    if intermediate is None:
      return None
    return await g(intermediate)
  return Thunk(composed)
