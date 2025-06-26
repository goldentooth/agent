from goldentooth_agent.core.context import context_key
from .strategy import PlayerSelectorStrategy

PLAYER_SELECTOR_STRATEGY_KEY = context_key(
    "player_selector_strategy", PlayerSelectorStrategy
)
