from antidote import injectable
from dataclasses import dataclass

@dataclass
@injectable
class ChatOptions:
  """Options for the chat session."""

  is_straight: bool = False
  """Whether to use straightness (don't mess around) or not."""
