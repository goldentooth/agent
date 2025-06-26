from __future__ import annotations
from antidote import inject
from goldentooth_agent.core.context import Context
from goldentooth_agent.core.scenario import Scenario, ScenarioRegistry
from .context import DEFAULT_SCENARIO_KEY
from .strategy import ScenarioSelectorStrategy
from .strategy_registry import register_scenario_selector_strategy


class DefaultScenarioSelectorStrategy(ScenarioSelectorStrategy):
    """Default strategy for selecting scenarios."""

    id = "default"
    description = (
        "Default strategy for selecting scenarios based on the current context."
    )

    @inject.method
    def select_scenario(self, context: Context, scenario_registry: ScenarioRegistry = inject.me()) -> Scenario:  # type: ignore
        """Select a scenario based on the current context."""
        default_scenario_id = context.get(DEFAULT_SCENARIO_KEY)
        return scenario_registry.get(default_scenario_id)


register_scenario_selector_strategy(obj=DefaultScenarioSelectorStrategy())
