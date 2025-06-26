from __future__ import annotations
from antidote import inject, injectable
from atomic_agents.agents.base_agent import BaseAgent
from atomic_agents.lib.base.base_io_schema import BaseIOSchema
from goldentooth_agent.core.agent_config import AgentConfigRegistry
from goldentooth_agent.core.logging import get_logger
from goldentooth_agent.core.named_registry import NamedRegistry, make_register_fn
from goldentooth_agent.core.thunk import Thunk
from rich.table import Table


@injectable()
class AgentRegistry(NamedRegistry[BaseAgent]):
    """Registry for managing agents."""

    def get_thunk(self, agent_name: str) -> Thunk[BaseIOSchema, BaseIOSchema]:
        """Get a thunk for the specified agent name."""
        from .thunk import thunkify_agent

        agent = self.get(agent_name)
        return thunkify_agent(agent)

    def get_by_input_schema(self, schema: type[BaseIOSchema]) -> BaseAgent:
        """Get an agent by its input schema."""
        for agent in self.all():
            if issubclass(schema, agent.input_schema):
                return agent
        raise LookupError(f"No agent found for input schema: {schema}")

    @inject
    def get(
        self, id: str, agent_config_registry: AgentConfigRegistry = inject.me()
    ) -> BaseAgent:  # override
        """Get an agent by its ID."""
        try:
            return super().get(id)
        except KeyError:
            agent = BaseAgent(config=agent_config_registry.get(id))
            self.set(id, agent)
            return agent

    @inject.method
    def dump(self, logger=inject[get_logger(__name__)]) -> Table:
        """Dump the registry to the console."""
        logger.debug("Dumping agent registry")
        table = Table(title=f"Agent Registry Dump")
        table.add_column("Name")
        table.add_column("Agent", overflow="fold")
        for k, v in self.items():
            table.add_row(str(k), repr(v))
        return table


register_agent = make_register_fn(AgentRegistry)
