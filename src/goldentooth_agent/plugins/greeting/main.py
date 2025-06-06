from atomic_agents.lib.base.base_tool import BaseIOSchema
from pydantic import Field
from goldentooth_agent.core.chat_session.loop import pipeline_as_action
from goldentooth_agent.core.chat_session.loop.middleware_fns import schema_message_middleware

class GreetingSchema(BaseIOSchema):
  """Schema for the initial greeting created on behalf of the assistant."""
  chat_message: str = Field(..., description="The message to the user.")

greeting_mw = schema_message_middleware(
  schema=GreetingSchema,
  style="bold yellow",
  type="greeting",
)
greeting = pipeline_as_action([greeting_mw])
