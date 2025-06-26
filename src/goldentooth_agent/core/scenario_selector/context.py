from goldentooth_agent.core.context import context_key
from goldentooth_agent.core.scenario import Scenario
from .strategy import ScenarioSelectorStrategy

DEFAULT_SCENARIO_KEY = context_key("default_scenario", str)
SCENARIO_SELECTOR_STRATEGY_KEY = context_key(
    "scenario_selector_strategy", ScenarioSelectorStrategy
)
SCENARIO_KEY = context_key("scenario", Scenario)
