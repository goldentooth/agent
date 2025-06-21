from __future__ import annotations
from antidote import inject, injectable
from goldentooth_agent.data import context_providers
from goldentooth_agent.core.logging import get_logger
from logging import Logger
from pathlib import Path
import yaml
from .store import StaticContextProviderStore

@injectable(factory_method='create')
class StaticContextProviderInstaller:
  """Copies default embedded context providers to the user data directory if missing."""

  @inject
  def __init__(
    self,
    embedded_dir: Path = Path(context_providers.__path__[0]),
    store: StaticContextProviderStore = inject.me(),
    logger: Logger = inject[get_logger(__name__)],
  ) -> None:
    """Initialize the installer with a store and the directory containing embedded context providers."""
    logger.debug(f"Initializing StaticContextProviderInstaller with embedded directory: {embedded_dir}")
    self.embedded_dir = embedded_dir
    self.store = store

  @classmethod
  def create(cls) -> StaticContextProviderInstaller:
    """Create a new StaticContextProviderInstaller instance."""
    result = cls()
    result.install()
    return result

  @inject.method
  def install(self, logger: Logger = inject[get_logger(__name__)]) -> None:
    """Copy embedded context providers to the user store, skipping ones that already exist."""
    changed = False
    logger.debug(f"Installing static context providers from {self.embedded_dir}")
    for path in self.embedded_dir.glob("*.yaml"):
      logger.debug(f"Installing static context provider: {path.name}")
      name = path.stem
      # if self.exists(name):
      #   continue
      data = self.load(path)
      self.save(name, data)
      changed = True
    if changed:
      logger.debug(f"Installed static context providers from {self.embedded_dir}")
      self.store.discover()

  @inject.method
  def load(self, path: Path, logger: Logger = inject[get_logger(__name__)]) -> dict:
    """Load context provider data from a YAML file by name."""
    logger.debug(f"Loading context provider data from {path}")
    return yaml.safe_load(path.read_text())

  @inject.method
  def save(self, name: str, data: dict, logger: Logger = inject[get_logger(__name__)]) -> None:
    """Save prompt data to a YAML file."""
    logger.debug(f"Saving context provider '{name}' with data: {data}")
    return self.store.save(name, data)

  @inject.method
  def delete(self, name: str, logger: Logger = inject[get_logger(__name__)]) -> bool:
    """Delete a prompt file by name."""
    logger.debug(f"Deleting context provider '{name}'")
    return self.store.delete(name)

  @inject.method
  def exists(self, name: str, logger: Logger = inject[get_logger(__name__)]) -> bool:
    """Check if a prompt file exists by name."""
    logger.debug(f"Checking if context provider '{name}' exists")
    return self.store.exists(name)

context_provider_installer = StaticContextProviderInstaller.create()
context_provider_installer.install()
