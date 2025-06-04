from antidote import injectable
from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from .action import ChatLoopAction

@injectable
@dataclass
class ChatLoopContext:
  """Context for a chat loop."""
  user_input: Optional[str] = None
  agent_output: Optional[str] = None
  next_action: Optional[ChatLoopAction] = None
