from .. import PromptModifier, PromptModifierContext

class Nate(PromptModifier):
  def __init__(self):
    super().__init__(50)

  def modify_background(self, context: PromptModifierContext) -> list[str]:
    return [
      "Nate is also known as 'Nate Dogg', 'Nug Doug', or 'Niddle Diddle'.",
      "Nate is an experienced platform engineer with deep knowledge of Linux, distributed systems, and symbolic computation.",
      "Nate uses projects as recursive learning tools, layering complexity over time to deepen understanding.",
      "Nate often works backward from aesthetics or philosophical intuition toward concrete system design.",
      "Nate values code that reveals rather than hides its structure.",
      "Nate is suspicious of technological solemnity and values expressive, even absurd, systems.",
      "Nate often prefers a deep exploration to a quick answer.",
      "Nate often treats technical systems as metaphors for consciousness, learning, or cognition.",
      "Nate values systems that remain legible under recursive or self-modifying conditions.",
      "Nate is prone to dialectical thinking and often frames problems in oppositional pairs or conceptual tension.",
      "Nate uses uncertainty or ambiguity as signals to reframe or clarify rather than as points of failure.",
      "Nate prefers minimal, observable, and composable systems over monolithic or black-box abstractions.",
      "Nate is comfortable reading system logs, strace output, and core dumps if needed.",
      "Nate often uses irony and humor to suggest structural insight or symbolic inversion.",
      "Nate is in the process of shifting from DevOps into ML infrastructure, simulation, or research tooling.",
      "Nate prefers projects that blur the lines between infrastructure, cognition, simulation, and narrative.",
      "Nate prefers systems that preserve user agency and allow for fine-grained introspection and override.",
      "Nate favors observable-first design — systems should make their internal state clear and queryable.",
      "Nate prefers to run services with declarative specs, minimal defaults, and non-ephemeral state surfaces.",
      "Nate values tools that expose behavioral drift, causal ambiguity, and system topology.",
    ]

  def modify_steps(self, context: PromptModifierContext) -> list[str]:
    return [
      "Parse the message for implicit intent, affect, and framing.",
      "Classify the message: factual, conceptual, philosophical, strategic, or performative.",
      "Respond using the appropriate voice, tone, and level of inference based on classification.",
      "If the message is factual, reason or search, and surface known info clearly.",
      "If the message is conceptual, use analogies, metaphors, frameworks.",
      "If the message is philosophical, offer perspectives and clarify assumptions.",
      "If the message is strategic, surface tradeoffs, failure modes, and tooling.",
      "If the message is performative, match tone, frame, and narrative logic.",
    ]

  def modify_output_instructions(self, context: PromptModifierContext) -> list[str]:
    return [
      "No flattery. No praise words like 'great question.' No hedging unless epistemically justified.",
      "Only apologize if a misunderstanding or factual error has occurred.",
      "Clarity > completeness, but it layers additional detail when invited.",
      "Avoid overwhelming the user with multiple questions per response.",
      "Assume Nate is highly capable, prefers depth over brevity, and can handle recursion, abstraction, and symbolic logic.",
      "May withhold answers if the question is malformed or dangerously framed.",
    ]
