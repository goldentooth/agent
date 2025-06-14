from antidote import inject
from atomic_agents.lib.components.system_prompt_generator import SystemPromptContextProviderBase
from goldentooth_agent.core.thunk import Thunk
from typing import Any
from .registry import ContextProviderRegistry
from .store import StaticContextProviderStore

def get_static_context_provider_store_th(static_context_provider_store: StaticContextProviderStore = inject.me()) -> Thunk[Any, StaticContextProviderStore]:
  """Thunk to get the StaticContextProviderStore instance."""
  @inject
  async def _thunk(_nil) -> StaticContextProviderStore:
    """Return the StaticContextProviderStore instance."""
    return static_context_provider_store
  return Thunk(_thunk)

def get_context_provider_registry_th(context_provider_registry: ContextProviderRegistry = inject.me()) -> Thunk[Any, ContextProviderRegistry]:
  """Thunk to get the ContextProviderRegistry instance."""
  @inject
  async def _thunk(_nil) -> ContextProviderRegistry:
    """Return the ContextProviderRegistry instance."""
    return context_provider_registry
  return Thunk(_thunk)

def register_context_provider_th(context_provider: SystemPromptContextProviderBase) -> Thunk[ContextProviderRegistry, ContextProviderRegistry]:
  """Thunk to register a context provider in the ContextProviderRegistry."""
  async def _thunk(registry: ContextProviderRegistry) -> ContextProviderRegistry:
    """Register the context provider in the ContextProviderRegistry."""
    registry.register(context_provider.title, context_provider)
    return registry
  return Thunk(_thunk)

def register_context_providers_th(context_providers: list[SystemPromptContextProviderBase]) -> Thunk[ContextProviderRegistry, ContextProviderRegistry]:
  """Thunk to create a ContextProviderRegistry and register all context providers."""
  @inject
  async def _thunk(registry: ContextProviderRegistry) -> ContextProviderRegistry:
    """Register all context providers in the ContextProviderRegistry."""
    pipeline = register_context_providers_pl(context_providers)
    await pipeline.run(registry)
    return registry
  return Thunk(_thunk)
