from antidote import injectable
from dataclasses import dataclass
from typing import Optional
from .action import ChatSessionLoopAction

@injectable(lifetime='transient')
@dataclass
class ChatSessionLoopContext:
  """Context for a chat loop."""
  user_input: Optional[str] = None
  agent_output: Optional[str] = None
  next_action: Optional[ChatSessionLoopAction] = None
