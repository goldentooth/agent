from goldentooth_agent.core.context import context_key
from .strategy import PersonaSelectorStrategy

PERSONA_SELECTOR_STRATEGY_KEY = context_key(
    "persona_selector_strategy", PersonaSelectorStrategy
)
