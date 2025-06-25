from __future__ import annotations
from antidote import inject, injectable
from atomic_agents.agents.base_agent import BaseAgentConfig
from atomic_agents.lib.components.agent_memory import AgentMemory
from goldentooth_agent.core.logging import get_logger
from goldentooth_agent.core.path import UserPaths
from goldentooth_agent.core.yaml_store import YamlStore, YamlStoreAdapter, YamlStoreInstaller
from goldentooth_agent.data import agent_configs as agent_configs_source
from logging import Logger
from pathlib import Path
from rich.syntax import Syntax
from rich.table import Table
from .client import AgentConfigClient
from .model import AgentConfigModel
from .registry import AgentConfigRegistry

class YamlAgentConfigAdapter(YamlStoreAdapter[BaseAgentConfig]):
  """Adapter for AgentConfig to handle YAML serialization and deserialization."""

  @classmethod
  @inject
  def from_dict(cls, data: dict) -> BaseAgentConfig:
    """Create a BaseAgentConfig instance from a dictionary."""
    client = AgentConfigClient(data.get("client")).client
    model = AgentConfigModel(data.get("model")).value
    return BaseAgentConfig(
      client=client,
      memory=AgentMemory(),
      model=model,
      max_tokens=data.get("max_tokens", 4096),
      temperature=data.get("temperature", 1.0),
      model_api_parameters=data.get("model_api_parameters", {}),
    )

  @classmethod
  def to_dict(cls, obj: BaseAgentConfig) -> dict:
    """Convert a Player instance to a dictionary."""
    provider = obj.client.provider.value
    return {
      "client": provider,
      "memory": None,
      "model": obj.model,
      "max_tokens": obj.max_tokens,
      "temperature": obj.temperature,
      "model_api_parameters": obj.model_api_parameters,
    }

@injectable(factory_method='create')
class YamlAgentConfigStore(YamlStore[BaseAgentConfig]):
  """A store for agent configurations that uses YAML files for serialization."""

  def __init__(self, path: Path):
    """Initialize the YAML store with a given path."""
    super().__init__(path, YamlAgentConfigAdapter)

  @classmethod
  def create(cls, paths: UserPaths = inject.me()) -> YamlAgentConfigStore:
    """Create a new instance of the YAML agent config store."""
    directory = paths.data() / 'agent_configs'
    store = cls(directory)
    store.discover()
    return store

  @inject.method
  def discover(
    self,
    registry: AgentConfigRegistry = inject.me(),
    logger: Logger = inject[get_logger(__name__)],
  ) -> None:
    """Discover all YAML files in the store directory and load them."""
    logger.debug(f"Discovering agent configs in {self.directory}")
    for name in self.list():
      logger.debug(f"Loading agent config '{name}'")
      agent = self.load(name)
      registry.set(name, agent)

  @inject.method
  def dump(self, logger: Logger = inject[get_logger(__name__)]) -> Table:
    """Dump all agent configs in the store to a table."""
    logger.debug("Dumping all agent configs to table")
    table = Table(title="Agent Config Store")
    table.add_column("Name", justify="left", style="cyan")
    table.add_column("Contents", justify="left", style="magenta")
    for name in self.list():
      contents = Syntax.from_path(str(self.directory / f"{name}.yaml"))
      table.add_row(name, contents)
    return table

@inject
def discover_yaml_agent_configs(
  store: YamlAgentConfigStore = inject.me(),
  logger: Logger = inject[get_logger(__name__)],
) -> None:
  """Install YAML agent configs from the embedded directory to the user data directory."""
  logger.debug("Discovering YAML agent configs...")
  store.discover()

discover_yaml_agent_configs()

@injectable
class YamlAgentConfigInstaller(YamlStoreInstaller[BaseAgentConfig]):
  """Installer for agent configs that copies embedded YAML files to the user data directory."""

  def __init__(self, destination: YamlAgentConfigStore = inject.me()):
    """Initialize the installer with the store."""
    source = YamlAgentConfigStore(Path(agent_configs_source.__path__[0]))
    super().__init__(source, destination, YamlAgentConfigAdapter)

@inject
def install_yaml_agent_configs(
  store: YamlAgentConfigStore = inject.me(),
  installer: YamlAgentConfigInstaller = inject.me(),
  logger: Logger = inject[get_logger(__name__)],
) -> None:
  """Install YAML agent configs from the embedded directory to the user data directory."""
  logger.debug("Installing YAML agent configs...")
  if installer.install(True):
    logger.debug("YAML agent configs installed successfully.")
    store.discover()

install_yaml_agent_configs()
