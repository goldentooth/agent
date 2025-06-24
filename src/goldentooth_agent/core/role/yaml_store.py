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
from .base import Role
from .registry import RoleRegistry

class YamlRoleAdapter(YamlStoreAdapter[Role]):
  """Adapter for Role to handle YAML serialization and deserialization."""

  @classmethod
  def from_dict(cls, data: dict) -> Role:
    """Create a Role instance from a dictionary."""
    return Role(
      name=data.get("name", ""),
      system_prompt_id=data.get("system_prompt", ""),
      context_provider_ids=data.get("context_providers", []),
      tool_ids=data.get("tools", []),
    )

  @classmethod
  def to_dict(cls, obj: Role) -> dict:
    """Convert a Role instance to a dictionary."""
    return {
      "name": obj.name,
      "system_prompt": obj.system_prompt_id,
      "context_providers": obj.context_provider_ids,
      "tools": obj.tool_ids,
    }

@injectable(factory_method='create')
class YamlRoleStore(YamlStore[Role]):
  """A store for roles that uses YAML files for serialization."""

  def __init__(self, path: Path):
    """Initialize the YAML store with a given path."""
    super().__init__(path, YamlRoleAdapter)

  @classmethod
  def create(cls, paths: UserPaths = inject.me()) -> YamlRoleStore:
    """Create a new instance of the YAML role store."""
    directory = paths.data() / 'roles'
    store = cls(directory)
    store.discover()
    return store

  @inject.method
  def discover(
    self,
    registry: RoleRegistry = inject.me(),
    logger: Logger = inject[get_logger(__name__)],
  ) -> None:
    """Discover all YAML files in the store directory and load them."""
    logger.debug(f"Discovering roles in {self.directory}")
    for name in self.list():
      logger.debug(f"Loading role '{name}'")
      role = self.load(name)
      registry.set(name, role)

  @inject.method
  def dump(self, logger: Logger = inject[get_logger(__name__)]) -> Table:
    """Dump all roles in the store to a table."""
    logger.debug("Dumping all roles to table")
    table = Table(title="Store Roles")
    table.add_column("Name", justify="left", style="cyan")
    table.add_column("Contents", justify="left", style="magenta")
    for name in self.list():
      contents = Syntax.from_path(str(self.directory / f"{name}.yaml"))
      table.add_row(name, contents)
    return table

@inject
def discover_yaml_roles(
  store: YamlRoleStore = inject.me(),
  logger: Logger = inject[get_logger(__name__)],
) -> None:
  """Install YAML roles from the embedded directory to the user data directory."""
  logger.debug("Discovering YAML roles...")
  store.discover()

discover_yaml_roles()

@injectable
class YamlRoleInstaller(YamlStoreInstaller[Role]):
  """Installer for roles that copies embedded YAML files to the user data directory."""

  def __init__(self, destination: YamlRoleStore = inject.me()) -> None:
    """Initialize the installer with the store."""
    source = YamlRoleStore(Path(roles_source.__path__[0]))
    super().__init__(source, destination, YamlRoleAdapter)

@inject
def install_yaml_roles(
  store: YamlRoleStore = inject.me(),
  installer: YamlRoleInstaller = inject.me(),
  logger: Logger = inject[get_logger(__name__)],
) -> None:
  """Install YAML roles from the embedded directory to the user data directory."""
  logger.debug("Installing YAML roles...")
  if installer.install(True):
    store.discover()
  logger.debug("YAML roles installed successfully.")

install_yaml_roles()
