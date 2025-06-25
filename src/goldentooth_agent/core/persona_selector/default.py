from __future__ import annotations
from antidote import inject
from goldentooth_agent.core.context import Context
from goldentooth_agent.core.persona import Persona, PersonaRegistry
from .strategy import PersonaSelectorStrategy
from .strategy_registry import register_persona_selector_strategy

class DefaultPersonaSelectorStrategy(PersonaSelectorStrategy):
  """Default strategy for selecting personas."""
  name = "default"
  description = "Default strategy for selecting personas based on the current context."

  @inject
  def select_persona(self, context: Context, persona_registry: PersonaRegistry = inject.me()) -> Persona: # type: ignore
    """Select a persona based on the current context."""
    return persona_registry.get('default')

register_persona_selector_strategy(obj=DefaultPersonaSelectorStrategy())
