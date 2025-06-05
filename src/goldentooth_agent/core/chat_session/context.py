from antidote import injectable
from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from .loop import ChatSessionLoopAction

@injectable(lifetime='transient')
@dataclass
class ChatSessionContext:
  """Context for a chat session."""
  current_date: datetime = datetime.now()
  loop_action: Optional[ChatSessionLoopAction] = None
