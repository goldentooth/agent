from __future__ import annotations
from antidote import inject, injectable
from pathlib import Path
from typing import List
import yaml
from goldentooth_agent.core.path import UserPaths

@injectable(factory_method='create')
class StaticContextProviderStore:
  """A simple filesystem store for managing static context providers as YAML files."""

  def __init__(self, directory: Path):
    self.directory = directory
    self.directory.mkdir(parents=True, exist_ok=True)

  @classmethod
  def create(cls, paths: UserPaths = inject[UserPaths]) -> StaticContextProviderStore:
    """Create a new StaticContextProviderStore instance."""
    result = cls(paths.data / 'context_providers')
    return result

  def list(self) -> List[str]:
    """List all available context provider names in the store."""
    return sorted(p.stem for p in self.directory.glob("*.yaml"))

  def load(self, name: str) -> dict:
    """Load context provider data from a YAML file by name."""
    path = self.directory / f"{name}.yaml"
    return yaml.safe_load(path.read_text())

  def save(self, name: str, data: dict):
    """Save context provider data to a YAML file."""
    path = self.directory / f"{name}.yaml"
    with path.open("w") as f:
      yaml.safe_dump(data, f)

  def delete(self, name: str) -> bool:
    """Delete a context provider file by name."""
    path = self.directory / f"{name}.yaml"
    if path.exists():
      path.unlink()
      return True
    return False

  def exists(self, name: str) -> bool:
    """Check if a context provider file exists by name."""
    return (self.directory / f"{name}.yaml").exists()
