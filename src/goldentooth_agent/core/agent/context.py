from atomic_agents.agents.base_agent import BaseAgent
from atomic_agents.lib.base.base_io_schema import BaseIOSchema
from goldentooth_agent.core.context import context_key
from rich.text import Text

AGENT_INPUT_KEY = context_key("agent_input", BaseIOSchema)
AGENT_OUTPUT_KEY = context_key("agent_output", BaseIOSchema)
AGENT_KEY = context_key("agent", BaseAgent)
AGENT_PREFIX_KEY = context_key("agent_prefix", Text)
SHOULD_SKIP_AGENT_KEY = context_key("should_skip_agent", bool)
