from .. import PromptModifier, PromptModifierContext

class PiBramble(PromptModifier):
  def __init__(self):
    super().__init__(-50)

  def modify_background(self, context: PromptModifierContext) -> list[str]:
    return [
      "Goldentooth (the Pi Bramble) is a sandbox for experimenting with distributed systems, orchestration layers, and failure modes.",
      "Goldentooth services have no purpose but to teach Nate how they behave under stress, failure, and reconfiguration.",
      "Goldentooth could be considered a sort of **Chaos Zoo**, a system design playground, or a physical dev environment for recursive infrastructure.",
      "Goldentooth is a distributed system that is designed to be resilient, self-healing, and capable of handling failures gracefully.",
      "Goldentooth nodes are expected to misbehave — chaos, latency, and drift are not bugs but features.",
      "Goldentooth may be treated as a metaphor for the organism, ecosystem, or neural substrate.",
      "Goldentooth encourages observing system behavior through chaos, complexity, strain, and failure rather than chasing perfection.",
      "Goldentooth services may have symbolic, aesthetic, or recursive roles in addition to their literal function.",
    ]

  def modify_steps(self, context: PromptModifierContext) -> list[str]:
    return []

  def modify_output_instructions(self, context: PromptModifierContext) -> list[str]:
    return [
      "If you have suggestions for additional tools that could help you answer the question, suggest them.",
    ]
