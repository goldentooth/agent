from antidote import inject
from atomic_agents.lib.components.system_prompt_generator import SystemPromptContextProviderBase, SystemPromptGenerator
from goldentooth_agent.core.pipeline import Middleware, NextMiddleware, middleware, Pipeline
from goldentooth_agent.core.thunk import Thunk

def attach_context_provider_mw(context_provider: SystemPromptContextProviderBase) -> Middleware:
  """Middleware to attach a context provider to the system prompt generator."""
  @middleware
  @inject
  async def _middleware(system_prompt_generator: SystemPromptGenerator, next: NextMiddleware) -> None:
    """Attach the context provider to the system prompt generator."""
    system_prompt_generator.context_providers[context_provider.title] = context_provider
    await next()
  return _middleware

def attach_context_providers_pl(context_providers: list[SystemPromptContextProviderBase]) -> Pipeline:
  """Pipeline to attach multiple context providers to the system prompt generator."""
  pipeline = Pipeline()
  for provider in context_providers:
    pipeline.use(attach_context_provider_mw(provider))
  return pipeline

def attach_context_providers_th(context_providers: list[SystemPromptContextProviderBase]) -> Thunk[SystemPromptGenerator, SystemPromptGenerator]:
  """Thunk to attach multiple context providers to the system prompt generator."""
  async def _thunk(system_prompt_generator: SystemPromptGenerator) -> SystemPromptGenerator:
    """Attach the context providers to the system prompt generator."""
    pipeline = attach_context_providers_pl(context_providers)
    await pipeline.run(system_prompt_generator)
    return system_prompt_generator
  return Thunk(_thunk)
