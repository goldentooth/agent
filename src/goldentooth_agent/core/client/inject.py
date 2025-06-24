import anthropic
from antidote import lazy
import instructor
from instructor import Instructor

@lazy
def get_default_client() -> Instructor:
  """Get the LLM client."""
  return instructor.from_anthropic(anthropic.Anthropic())

if __name__ == "__main__":
  # This is just to ensure that the lazy loading works correctly
  from antidote import world
  client = world[get_default_client()]
  print(f"Client type: {type(client)}")
