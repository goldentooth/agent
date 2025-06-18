from __future__ import annotations
from antidote import injectable, inject
from typing import Callable, List

@injectable(factory_method='create')
class CommandRegistry:
  """Registry for commands."""

  def __init__(self):
    """Initialize the registry with an empty dictionary."""
    self.commands: List[Callable[[], None]] = []

  @classmethod
  def create(cls) -> CommandRegistry:
    """Create a new CommandRegistry instance."""
    result = cls()
    return result

  def enroll(self, callable: Callable[[], None]):
    """Enroll a comand."""
    self.commands.append(callable)

  def clear(self):
    """Clear all registered command registrars."""
    self.commands.clear()

  def register(self):
    """Register all enrolled commands."""
    for fn in self.commands:
      fn()

@inject
def enroll_command(fn: Callable[[], None], registry: CommandRegistry = inject.me()) -> Callable[[], None]:
  """Decorator to enroll a command in the command registry."""
  print(f"Enrolling command: {fn.__name__}")
  registry.enroll(fn)
  return fn
