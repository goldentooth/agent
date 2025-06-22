from typing import TypeVar, Generic
from pathlib import Path
import yaml
from .adapter import YamlStoreAdapter

T = TypeVar("T") # Type being serialized/deserialized

class YamlStore(Generic[T]):
  """A generic base class for managing YAML files in a directory."""

  def __init__(self, directory: Path, adapter: type[YamlStoreAdapter[T]]):
    """Initialize the store with a directory path and the type of objects it will manage."""
    self.directory = directory
    self.directory.mkdir(parents=True, exist_ok=True)
    self.adapter = adapter

  def list(self) -> list[str]:
    """List all available object names in the store."""
    return [p.stem for p in self.directory.glob("*.yaml")]

  def load(self, name: str) -> T:
    """Load an object by its name from the YAML store."""
    path = self.directory / f"{name}.yaml"
    data = yaml.safe_load(path.read_text())
    return self.adapter.from_dict(data)

  def save(self, name: str, obj: T) -> None:
    """Save an object to the YAML store with the given name."""
    path = self.directory / f"{name}.yaml"
    data = self.adapter.to_dict(obj)
    path.write_text(yaml.safe_dump(data))

  def delete(self, name: str) -> None:
    """Delete an object by its name from the YAML store."""
    path = self.directory / f"{name}.yaml"
    path.unlink(missing_ok=True)

  def exists(self, name: str) -> bool:
    """Check if an object exists in the YAML store by its name."""
    return (self.directory / f"{name}.yaml").exists()
