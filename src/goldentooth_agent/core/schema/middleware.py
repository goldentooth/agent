from antidote import inject
from atomic_agents.lib.components.system_prompt_generator import SystemPromptContextProviderBase
from goldentooth_agent.core.pipeline import Middleware, NextMiddleware, middleware, Pipeline
from goldentooth_agent.core.thunk import Thunk
from typing import Any

def get_static_context_provider_store_th(static_context_provider_store: StaticContextProviderStore = inject.me()) -> Thunk[Any, StaticContextProviderStore]:
  """Thunk to get the StaticContextProviderStore instance."""
  @inject
  async def _thunk(_nil) -> StaticContextProviderStore:
    """Return the StaticContextProviderStore instance."""
    return static_context_provider_store
  return Thunk(_thunk)
