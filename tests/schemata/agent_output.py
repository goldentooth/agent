from atomic_agents.agents.base_agent import BaseIOSchema
from pydantic import Field

class AgentOutputSchema(BaseIOSchema):
  """Schema for agent output."""
  chat_message: str = Field(..., description="The agent's message.")

if __name__ == "__main__":
  # Example usage
  output = AgentOutputSchema(chat_message="Hello, this is the agent's response.")
  print(output.chat_message)  # Should print: Hello, this is the agent's response.
  print(output.model_dump_json())  # Print the schema in JSON format
