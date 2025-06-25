from __future__ import annotations
from antidote import inject
from goldentooth_agent.core.context import Context
from goldentooth_agent.core.persona import Persona, PersonaRegistry
from goldentooth_agent.core.player import PlayerRegistry
from goldentooth_agent.core.role import Role, RoleRegistry
from .strategy import PlayerSelectorStrategy
from .strategy_registry import register_player_selector_strategy

class DefaultPlayerSelectorStrategy(PlayerSelectorStrategy):
  """Default strategy for selecting players."""
  id = "default"
  description = "Default strategy for selecting players based on the current context."

  @inject.method
  def select_persona(  # type: ignore
    self,
    context: Context,
    role: Role,
    persona_registry: PersonaRegistry = inject.me(),
    player_registry: PlayerRegistry = inject.me(),
  ) -> Persona: # type: ignore
    """Select a player based on the current context."""
    for player in player_registry.all():
      if player.role_id == role.name:
        return persona_registry.get(player.persona_id)

  @inject.method
  def select_role(  # type: ignore
    self,
    context: Context,
    persona: Persona,
    role_registry: RoleRegistry = inject.me(),
    player_registry: PlayerRegistry = inject.me(),
  ) -> Role: # type: ignore
    """Select a role based on the current context."""
    for player in player_registry.all():
      if player.persona_id == persona.name:
        return role_registry.get(player.role_id)

register_player_selector_strategy(obj=DefaultPlayerSelectorStrategy())
