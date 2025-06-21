from __future__ import annotations
from antidote import injectable, inject
from goldentooth_agent.core.logging import get_logger
from logging import Logger
from typing import Callable, List

@injectable(factory_method='create')
class CommandRegistry:
  """Registry for commands."""

  def __init__(self, logger: Logger = inject[get_logger(__name__)]) -> None:
    """Initialize the registry with an empty dictionary."""
    logger.debug("Initializing CommandRegistry")
    self.commands: List[Callable[[], None]] = []

  @classmethod
  def create(cls) -> CommandRegistry:
    """Create a new CommandRegistry instance."""
    result = cls()
    return result

  @inject.method
  def enroll(self, callable: Callable[[], None], logger: Logger = inject[get_logger(__name__)]) -> None:
    """Enroll a comand."""
    logger.debug(f"Enrolling command: {callable.__name__}")
    self.commands.append(callable)

  @inject.method
  def clear(self, logger: Logger = inject[get_logger(__name__)]):
    """Clear all registered command registrars."""
    logger.debug(f"Clearing {len(self.commands)} commands")
    self.commands.clear()

  @inject.method
  def register(self, logger: Logger = inject[get_logger(__name__)]):
    """Register all enrolled commands."""
    logger.debug(f"Registering {len(self.commands)} commands")
    for fn in self.commands:
      fn()

@inject
def enroll_command(fn: Callable[[], None], registry: CommandRegistry = inject.me(), logger: Logger = inject[get_logger(__name__)]) -> Callable[[], None]:
  """Decorator to enroll a command in the command registry."""
  logger.debug(f"Enrolling command: {fn.__name__}")
  registry.enroll(fn)
  return fn
