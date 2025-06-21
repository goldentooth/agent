from __future__ import annotations
from antidote import inject, injectable
from pathlib import Path
import yaml
from goldentooth_agent.data import system_prompts
from goldentooth_agent.core.logging import get_logger
from logging import Logger
from .store import StaticSystemPromptStore

@injectable(factory_method='create')
class StaticSystemPromptInstaller:
  """Copies default embedded system prompts to the user data directory if missing."""

  @inject
  def __init__(
    self,
    embedded_dir: Path = Path(system_prompts.__path__[0]),
    store: StaticSystemPromptStore = inject.me(),
    logger: Logger = inject[get_logger(__name__)],
  ) -> None:
    """Initialize the installer with a store and the directory containing embedded prompts."""
    logger.debug(f"Initializing StaticSystemPromptInstaller with embedded directory: {embedded_dir}")
    self.embedded_dir = embedded_dir
    self.store = store

  @classmethod
  def create(cls) -> StaticSystemPromptInstaller:
    """Create a new SystemPromptInstaller instance."""
    return cls()

  @inject.method
  def install(self, logger: Logger = inject[get_logger(__name__)]) -> None:
    """Copy embedded prompts to the user store, skipping ones that already exist."""
    logger.debug(f"Installing static system prompts from {self.embedded_dir}")
    changed = False
    for path in self.embedded_dir.glob("*.yaml"):
      logger.debug(f"Installing static system prompt: {path.name}")
      name = path.stem
      # if self.exists(name):
      #   continue
      data = self.load(path)
      self.save(name, data)
      changed = True
    if changed:
      logger.debug(f"Installed static system prompts from {self.embedded_dir}")
      self.store.discover()

  @inject.method
  def load(self, path: Path) -> dict:
    """Load prompt data from a YAML file by name."""
    return yaml.safe_load(path.read_text())

  @inject.method
  def save(self, name: str, data: dict):
    """Save prompt data to a YAML file."""
    return self.store.save(name, data)

  @inject.method
  def delete(self, name: str) -> bool:
    """Delete a prompt file by name."""
    return self.store.delete(name)

  @inject.method
  def has(self, name: str) -> bool:
    """Check if a prompt file exists by name."""
    return self.store.has(name)

@inject
def install_static_system_prompts(
  installer: StaticSystemPromptInstaller = inject.me(),
  logger: Logger = inject[get_logger(__name__)],
) -> None:
  """Install static system prompts from the embedded directory to the user data directory."""
  logger.debug("Installing static system prompts...")
  installer.install()

install_static_system_prompts()
