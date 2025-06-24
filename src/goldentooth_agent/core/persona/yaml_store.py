from __future__ import annotations
from antidote import inject, injectable
from goldentooth_agent.core.logging import get_logger
from goldentooth_agent.core.path import UserPaths
from goldentooth_agent.core.yaml_store import YamlStore, YamlStoreAdapter, YamlStoreInstaller
from goldentooth_agent.data import roles as roles_source
from logging import Logger
from pathlib import Path
from rich.syntax import Syntax
from rich.table import Table
from .base import Persona
from .registry import PersonaRegistry

class YamlPersonaAdapter(YamlStoreAdapter[Persona]):
  """Adapter for Persona to handle YAML serialization and deserialization."""

  @classmethod
  def from_dict(cls, data: dict) -> Persona:
    """Create a Persona instance from a dictionary."""
    return Persona(
      name=data.get("name", ""),
      context_provider_ids=data.get("context_providers", []),
      tool_ids=data.get("tools", []),
    )

  @classmethod
  def to_dict(cls, obj: Persona) -> dict:
    """Convert a Persona instance to a dictionary."""
    return {
      "name": obj.name,
      "context_providers": obj.context_provider_ids,
      "tools": obj.tool_ids,
    }

@injectable(factory_method='create')
class YamlPersonaStore(YamlStore[Persona]):
  """A store for personas that uses YAML files for serialization."""

  def __init__(self, path: Path):
    """Initialize the YAML store with a given path."""
    super().__init__(path, YamlPersonaAdapter)

  @classmethod
  def create(cls, paths: UserPaths = inject.me()) -> YamlPersonaStore:
    """Create a new instance of the YAML persona store."""
    directory = paths.data() / 'personas'
    store = cls(directory)
    store.discover()
    return store

  @inject.method
  def discover(
    self,
    registry: PersonaRegistry = inject.me(),
    logger: Logger = inject[get_logger(__name__)],
  ) -> None:
    """Discover all YAML files in the store directory and load them."""
    logger.debug(f"Discovering personas in {self.directory}")
    for name in self.list():
      logger.debug(f"Loading persona '{name}'")
      persona = self.load(name)
      registry.set(name, persona)

  @inject.method
  def dump(self, logger: Logger = inject[get_logger(__name__)]) -> Table:
    """Dump all personas in the store to a table."""
    logger.debug("Dumping all personas to table")
    table = Table(title="Store Personas")
    table.add_column("Name", justify="left", style="cyan")
    table.add_column("Contents", justify="left", style="magenta")
    for name in self.list():
      contents = Syntax.from_path(str(self.directory / f"{name}.yaml"))
      table.add_row(name, contents)
    return table

@inject
def discover_yaml_personas(
  store: YamlPersonaStore = inject.me(),
  logger: Logger = inject[get_logger(__name__)],
) -> None:
  """Install YAML personas from the embedded directory to the user data directory."""
  logger.debug("Discovering YAML personas...")
  store.discover()

discover_yaml_personas()

@injectable
class YamlPersonaInstaller(YamlStoreInstaller[Persona]):
  """Installer for personas that copies embedded YAML files to the user data directory."""

  def __init__(self, destination: YamlPersonaStore = inject.me()):
    """Initialize the installer with the store."""
    source = YamlPersonaStore(Path(roles_source.__path__[0]))
    super().__init__(source, destination, YamlPersonaAdapter)

@inject
def install_yaml_personas(
  store: YamlPersonaStore = inject.me(),
  installer: YamlPersonaInstaller = inject.me(),
  logger: Logger = inject[get_logger(__name__)],
) -> None:
  """Install YAML personas from the embedded directory to the user data directory."""
  logger.debug("Installing YAML personas...")
  if installer.install(True):
    logger.debug("YAML personas installed successfully.")
    store.discover()

install_yaml_personas()
