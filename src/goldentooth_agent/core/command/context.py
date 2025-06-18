from atomic_agents.lib.base.base_io_schema import BaseIOSchema
from goldentooth_agent.core.context import context_key

COMMAND_INPUT_KEY = context_key("command_input", BaseIOSchema)
COMMAND_OUTPUT_KEY = context_key("command_output", BaseIOSchema)
