from goldentooth_agent.core.context import context_key
from .strategy import RoleSelectorStrategy

ROLE_SELECTOR_STRATEGY_KEY = context_key("role_selector_strategy", RoleSelectorStrategy)
