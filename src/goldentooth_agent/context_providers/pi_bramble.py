from typing import List
from .base import ContextProviderBase

class PiBramble(ContextProviderBase):
  """Context provider that provides information about the Pi Bramble, Goldentooth."""

  def get_instructions(self) -> List[str]:
    """Get instructions for the Pi Bramble context provider."""
    return [
      "Goldentooth (the Pi Bramble) is a sandbox for experimenting with distributed systems, orchestration layers, and failure modes.",
      "Its services have no purpose but to teach Nate how they behave under stress, failure, and reconfiguration.",
      "The Goldentooth Pi Bramble could be considered a sort of Chaos Zoo, a system design playground, or a physical dev environment for recursive infrastructure.",
      "It is a distributed system that is designed to be resilient, self-healing, and capable of handling failures gracefully.",
      "Its nodes are expected to misbehave — chaos, latency, and drift are not bugs but features, since they reveal the system's true nature under stress.",
      "The Goldentooth Pi Bramble may be treated as a metaphor for the organism, ecosystem, or neural substrate.",
      "It encourages observing system behavior through chaos, complexity, strain, and failure rather than chasing perfection.",
      "Its services may have symbolic, aesthetic, or recursive roles in addition to their literal function.",
    ]

if __name__ == "__main__":
  # Example usage
  from ..initial_context import InitialContext
  initial_context = InitialContext(current_date=None)  # No date context needed for this provider
  pi_bramble_provider = PiBramble(initial_context)

  print("Instructions:")
  for instruction in pi_bramble_provider.get_instructions():
    print(f"- {instruction}")

  print("Pi Bramble context provided.")
