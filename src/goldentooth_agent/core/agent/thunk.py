from atomic_agents.lib.base.base_io_schema import BaseIOSchema
from atomic_agents.agents.base_agent import BaseAgent
from goldentooth_agent.core.dynamic_context_provider import DynamicContextProvider
from goldentooth_agent.core.system_prompt import HasSystemPromptGenerator, enable_context_provider, disable_context_provider
from goldentooth_agent.core.thunk import Thunk, thunk
from typing import Callable
from .context import HasAgents

def thunkify_agent(agent: BaseAgent) -> Thunk[BaseIOSchema, BaseIOSchema]:
  """Convert an agent into a thunk."""
  async def _as_thunk(params: BaseIOSchema) -> BaseIOSchema:
    """Run the agent with the given parameters."""
    return agent.run(params)
  return Thunk(_as_thunk)

def enable_agent(agent_name: str, agent: BaseAgent) -> Thunk[HasAgents, HasAgents]:
  """Enable an agent in the context."""
  @thunk
  async def _enable(ctx) -> HasAgents:
    """Enable the agent in the context."""
    ctx.agents[agent_name] = agent
    return ctx
  return _enable

def disable_agent(agent_name: str) -> Thunk[HasAgents, HasAgents]:
  """Disable an agent in the context."""
  @thunk
  async def _disable(ctx) -> HasAgents:
    """Disable the agent in the context."""
    if agent_name in ctx.agents:
      del ctx.agents[agent_name]
    return ctx
  return _disable

def enable_agent_context_provider(agent_name: str, agent_fn: Callable[[], str]) -> Thunk[HasSystemPromptGenerator, HasSystemPromptGenerator]:
  """Enable a agent's context provider in the system prompt generator."""
  @thunk
  async def _enable(ctx) -> HasSystemPromptGenerator:
    """Enable the agent's context provider in the system prompt generator."""
    dcp = DynamicContextProvider(title=agent_name, fn=agent_fn)
    ctx = await enable_context_provider(dcp)(ctx)
    return ctx
  return _enable

def disable_tool_context_provider(agent_name: str) -> Thunk[HasSystemPromptGenerator, HasSystemPromptGenerator]:
  """Disable a agent's context provider in the system prompt generator."""
  @thunk
  async def _disable(ctx) -> HasSystemPromptGenerator:
    """Disable the agent's context provider in the system prompt generator."""
    ctx = await disable_context_provider(agent_name)(ctx)
    return ctx
  return _disable
