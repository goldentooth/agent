from __future__ import annotations
from antidote import inject, injectable
from pathlib import Path
import yaml
from goldentooth_agent.data import context_providers
from .store import StaticContextProviderStore

@injectable(factory_method='create')
class StaticContextProviderInstaller:
  """Copies default embedded context providers to the user data directory if missing."""

  def __init__(
    self,
    embedded_dir: Path = Path(context_providers.__path__[0]),
    store: StaticContextProviderStore = inject.me(),
  ) -> None:
    """Initialize the installer with a store and the directory containing embedded context providers."""
    self.embedded_dir = embedded_dir
    self.store = store

  @classmethod
  def create(cls) -> StaticContextProviderInstaller:
    """Create a new StaticContextProviderInstaller instance."""
    return cls()

  def install(self):
    """Copy embedded context providers to the user store, skipping ones that already exist."""
    for path in self.embedded_dir.glob("*.yaml"):
      name = path.stem
      if self.exists(name):
        continue
      data = self.load(path)
      self.save(name, data)

  def load(self, path: Path) -> dict:
    """Load context provider data from a YAML file by name."""
    return yaml.safe_load(path.read_text())

  def save(self, name: str, data: dict):
    """Save prompt data to a YAML file."""
    return self.store.save(name, data)

  def delete(self, name: str) -> bool:
    """Delete a prompt file by name."""
    return self.store.delete(name)

  def exists(self, name: str) -> bool:
    """Check if a prompt file exists by name."""
    return self.store.exists(name)

context_provider_installer = StaticContextProviderInstaller.create()
context_provider_installer.install()
