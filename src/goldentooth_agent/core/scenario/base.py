from __future__ import annotations
from antidote import inject
from goldentooth_agent.core.logging import get_logger
from logging import Logger

class Scenario:
  """Base class for all scenarios in the GoldenTooth Agent system."""

  @inject
  def __init__(self, name: str, hidden: bool, info: list[str], tags: list[str], logger: Logger = inject[get_logger(__name__)]) -> None:
    """Initialize the scenario with context providers."""
    logger.debug(f"Initializing Scenario: {name}")
    self.name = name
    self.hidden = hidden
    self.info = info
