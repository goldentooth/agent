from __future__ import annotations
from antidote import inject, injectable
from pathlib import Path
from typing import List
import yaml
from goldentooth_agent.core.path import UserPaths

@injectable(factory_method='create')
class StaticSystemPromptStore:
  """A simple filesystem store for managing system prompts as YAML files."""

  def __init__(self, directory: Path):
    self.directory = directory
    self.directory.mkdir(parents=True, exist_ok=True)

  @classmethod
  def create(cls, paths: UserPaths = inject.me()) -> StaticSystemPromptStore:
    """Create a new StaticSystemPromptStore instance."""
    result = cls(paths.data() / 'system_prompts')
    return result

  def list(self) -> List[str]:
    """List all available prompt names in the store."""
    return sorted(p.stem for p in self.directory.glob("*.yaml"))

  def load(self, name: str) -> dict:
    """Load prompt data from a YAML file by name."""
    path = self.directory / f"{name}.yaml"
    return yaml.safe_load(path.read_text())

  def save(self, name: str, data: dict):
    """Save prompt data to a YAML file."""
    path = self.directory / f"{name}.yaml"
    with path.open("w") as f:
      yaml.safe_dump(data, f)

  def delete(self, name: str) -> bool:
    """Delete a prompt file by name."""
    path = self.directory / f"{name}.yaml"
    if path.exists():
      path.unlink()
      return True
    return False

  def exists(self, name: str) -> bool:
    """Check if a prompt file exists by name."""
    return (self.directory / f"{name}.yaml").exists()
