from __future__ import annotations
from antidote import inject, injectable
from atomic_agents.lib.components.system_prompt_generator import SystemPromptGenerator
from goldentooth_agent.core.logging import get_logger
from logging import Logger
from rich.pretty import Pretty
from rich.table import Table
from typing import Dict, List, Optional

DEFAULT_PROMPT_NAME = "default"

@injectable(factory_method='create')
class SystemPromptRegistry:
  """Manages system prompts stored as YAML files."""

  @inject
  def __init__(self, logger: Logger = inject[get_logger(__name__)]) -> None:
    """Initialize the registry."""
    logger.debug("Initializing SystemPromptRegistry")
    self.generators: Dict[str, SystemPromptGenerator] = {}

  @classmethod
  def create(cls) -> SystemPromptRegistry:
    """Create a new SystemPromptRegistry instance."""
    result = cls()
    return result

  @inject.method
  def register(
    self,
    name: str,
    generator: SystemPromptGenerator,
    logger: Logger = inject[get_logger(__name__)]
  ) -> None:
    """Register a prompt generator under a given name (in-memory only)."""
    logger.debug(f"Registering system prompt generator '{name}'")
    self.generators[name] = generator

  @inject.method
  def unregister(self, name: str, logger: Logger = inject[get_logger(__name__)]) -> None:
    """Unregister a prompt generator by name (in-memory only)."""
    logger.debug(f"Unregistering system prompt generator '{name}'")
    self.generators.pop(name, None)

  @inject.method
  def get(self, name: str, logger: Logger = inject[get_logger(__name__)]) -> Optional[SystemPromptGenerator]:
    """Retrieve a registered prompt generator by name."""
    logger.debug(f"Retrieving system prompt generator '{name}'")
    return self.generators.get(name)

  @inject.method
  def get_default(self, logger: Logger = inject[get_logger(__name__)]) -> SystemPromptGenerator:
    """Get the default system prompt generator."""
    logger.debug(f"Retrieving default system prompt generator '{DEFAULT_PROMPT_NAME}'")
    result = self.generators.get(DEFAULT_PROMPT_NAME)
    if not result:
      raise ValueError(f"Default prompt '{DEFAULT_PROMPT_NAME}' is not registered.")
    return result

  @inject.method
  def list(self, logger: Logger = inject[get_logger(__name__)]) -> List[str]:
    """List all registered prompt names."""
    logger.debug("Listing all registered system prompts")
    return sorted(self.generators.keys())

  @inject.method
  def has(self, name: str, logger: Logger = inject[get_logger(__name__)]) -> bool:
    """Check if a prompt with the given name is registered."""
    logger.debug(f"Checking if system prompt generator '{name}' is registered")
    return name in self.generators

  @inject.method
  def clear(self, logger: Logger = inject[get_logger(__name__)]) -> None:
    """Clear all registered prompts from memory."""
    logger.debug("Clearing all registered system prompts")
    self.generators.clear()

  @inject.method
  def dump(self, logger: Logger = inject[get_logger(__name__)]) -> Table:
    """Dump all registered prompts to a table."""
    logger.debug("Dumping all registered system prompts to a table")
    table = Table(title="Registered System Prompts")
    table.add_column("Name", justify="left", style="cyan", no_wrap=True)
    table.add_column("Data", justify="left", style="magenta")
    for name, generator in self.generators.items():
      generator_dict = {
        "background": generator.background if generator.background else None,
        "steps": generator.steps if generator.steps else None,
        "output_instructions": generator.output_instructions if generator.output_instructions else None,
        "context_providers": list(generator.context_providers.keys()) if generator.context_providers else None,
      }
      table.add_row(name, Pretty(generator_dict))
    return table
