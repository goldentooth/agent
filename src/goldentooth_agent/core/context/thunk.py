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
    @thunk(name=f"clear_context_keys({', '.join(k.name for k in keys)})")
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
    @thunk(name=f"clear_context_key({key.name})")
    async def _wrapped(ctx: Context) -> Context:
      """Execute the thunk and clear the specified key from the context."""
      ctx = await th(ctx)
      ctx.forget(key)
      return ctx
    return _wrapped
  return _clear_context_key

def inject_context() -> Thunk[Context, Context]:
  """Thunk to inject the current context into the thunk execution."""
  @thunk(name="inject_context")
  @inject
  async def _inject_context(ctx: Context = inject.me()) -> Context:
    """Inject the current context into the thunk execution."""
    return ctx
  return _inject_context

class ThunkSentinel:
  """Sentinel to represent the full context in function parameters."""
  def __init__(self, name: str) -> None:
    """Initialize the sentinel with a name."""
    self.name = name
  def __repr__(self) -> str:
    """Return a string representation of the sentinel."""
    return f"<ThunkSentinel name={self.name}>"

class FullContextSentinel(ThunkSentinel):
  """Sentinel to represent the full context in function parameters."""
  def __init__(self) -> None:
    """Initialize the sentinel with a default name."""
    super().__init__("FULL_CONTEXT")

def context_autothunk(*, name: str) -> Callable[[Callable[..., Any]], Thunk[Context, Context]]:
  """Decorator to automatically create a thunk from a function by extracting context keys from its parameters and return type."""
  fn_name = name
  def _decorator(fn: Callable[..., Any]) -> Thunk[Context, Context]:
    """Automatically create a thunk from a function by extracting context keys from its parameters and return type."""
    # Handle annotations stringified by `from __future__ import annotations`
    if isinstance(fn.__annotations__, dict):
      fn.__annotations__ = {
        k: eval(v, fn.__globals__) if isinstance(v, str) else v
        for k, v in fn.__annotations__.items()
      }

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

    thunk = Thunk(_wrapped, name=fn_name)
    thunk.metadata["context_keys"] = [k.name for k in param_keys]
    thunk.metadata["return_key"] = return_key.name if return_key else None
    return thunk
  return _decorator

def move_context(
  source: ContextKey[Any],
  destination: ContextKey[Any],
) -> Thunk[Context, Context]:
  """Thunk to move a context item from one key to another."""
  @thunk(name=f"move_context({source.name} -> {destination.name})")
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
  @thunk(name=f"copy_context({source.name} -> {destination.name})")
  async def _copy_context(ctx: Context) -> Context:
    """Copy the context item from one key to another."""
    value = ctx.get(source)
    ctx.set(destination, value)
    return ctx
  return _copy_context

def forget_context(key: ContextKey[Any]) -> Thunk[Context, Context]:
  """Thunk to forget a context key."""
  @thunk(name=f"forget_context({key.name})")
  async def _forget_context(ctx: Context) -> Context:
    """Forget the specified context key."""
    ctx.forget(key)
    return ctx
  return _forget_context

def require_context(*keys: ContextKey[Any]) -> Thunk[Context, Context]:
  """Thunk to require certain context keys."""
  @thunk(name=f"require_context({', '.join(k.name for k in keys)})")
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

def dump_context() -> Thunk[Context, Context]:
  """Print all current keys/values in the context."""
  from goldentooth_agent.core.console import get_console
  from rich.console import Console
  @inject
  @thunk(name="dump_context")
  def _dump(ctx: Context, console: Console = inject[get_console()]) -> Context:
    """Dump the context to the console."""
    table = ctx.dump()
    console.print(table)
    return ctx
  return _dump
