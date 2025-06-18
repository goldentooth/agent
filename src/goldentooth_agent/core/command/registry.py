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

def enroll_command(fn: Callable[[], None]) -> Callable[[], None]:
  """Decorator to enroll a command in the command registry."""
  @inject
  def _enroll(registry: CommandRegistry = inject.me()) -> None:
    """Enroll the command in the registry."""
    registry.enroll(fn)
  return _enroll
