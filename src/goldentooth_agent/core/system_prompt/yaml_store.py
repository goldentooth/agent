from __future__ import annotations
from atomic_agents.lib.components.system_prompt_generator import SystemPromptGenerator
from goldentooth_agent.core.yaml_store import YamlStoreAdapter

class YamlSystemPromptAdapter(YamlStoreAdapter[SystemPromptGenerator]):
  """Adapter for SystemPromptGenerator to handle YAML serialization and deserialization."""

  @classmethod
  def from_dict(cls, data: dict) -> SystemPromptGenerator:
    """Create a SystemPromptGenerator instance from a dictionary."""
    return SystemPromptGenerator(
      background=data.get("background", []),
      steps=data.get("steps", []),
      output_instructions=data.get("output_instructions", []),
    )

  @classmethod
  def to_dict(cls, obj: SystemPromptGenerator) -> dict:
    """Convert a SystemPromptGenerator instance to a dictionary."""
    return {
      "background": obj.background,
      "steps": obj.steps,
      "output_instructions": obj.output_instructions,
    }

from antidote import inject, injectable
from goldentooth_agent.core.yaml_store import YamlStore
from goldentooth_agent.core.logging import get_logger
from goldentooth_agent.core.path import UserPaths
from logging import Logger
from pathlib import Path
from rich.syntax import Syntax
from rich.table import Table
from .registry import SystemPromptRegistry

@injectable(factory_method='create')
class YamlSystemPromptStore(YamlStore[SystemPromptGenerator]):
  """A store for system prompts that uses YAML files for serialization."""

  def __init__(self, path: Path):
    """Initialize the YAML store with a given path."""
    super().__init__(path, YamlSystemPromptAdapter)

  @classmethod
  def create(cls, paths: UserPaths = inject.me()) -> YamlSystemPromptStore:
    """Create a new instance of the YAML system prompt store."""
    directory = paths.data() / 'system_prompts'
    store = cls(directory)
    store.discover()
    return store

  @inject.method
  def discover(
    self,
    registry: SystemPromptRegistry = inject.me(),
    logger: Logger = inject[get_logger(__name__)],
  ) -> None:
    """Discover all YAML files in the store directory and load them."""
    logger.debug(f"Discovering system prompts in {self.directory}")
    for name in self.list():
      logger.debug(f"Loading system prompt '{name}'")
      spg = self.load(name)
      registry.set(name, spg)

  @inject.method
  def dump(self, logger: Logger = inject[get_logger(__name__)]) -> Table:
    """Dump all prompts in the store to a table."""
    logger.debug("Dumping all system prompts to table")
    table = Table(title="Store System Prompts")
    table.add_column("Name", justify="left", style="cyan")
    table.add_column("Contents", justify="left", style="magenta")
    for name in self.list():
      contents = Syntax.from_path(str(self.directory / f"{name}.yaml"))
      table.add_row(name, contents)
    return table

@inject
def discover_yaml_system_prompts(
  store: YamlSystemPromptStore = inject.me(),
  logger: Logger = inject[get_logger(__name__)],
) -> None:
  """Install YAML system prompts from the embedded directory to the user data directory."""
  logger.debug("Discovering YAML system prompts...")
  store.discover()

discover_yaml_system_prompts()

from goldentooth_agent.data import system_prompts as system_prompts_source
from goldentooth_agent.core.yaml_store import YamlStoreInstaller

@injectable
class YamlSystemPromptInstaller(YamlStoreInstaller[SystemPromptGenerator]):
  """Installer for system prompts that copies embedded YAML files to the user data directory."""

  def __init__(self, destination: YamlSystemPromptStore = inject.me()):
    """Initialize the installer with the store."""
    source = YamlSystemPromptStore(Path(system_prompts_source.__path__[0]))
    super().__init__(source, destination, YamlSystemPromptAdapter)

@inject
def install_yaml_system_prompts(
  store: YamlSystemPromptStore = inject.me(),
  installer: YamlSystemPromptInstaller = inject.me(),
  logger: Logger = inject[get_logger(__name__)],
) -> None:
  """Install YAML system prompts from the embedded directory to the user data directory."""
  logger.debug("Installing YAML system prompts...")
  if installer.install(True):
    logger.debug("YAML system prompts installed successfully.")
    store.discover()

install_yaml_system_prompts()
