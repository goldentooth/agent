from __future__ import annotations
from antidote import inject, injectable
from atomic_agents.lib.components.system_prompt_generator import SystemPromptGenerator, SystemPromptContextProviderBase
from goldentooth_agent.core.static_context_provider import StaticContextProviderRegistry
from typing import Dict, List, Optional
from .store import StaticSystemPromptStore

DEFAULT_PROMPT_NAME = "default"

@injectable(factory_method='create')
class StaticSystemPromptRegistry:
  """Manages system prompts stored as YAML files."""

  def __init__(
    self,
    store: StaticSystemPromptStore = inject.me(),
    context_provider_registry: StaticContextProviderRegistry = inject.me(),
  ):
    """Initialize the registry with a filesystem store."""
    self.store = store
    self.context_provider_registry = context_provider_registry
    self._generators: Dict[str, SystemPromptGenerator] = {}

  @classmethod
  def create(cls) -> StaticSystemPromptRegistry:
    """Create a new SystemPromptRegistry instance."""
    result = cls()
    return result

  def register(self, name: str, generator: SystemPromptGenerator):
    """Register a prompt generator under a given name (in-memory only)."""
    self._generators[name] = generator

  def unregister(self, name: str):
    """Unregister a prompt generator by name (in-memory only)."""
    self._generators.pop(name, None)

  def get(self, name: str) -> Optional[SystemPromptGenerator]:
    """Retrieve a registered prompt generator by name."""
    return self._generators.get(name)

  def get_default(self) -> SystemPromptGenerator:
    """Get the default system prompt generator."""
    if DEFAULT_PROMPT_NAME not in self._generators:
      self.load(DEFAULT_PROMPT_NAME)
    result = self._generators.get(DEFAULT_PROMPT_NAME)
    if not result:
      raise ValueError(f"Default prompt '{DEFAULT_PROMPT_NAME}' is not registered.")
    return result

  def list(self) -> List[str]:
    """List all registered prompt names."""
    return sorted(self._generators.keys())

  def exists(self, name: str) -> bool:
    """Check if a prompt with the given name is registered."""
    return name in self._generators

  def load(self, name: str):
    """Load a prompt from the underlying store and register it."""
    if not self.store.exists(name):
      return
    data = self.store.load(name)
    gen = self._build(data)
    self.register(name, gen)

  def save(self, name: str):
    """Persist a registered prompt back to the store."""
    gen = self._generators.get(name)
    if not gen:
      return
    data = {
      "background": gen.background,
      "steps": gen.steps,
      "output_instructions": gen.output_instructions,
      "context_providers": list(gen.context_providers.keys()),
    }
    self.store.save(name, data)

  def delete(self, name: str) -> bool:
    """Delete a prompt by name from both memory and store."""
    if name in self._generators:
      del self._generators[name]
    return self.store.delete(name)

  def clear(self):
    """Clear all registered prompts from memory."""
    self._generators.clear()

  def _build(self, data: dict) -> SystemPromptGenerator:
    """Construct a SystemPromptGenerator from YAML data."""
    background = data.get("background", [])
    steps = data.get("steps", [])
    output_instructions = data.get("output_instructions", [])
    context_provider_ids = data.get("context_providers", [])
    for context_provider_id in context_provider_ids:
      if not self.context_provider_registry.exists(context_provider_id):
        raise ValueError(f"Context provider '{context_provider_id}' does not exist.")

    providers: Dict[str, SystemPromptContextProviderBase] = {
      ident: self.context_provider_registry.get(ident)
      for ident in context_provider_ids
    }

    return SystemPromptGenerator(
      background=background,
      steps=steps,
      output_instructions=output_instructions,
      context_providers=providers,
    )
