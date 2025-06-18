from antidote import inject
from goldentooth_agent.core.logging import get_logger
from goldentooth_agent.core.thunk import Thunk, thunk
import inspect
from logging import Logger
from typing import Annotated, Any, Callable, get_args, get_origin
from .key import ContextKey
from .main import Context

def clear_context_keys(keys: list[ContextKey[Any]]) -> Callable[[Thunk[Context, Context]], Thunk[Context, Context]]:
  """Decorator to clear specified keys from the context after executing a thunk."""
  def _clear_context_keys(th: Thunk[Context, Context]) -> Thunk[Context, Context]:
    """Decorator to clear specified keys from the context after executing a thunk."""
    @thunk
    async def _wrapped(ctx: Context) -> Context:
      """Execute the thunk and clear specified keys from the context."""
      ctx = await th(ctx)
      for key in keys:
        ctx.forget(key)
      return ctx
    return _wrapped
  return _clear_context_keys

def clear_context_key(key: ContextKey[Any]) -> Callable[[Thunk[Context, Context]], Thunk[Context, Context]]:
  """Decorator to clear a specific key from the context after executing a thunk."""
  def _clear_context_key(th: Thunk[Context, Context]) -> Thunk[Context, Context]:
    """Decorator to clear a specific key from the context after executing a thunk."""
    @thunk
    async def _wrapped(ctx: Context) -> Context:
      """Execute the thunk and clear the specified key from the context."""
      ctx = await th(ctx)
      ctx.forget(key)
      return ctx
    return _wrapped
  return _clear_context_key

def inject_context() -> Thunk[Context, Context]:
  """Thunk to inject the current context into the thunk execution."""
  @thunk
  @inject
  async def _inject_context(ctx: Context = inject.me()) -> Context:
    """Inject the current context into the thunk execution."""
    return ctx
  return _inject_context

def context_autothunk(fn: Callable[..., Any]) -> Thunk[Context, Context]:
  """Automatically create a thunk from a function by extracting context keys from its parameters and return type."""
  # Handle annotations stringified by `from __future__ import annotations`
  if isinstance(fn.__annotations__, dict):
    fn.__annotations__ = {
      k: eval(v, fn.__globals__) if isinstance(v, str) else v
      for k, v in fn.__annotations__.items()
    }

  class FullContextSentinel: pass
  FULL_CONTEXT = FullContextSentinel()

  sig = inspect.signature(fn)
  param_keys: list[ContextKey[Any] | FullContextSentinel] = []
  param_names: list[str] = []

  for name, param in sig.parameters.items():
    annotation = param.annotation
    if annotation is Context:
      param_keys.append(FULL_CONTEXT)
      param_names.append(name)
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

  @inject
  async def _wrapped(ctx: Context, logger: Logger = inject[get_logger(__name__)],) -> Context:
    """Execute the thunk with the context, retrieving parameters and setting return value."""

    def get_value(k: ContextKey[Any] | FullContextSentinel) -> Any:
      """Get the value from the context or return FULL_CONTEXT sentinel."""
      if isinstance(k, FullContextSentinel):
        return ctx
      else:
        return ctx.get(k)

    values = [ get_value(k) for k in param_keys ]
    logger.debug(f"Context keys before executing {fn.__name__}: {ctx.data}")
    logger.debug(f"Values to pass to {fn.__name__}: {values}")
    result = await fn(*values)
    if return_key:
      if result is None:
        ctx.forget(return_key)
      else:
        ctx.set(return_key, result)
    logger.debug(f"Context keys after executing {fn.__name__}: {ctx.data}")
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

def has_context_key(key: ContextKey) -> Callable[[Context], bool]:
  """Check if the context has a key set."""
  def _has_context_key(ctx: Context) -> bool:
    """Check if the context has a key set."""
    return ctx.has(key)
  return _has_context_key
