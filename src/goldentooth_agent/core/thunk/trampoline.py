from __future__ import annotations
from typing import Generic, TypeVar, Union, cast
from dataclasses import dataclass
from .thunk import Thunk

T = TypeVar('T')
Ctx = TypeVar('Ctx')
TIn = TypeVar('TIn')
TOut = TypeVar('TOut')

@dataclass
class Done(Generic[T]):
  value: T

@dataclass
class Call(Generic[Ctx, T]):
  thunk: Thunk[Ctx, Bounce[Ctx, T]]
  ctx: Ctx

Bounce = Union[Done[T], Call[Ctx, T]]

async def trampoline(ctx: Ctx, thunk: Thunk[Ctx, Bounce[Ctx, T]]) -> T:
  current_thunk = thunk
  current_ctx = ctx

  while True:
    result = await current_thunk(current_ctx)
    if isinstance(result, Done):
      return cast(T, result.value)
    elif isinstance(result, Call):
      result = cast(Call[Ctx, T], result)
      current_thunk = result.thunk
      current_ctx = result.ctx
    else:
      raise TypeError(f"Unexpected result: {result}")
