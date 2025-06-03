from antidote import injectable
from dataclasses import dataclass
from .persona import ChatPersona

@injectable
@dataclass
class ChatOptions:
  """Options for the chat command."""
  persona: ChatPersona = ChatPersona.default
  tool_mode: bool = False
  raw: bool = False
