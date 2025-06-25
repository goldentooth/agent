from __future__ import annotations
from antidote import inject, injectable
from goldentooth_agent.core.logging import get_logger
from goldentooth_agent.core.path import UserPaths
from goldentooth_agent.core.yaml_store import YamlStore, YamlStoreAdapter, YamlStoreInstaller
from goldentooth_agent.data import players as players_source
from logging import Logger
from pathlib import Path
from rich.syntax import Syntax
from rich.table import Table
from .base import Player
from .registry import PlayerRegistry

class YamlPlayerAdapter(YamlStoreAdapter[Player]):
  """Adapter for Player to handle YAML serialization and deserialization."""

  @classmethod
  def from_dict(cls, data: dict) -> Player:
    """Create a Player instance from a dictionary."""
    return Player(
      role_id=data.get("role", ""),
      persona_id=data.get("persona", ""),
    )

  @classmethod
  def to_dict(cls, obj: Player) -> dict:
    """Convert a Player instance to a dictionary."""
    return {
      "role": obj.role_id,
      "persona": obj.persona_id,
    }

@injectable(factory_method='create')
class YamlPlayerStore(YamlStore[Player]):
  """A store for players that uses YAML files for serialization."""

  def __init__(self, path: Path):
    """Initialize the YAML store with a given path."""
    super().__init__(path, YamlPlayerAdapter)

  @classmethod
  def create(cls, paths: UserPaths = inject.me()) -> YamlPlayerStore:
    """Create a new instance of the YAML player store."""
    directory = paths.data() / 'players'
    store = cls(directory)
    store.discover()
    return store

  @inject.method
  def discover(
    self,
    registry: PlayerRegistry = inject.me(),
    logger: Logger = inject[get_logger(__name__)],
  ) -> None:
    """Discover all YAML files in the store directory and load them."""
    logger.debug(f"Discovering players in {self.directory}")
    for name in self.list():
      logger.debug(f"Loading player '{name}'")
      player = self.load(name)
      registry.set(name, player)

  @inject.method
  def dump(self, logger: Logger = inject[get_logger(__name__)]) -> Table:
    """Dump all players in the store to a table."""
    logger.debug("Dumping all players to table")
    table = Table(title="Players Store")
    table.add_column("Name", justify="left", style="cyan")
    table.add_column("Contents", justify="left", style="magenta")
    for name in self.list():
      contents = Syntax.from_path(str(self.directory / f"{name}.yaml"))
      table.add_row(name, contents)
    return table

@inject
def discover_yaml_players(
  store: YamlPlayerStore = inject.me(),
  logger: Logger = inject[get_logger(__name__)],
) -> None:
  """Install YAML players from the embedded directory to the user data directory."""
  logger.debug("Discovering YAML players...")
  store.discover()

discover_yaml_players()

@injectable
class YamlPlayerInstaller(YamlStoreInstaller[Player]):
  """Installer for players that copies embedded YAML files to the user data directory."""

  def __init__(self, destination: YamlPlayerStore = inject.me()):
    """Initialize the installer with the store."""
    source = YamlPlayerStore(Path(players_source.__path__[0]))
    super().__init__(source, destination, YamlPlayerAdapter)

@inject
def install_yaml_players(
  store: YamlPlayerStore = inject.me(),
  installer: YamlPlayerInstaller = inject.me(),
  logger: Logger = inject[get_logger(__name__)],
) -> None:
  """Install YAML players from the embedded directory to the user data directory."""
  logger.debug("Installing YAML players...")
  if installer.install(True):
    logger.debug("YAML players installed successfully.")
    store.discover()

install_yaml_players()
