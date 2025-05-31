from atomic_agents.agents.base_agent import BaseIOSchema
from pydantic import Field

class UserInputSchema(BaseIOSchema):
  """Schema for user input."""
  chat_message: str = Field(..., description="The user's message.")

if __name__ == "__main__":
  # Example usage
  input = UserInputSchema(chat_message="Hello, this is the user's message.")
  print(input.chat_message)  # Should print: Hello, this is the user's message.
  print(input.model_dump_json())  # Print the schema in JSON format
