from atomic_agents.lib.components.system_prompt_generator import SystemPromptContextProviderBase
import textwrap

class PiBramble(SystemPromptContextProviderBase):
  def __init__(self, title: str = "") -> None:
    super().__init__(title=title or "Pi Bramble")

  def get_info(self) -> str:
    """Get information about the Pi Bramble, Goldentooth."""
    content = """
Goldentooth (the Pi Bramble) is a sandbox for experimenting with distributed systems, orchestration layers, and failure
modes. Its services have no purpose but to teach Nate how they behave under stress, failure, and reconfiguration.

The Goldentooth Pi Bramble could be considered a sort of **Chaos Zoo**, a system design playground, or a physical dev
environment for recursive infrastructure. It is a distributed system that is designed to be resilient, self-healing,
and capable of handling failures gracefully. Its nodes are expected to misbehave — chaos, latency, and drift are not
bugs but features, since they reveal the system's true nature under stress.

The Goldentooth Pi Bramble may be treated as a metaphor for the organism, ecosystem, or neural substrate. It encourages
observing system behavior through chaos, complexity, strain, and failure rather than chasing perfection. Its services
may have symbolic, aesthetic, or recursive roles in addition to their literal function.
"""
    return textwrap.dedent(content).strip()
