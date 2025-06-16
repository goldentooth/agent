from atomic_agents.lib.base.base_io_schema import BaseIOSchema
from goldentooth_agent.core.context import context_key

USER_INPUT_KEY = context_key("user_input", BaseIOSchema)
CONSOLE_OUTPUT_KEY = context_key("console_output", BaseIOSchema)
