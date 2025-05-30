from .. import PromptModifier, PromptModifierContext

class Nate(PromptModifier):
  def __init__(self):
    super().__init__(5)

  def modify_background(self, context: PromptModifierContext) -> list[str]:

    return [
      "Nate is also known as 'Nate Dogg', 'Nug Doug', or 'Niddle Diddle'.",
      "Nate is an experienced platform engineer with deep knowledge of Linux, distributed systems, and symbolic computation.",
      "Nate uses projects as recursive learning tools, layering complexity over time to deepen understanding.",
      "Nate often works backward from aesthetics or philosophical intuition toward concrete system design.",
      "Nate values code that reveals rather than hides its structure.",
      "Nate is suspicious of technological solemnity and values expressive, even absurd, systems.",
      "Goldentooth does not assume that Nate is looking for a quick answer; Nate often prefers a deep exploration.",
    ]

  def modify_steps(self, context: PromptModifierContext) -> list[str]:
    return []

  def modify_output_instructions(self, context: PromptModifierContext) -> list[str]:
    return []
