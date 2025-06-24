from goldentooth_agent.core.context import context_key
from .strategy import ScenarioSelectorStrategy

SCENARIO_SELECTOR_STRATEGY_KEY = context_key("scenario_selector_strategy", ScenarioSelectorStrategy)
