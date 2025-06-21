from __future__ import annotations
from antidote import inject, injectable
from atomic_agents.lib.components.system_prompt_generator import SystemPromptGenerator
from goldentooth_agent.core.context_provider import ContextProviderRegistry
from goldentooth_agent.core.logging import get_logger
from goldentooth_agent.core.path import UserPaths
from goldentooth_agent.core.system_prompt.registry import SystemPromptRegistry
from logging import Logger
from pathlib import Path
from rich.table import Table
from rich.syntax import Syntax
from typing import List
import yaml

@injectable(factory_method='create')
class StaticSystemPromptStore:
  """A simple filesystem store for managing system prompts as YAML files."""

  @inject
  def __init__(self, directory: Path, logger: Logger = inject[get_logger(__name__)]):
    """Initialize the store with a directory path."""
    logger.debug(f"Initializing StaticSystemPromptStore at {directory}")
    self.directory = directory
    self.directory.mkdir(parents=True, exist_ok=True)

  @classmethod
  def create(cls, paths: UserPaths = inject.me()) -> StaticSystemPromptStore:
    """Create a new StaticSystemPromptStore instance."""
    result = cls(paths.data() / 'system_prompts')
    result.discover()
    return result

  @inject.method
  def discover(
    self,
    registry: SystemPromptRegistry = inject.me(),
    logger: Logger = inject[get_logger(__name__)],
  ) -> None:
    """Discover all YAML files in the store directory and load them."""
    logger.debug(f"Discovering system prompts in {self.directory}")
    for path in self.directory.glob("*.yaml"):
      if path.is_file():
        name = path.stem
        try:
          logger.debug(f"Loading system prompt from {path}")
          data = yaml.safe_load(path.read_text())
          self.save(name, data)
          try:
            logger.debug(f"Creating SystemPromptGenerator for {name}")
            spg = self._build(data)
            registry.register(name, spg)
          except Exception as e:
            logger.error(f"Error creating SystemPromptGenerator from {path}: {e}")
        except yaml.YAMLError as e:
          logger.error(f"Error loading {path}: {e}")

  @inject.method
  def list(self, logger: Logger = inject[get_logger(__name__)]) -> List[str]:
    """List all available prompt names in the store."""
    logger.debug(f"Listing all system prompts in {self.directory}")
    return sorted(p.stem for p in self.directory.glob("*.yaml"))

  @inject.method
  def load(self, name: str, logger: Logger = inject[get_logger(__name__)]) -> dict:
    """Load prompt data from a YAML file by name."""
    logger.debug(f"Loading system prompt '{name}' from {self.directory}")
    path = self.directory / f"{name}.yaml"
    return yaml.safe_load(path.read_text())

  @inject.method
  def save(self, name: str, data: dict, logger: Logger = inject[get_logger(__name__)]) -> None:
    """Save prompt data to a YAML file."""
    logger.debug(f"Saving system prompt '{name}' with data: {data}")
    path = self.directory / f"{name}.yaml"
    with path.open("w") as f:
      yaml.safe_dump(data, f)

  @inject.method
  def delete(self, name: str, logger: Logger = inject[get_logger(__name__)]) -> bool:
    """Delete a prompt file by name."""
    logger.debug(f"Deleting system prompt '{name}'")
    path = self.directory / f"{name}.yaml"
    if path.exists():
      path.unlink()
      return True
    return False

  @inject.method
  def has(self, name: str, logger: Logger = inject[get_logger(__name__)]) -> bool:
    """Check if a prompt file exists by name."""
    logger.debug(f"Checking if system prompt '{name}' exists")
    return (self.directory / f"{name}.yaml").exists()

  @inject.method
  def dump(self, logger: Logger = inject[get_logger(__name__)]) -> Table:
    """Dump all prompts in the store to a table."""
    logger.debug("Dumping all system prompts to table")
    table = Table(title="Static System Prompts")
    table.add_column("Name", justify="left", style="cyan")
    table.add_column("Contents", justify="left", style="magenta")
    for name in self.list():
      contents = Syntax.from_path(str(self.directory / f"{name}.yaml"))
      table.add_row(name, contents)
    return table

  @inject.method
  def _build(
    self,
    data: dict,
    context_provider_registry: ContextProviderRegistry = inject.me(),
    logger: Logger = inject[get_logger(__name__)],
  ) -> SystemPromptGenerator:
    """Construct a SystemPromptGenerator from YAML data."""
    logger.debug(f"Building SystemPromptGenerator from data: {data}")
    background = data.get("background", [])
    steps = data.get("steps", [])
    output_instructions = data.get("output_instructions", [])
    return SystemPromptGenerator(
      background=background,
      steps=steps,
      output_instructions=output_instructions,
    )

@inject
def discover_static_system_prompts(
  store: StaticSystemPromptStore = inject.me(),
  logger: Logger = inject[get_logger(__name__)],
) -> None:
  """Install static system prompts from the embedded directory to the user data directory."""
  logger.debug("Discovering static system prompts...")

discover_static_system_prompts()
