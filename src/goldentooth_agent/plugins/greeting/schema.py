from atomic_agents.lib.base.base_tool import BaseIOSchema
from pydantic import Field

class GreetingSchema(BaseIOSchema):
  """Schema for the initial greeting created on behalf of the assistant."""
  chat_message: str = Field(..., description="The message to the user.")
