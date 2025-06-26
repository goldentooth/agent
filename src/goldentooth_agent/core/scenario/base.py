from __future__ import annotations
from antidote import inject
from goldentooth_agent.core.logging import get_logger


class Scenario:
    """Base class for all scenarios in the GoldenTooth Agent system."""

    @inject
    def __init__(
        self,
        id: str,
        name: str,
        hidden: bool,
        info: list[str],
        role_ids: list[str],
        logger=inject[get_logger(__name__)],
    ) -> None:
        """Initialize the scenario with context providers."""
        logger.debug(f"Initializing Scenario: {id}")
        self.id = id
        self.name = name
        self.hidden = hidden
        self.info = info
        self.role_ids = role_ids
