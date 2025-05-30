from atomic_agents.lib.components.system_prompt_generator import SystemPromptContextProviderBase
import textwrap

class Nate(SystemPromptContextProviderBase):
  def __init__(self, title: str = "") -> None:
    super().__init__(title=title or "Nate")

  def get_info(self) -> str:
    """Get information about Nate."""
    content = """
Nate is also known as 'Nate Dogg', 'Nug Doug', or 'Niddle Diddle'. Hd is an experienced platform engineer with deep
knowledge of Linux, distributed systems, and symbolic computation. He uses projects as recursive learning tools,
layering complexity over time to deepen understanding. He often works backward from aesthetics or philosophical
intuition toward concrete system design.

Nate values code that reveals rather than hides its structure. He is suspicious of technological solemnity and values
expressive, even absurd, systems. He often prefers a deep exploration to a quick answer. He often treats technical
systems as metaphors for consciousness, learning, or cognition.

Nate values systems that remain legible under recursive or self-modifying conditions. He is prone to dialectical
thinking and often frames problems in oppositional pairs or conceptual tension. He uses uncertainty or ambiguity as
signals to reframe or clarify rather than as points of failure. He prefers minimal, observable, and composable systems
over monolithic or black-box abstractions.

Nate is comfortable reading system logs, strace output, and core dumps if needed. He often uses irony and humor to
suggest structural insight or symbolic inversion. He is in the process of shifting from DevOps into ML infrastructure,
simulation, or research tooling. He prefers projects that blur the lines between infrastructure, cognition, simulation,
and narrative. He prefers systems that preserve user agency and allow for fine-grained introspection and override.

Nate favors observable-first design — systems should make their internal state clear and queryable. He prefers to run
services with declarative specs, minimal defaults, and non-ephemeral state surfaces. He values tools that expose
behavioral drift, causal ambiguity, and system topology.
"""
    return textwrap.dedent(content).strip()
