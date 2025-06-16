from goldentooth_agent.core.thunk import Thunk, thunk
import inspect
from typing import Annotated, Any, Callable, get_args, get_origin
from .key import ContextKey
from .main import Context

def clear_keys(keys: list[ContextKey[Any]]) -> Callable[[Thunk[Context, Context]], Thunk[Context, Context]]:
  """Decorator to clear specified keys from the context after executing a thunk."""
  def _clear_keys(th: Thunk[Context, Context]) -> Thunk[Context, Context]:
    """Decorator to clear specified keys from the context after executing a thunk."""
    @thunk
    async def _wrapped(ctx: Context) -> Context:
      """Execute the thunk and clear specified keys from the context."""
      ctx = await th(ctx)
      for key in keys:
        ctx.forget(key)
      return ctx
    return _wrapped
  return _clear_keys

def clear_key(key: ContextKey[Any]) -> Callable[[Thunk[Context, Context]], Thunk[Context, Context]]:
  """Decorator to clear a specific key from the context after executing a thunk."""
  def _clear_key(th: Thunk[Context, Context]) -> Thunk[Context, Context]:
    """Decorator to clear a specific key from the context after executing a thunk."""
    @thunk
    async def _wrapped(ctx: Context) -> Context:
      """Execute the thunk and clear the specified key from the context."""
      ctx = await th(ctx)
      ctx.forget(key)
      return ctx
    return _wrapped
  return _clear_key

def context_autothunk(fn: Callable[..., Any]) -> Thunk[Context, Context]:
  """Automatically create a thunk from a function by extracting context keys from its parameters and return type."""
  sig = inspect.signature(fn)
  param_keys: list[ContextKey] = []
  param_names: list[str] = []

  for name, param in sig.parameters.items():
    annotation = param.annotation
    if get_origin(annotation) is Annotated:
      _, *meta = get_args(annotation)
      for m in meta:
        if isinstance(m, ContextKey):
          param_keys.append(m)
          param_names.append(name)

  return_annotation = sig.return_annotation
  return_key = None
  if get_origin(return_annotation) is Annotated:
    _, *meta = get_args(return_annotation)
    for m in meta:
      if isinstance(m, ContextKey):
        return_key = m
        break

  async def _wrapped(ctx: Context) -> Context:
    """Execute the thunk with the context, retrieving parameters and setting return value."""
    values = [ctx.get(k) for k in param_keys]
    result = await fn(*values)
    if return_key:
      ctx.set(return_key, result)
    return ctx

  return Thunk(_wrapped)

def move_context(
  source: ContextKey[Any],
  destination: ContextKey[Any],
) -> Thunk[Context, Context]:
  """Thunk to move a context item from one key to another."""
  @thunk
  async def _move_context(ctx: Context) -> Context:
    """Move the context item from one key to another."""
    value = ctx.pop(source)
    ctx.set(destination, value)
    return ctx
  return _move_context

def copy_context(
  source: ContextKey[Any],
  destination: ContextKey[Any],
) -> Thunk[Context, Context]:
  """Thunk to copy a context item from one key to another."""
  @thunk
  async def _copy_context(ctx: Context) -> Context:
    """Copy the context item from one key to another."""
    value = ctx.get(source)
    ctx.set(destination, value)
    return ctx
  return _copy_context

def forget_context(key: ContextKey[Any]) -> Thunk[Context, Context]:
  """Thunk to forget a context key."""
  @thunk
  async def _forget_context(ctx: Context) -> Context:
    """Forget the specified context key."""
    ctx.forget(key)
    return ctx
  return _forget_context

def require_context(*keys: ContextKey[Any]) -> Thunk[Context, Context]:
  """Thunk to require certain context keys."""
  @thunk
  async def _require_context(ctx: Context) -> Context:
    """Ensure that the specified context keys are present."""
    ctx.require(*keys)
    return ctx
  return _require_context
