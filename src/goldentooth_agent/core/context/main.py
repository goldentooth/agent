from __future__ import annotations
from antidote import inject, injectable
from rich.table import Table
from typing import Any, Callable, Dict, TypeVar
from .key import ContextKey, context_key

T = TypeVar('T')

@injectable(lifetime='transient')
class Context:
  """A simple context that stores key-value pairs."""

  def __init__(self, **initial):
    """Initialize the context with optional initial key-value pairs."""
    self.data: Dict[str, Any] = dict(initial)

  def get(self, key: ContextKey[T]) -> T:
    val = self.data.get(key.name)
    if val is None:
      raise KeyError(f"{key.name} not found in context")
    if not isinstance(val, key.type_T):
      raise TypeError(f"{key.name} wrong type; expected {key.type_T.__name__}, got {type(val).__name__}")
    return val

  def set(self, key: ContextKey[T], value: T) -> None:
    """Set a value in the context by key."""
    if not isinstance(value, key.type_T):
      raise TypeError(f"Value for {key.name} must be of type {key.type_T.__name__}, got {type(value).__name__}")
    self.data[key.name] = value

  def pop(self, key: ContextKey[T]) -> T:
    """Remove a key from the context and return its value."""
    if key.name not in self.data:
      raise KeyError(f"{key.name} not found in context")
    val = self.data.pop(key.name)
    if not isinstance(val, key.type_T):
      raise TypeError(f"{key.name} wrong type; expected {key.type_T.__name__}, got {type(val).__name__}")
    return val

  def has(self, key: ContextKey[T]) -> bool:
    """Check if a key exists in the context."""
    if key.name not in self.data:
      return False
    val = self.data[key.name]
    return isinstance(val, key.type_T)

  def clear(self) -> None:
    """Clear all key-value pairs from the context."""
    self.data.clear()

  def forget(self, key: ContextKey[T]) -> None:
    """Remove a key from the context without returning its value."""
    if key.name in self.data:
      del self.data[key.name]

  def require(self, *keys: ContextKey[Any]) -> None:
    """Ensure that all specified keys are present in the context."""
    for key in keys:
      if not self.has(key):
        raise KeyError(f"Missing required key: {key}")

  def get_or_default(self, key: ContextKey[T], fallback: Callable[[], T]) -> T:
    """Get a value from the context, or set it using a fallback function if not present."""
    if self.has(key):
      return self.get(key)
    return fallback()

  @inject
  def dump(self) -> Table:
    """Dump the context to the console."""
    table = Table(title=f"Context Dump")
    table.add_column("Key")
    table.add_column("Value", overflow="fold")
    for k in self.data:
      table.add_row(str(k), repr(self.data[k]))
    return table

if __name__ == "__main__":
  # Example usage
  from .key import context_key
  ctx = Context()
  key = context_key("example_key", int)
  ctx.set(key, 42)
  print(ctx.get(key))  # Output: 42
  ctx.forget(key)
  print(ctx.has(key))  # Output: False
  try:
    ctx.get(key)  # Should raise KeyError
  except KeyError as e:
    print(e)  # Output: example_key not found in context
  ctx.set(key, 100)
  print(ctx.get(key))  # Output: 100
  ctx.clear()
  print(ctx.has(key))  # Output: True
