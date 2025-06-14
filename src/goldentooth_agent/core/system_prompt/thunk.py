from atomic_agents.lib.components.system_prompt_generator import SystemPromptContextProviderBase
from goldentooth_agent.core.system_prompt import HasSystemPromptGenerator
from goldentooth_agent.core.thunk import Thunk, thunk

def enable_context_provider(context_provider: SystemPromptContextProviderBase) -> Thunk[HasSystemPromptGenerator, HasSystemPromptGenerator]:
  """Enable a tool as a context provider."""
  @thunk
  async def _enable(ctx) -> HasSystemPromptGenerator:
    """Enable the context provider."""
    ctx.system_prompt_generator.context_providers[context_provider.title] = context_provider
    return ctx
  return _enable

def disable_context_provider(name: str) -> Thunk[HasSystemPromptGenerator, HasSystemPromptGenerator]:
  """Disable a context provider."""
  @thunk
  async def _disable(ctx) -> HasSystemPromptGenerator:
    """Disable the context provider."""
    if name in ctx.system_prompt_generator.context_providers:
      del ctx.system_prompt_generator.context_providers[name]
    return ctx
  return _disable
