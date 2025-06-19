from __future__ import annotations
from typing import Generic, AsyncIterator, Awaitable, Callable, TypeVar, Any, TYPE_CHECKING

TIn = TypeVar('TIn')
TOut = TypeVar('TOut')
TNew = TypeVar('TNew')

class StreamThunk(Generic[TIn, TOut]):
  """A thunk that processes an asynchronous stream of values."""

  def __init__(
    self,
    fn: Callable[[AsyncIterator[TIn]], AsyncIterator[TOut]],
    name: str,
    metadata: dict[str, Any] = {},
  ):
    """Initialize the stream thunk with a function that processes the stream."""
    if not callable(fn):
      raise TypeError("StreamThunk requires a callable")
    self.fn = fn
    self.name = name or fn.__name__ or "<anonymous>"
    self.metadata: dict[str, Any] = metadata
    self.__name__ = self.name

  def __call__(self, stream: AsyncIterator[TIn]) -> AsyncIterator[TOut]:
    """Call the thunk with the given stream and return an async iterator."""
    return self.fn(stream)

  def pipe(self, next: StreamThunk[TOut, Any]) -> StreamThunk[TIn, Any]:
    """Pipe the output of this thunk to the next thunk."""
    return StreamThunk(lambda s: next(self(s)), name=f"{self.name} | {next.name}")

  def map(self, fn: Callable[[TOut], TNew]) -> StreamThunk[TIn, TNew]:
    """Map a function over the output of the stream thunk."""
    async def _mapped(stream: AsyncIterator[TIn]) -> AsyncIterator[TNew]:
      """Call the thunk and apply the function to each item in the stream."""
      async for item in self(stream):
        yield fn(item)
    return StreamThunk(_mapped, name=f"{self.name}.map({fn.__name__})")

  def filter(self, predicate: Callable[[TOut], bool]) -> StreamThunk[TIn, TOut]:
    """Filter the output of the stream thunk based on a predicate."""
    async def _filtered(stream: AsyncIterator[TIn]) -> AsyncIterator[TOut]:
      """Call the thunk and yield only items that match the predicate."""
      async for item in self(stream):
        if predicate(item):
          yield item
        else:
          continue
    return StreamThunk(_filtered, name=f"{self.name}.filter({predicate.__name__})")

  def flat_map(self, fn: Callable[[TOut], AsyncIterator[TNew]]) -> StreamThunk[TIn, TNew]:
    """Flat-map a function over the output of the stream thunk."""
    async def _flatmapped(stream: AsyncIterator[TIn]) -> AsyncIterator[TNew]:
      """Call the thunk, get the result, and apply the function to each item."""
      async for item in self(stream):
        async for sub in fn(item):
          yield sub
    return StreamThunk(_flatmapped, name=f"{self.name}.flat_map({fn.__name__})")

  def for_each(self, fn: Callable[[TOut], Awaitable[None]]) -> Callable[[AsyncIterator[TIn]], Awaitable[None]]:
    """Consume the stream and apply a function to each item."""
    async def _consume(stream: AsyncIterator[TIn]) -> None:
      """Consume the stream and apply the function to each item."""
      async for item in self(stream):
        await fn(item)
    return _consume

  def to_list(self) -> Callable[[AsyncIterator[TIn]], Awaitable[list[TOut]]]:
    """Convert the stream to a list."""
    async def _to_list(stream: AsyncIterator[TIn]) -> list[TOut]:
      """Consume the stream and return a list of items."""
      result = []
      async for item in self(stream):
        result.append(item)
      return result
    return _to_list

  def __rshift__(self, other: StreamThunk[TOut, Any]) -> StreamThunk[TIn, Any]:
    """Compose this thunk with another, where the output of this is the input to the other."""
    return self.pipe(other)

  if TYPE_CHECKING:
    from .thunk import Thunk
  def collect(self) -> Thunk[AsyncIterator[TIn], list[TOut]]:
    """Collect all emitted values into a list."""
    from .thunk import Thunk
    async def _collect(stream: AsyncIterator[TIn]) -> list[TOut]:
      """Collect all items emitted by the thunk into a list."""
      return [item async for item in self(stream)]
    return Thunk(_collect, name=f"{self.name}.collect", metadata=self.metadata)
