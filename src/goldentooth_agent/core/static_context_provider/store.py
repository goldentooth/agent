from __future__ import annotations
from antidote import inject, injectable
from goldentooth_agent.core.context_provider import ContextProviderRegistry
from goldentooth_agent.core.dynamic_context_provider import DynamicContextProvider
from goldentooth_agent.core.logging import get_logger
from goldentooth_agent.core.path import UserPaths
from logging import Logger
from pathlib import Path
from rich.table import Table
from rich.syntax import Syntax
from typing import List
import yaml

@injectable(factory_method='create')
class StaticContextProviderStore:
  """A simple filesystem store for managing static context providers as YAML files."""

  def __init__(
    self,
    directory: Path,
    logger: Logger = inject[get_logger(__name__)],
  ) -> None:
    """Initialize the store with a directory path."""
    logger.debug(f"Initializing StaticContextProviderStore at {directory}")
    self.directory = directory
    self.directory.mkdir(parents=True, exist_ok=True)

  @classmethod
  def create(
    cls,
    paths: UserPaths = inject[UserPaths]
  ) -> StaticContextProviderStore:
    """Create a new StaticContextProviderStore instance."""
    result = cls(paths.data() / 'context_providers')
    result.discover()
    return result

  @inject.method
  def discover(
    self,
    registry: ContextProviderRegistry = inject.me(),
    logger: Logger = inject[get_logger(__name__)],
  ) -> None:
    """Discover all YAML files in the store directory and load them."""
    logger.debug(f"Discovering context providers in {self.directory}")
    for path in self.directory.glob("*.yaml"):
      if path.is_file():
        name = path.stem
        try:
          logger.debug(f"Loading context provider '{name}' from {path}")
          data = yaml.safe_load(path.read_text())
          self.save(name, data)
          try:
            spg = self._build(data)
            logger.debug(f"Registering SystemPromptGenerator '{name}' from {path}")
            registry.register(name, spg)
          except Exception as e:
            logger.error(f"Error creating SystemPromptGenerator from {path}: {e}")
        except yaml.YAMLError as e:
          logger.error(f"Error loading {path}: {e}")

  @inject.method
  def list(self, logger: Logger = inject[get_logger(__name__)]) -> List[str]:
    """List all available context provider names in the store."""
    logger.debug(f"Listing context providers in {self.directory}")
    return sorted(p.stem for p in self.directory.glob("*.yaml"))

  @inject.method
  def load(self, name: str, logger: Logger = inject[get_logger(__name__)]) -> dict:
    """Load context provider data from a YAML file by name."""
    logger.debug(f"Loading context provider '{name}' from {self.directory}")
    path = self.directory / f"{name}.yaml"
    return yaml.safe_load(path.read_text())

  @inject.method
  def save(self, name: str, data: dict, logger: Logger = inject[get_logger(__name__)]) -> None:
    """Save context provider data to a YAML file."""
    logger.debug(f"Saving context provider '{name}' with data: {data}")
    path = self.directory / f"{name}.yaml"
    with path.open("w") as f:
      yaml.safe_dump(data, f)

  @inject.method
  def delete(self, name: str, logger: Logger = inject[get_logger(__name__)]) -> bool:
    """Delete a context provider file by name."""
    logger.debug(f"Deleting context provider '{name}' from {self.directory}")
    path = self.directory / f"{name}.yaml"
    if path.exists():
      path.unlink()
      return True
    return False

  @inject.method
  def exists(self, name: str, logger: Logger = inject[get_logger(__name__)]) -> bool:
    """Check if a context provider file exists by name."""
    logger.debug(f"Checking if context provider '{name}' exists in {self.directory}")
    return (self.directory / f"{name}.yaml").exists()

  @inject.method
  def _build(self, data: dict, logger: Logger = inject[get_logger(__name__)]) -> DynamicContextProvider:
    """Build a DynamicContextProvider from the given data."""
    logger.debug(f"Building DynamicContextProvider from data: {data}")
    return DynamicContextProvider.from_dict(data)

  @inject.method
  def dump(self, logger: Logger = inject[get_logger(__name__)]) -> Table:
    """Dump the discovered context providers as a table."""
    logger.debug("Dumping context providers as a table")
    table = Table(title="Static Context Providers")
    table.add_column("Name", justify="left", style="cyan")
    table.add_column("Contents", justify="left", style="magenta")

    for name in self.list():
      path = self.directory / f"{name}.yaml"
      table.add_row(name, Syntax.from_path(str(path)))

    return table
