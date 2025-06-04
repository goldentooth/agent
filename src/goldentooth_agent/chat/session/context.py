from antidote import injectable
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional

class ChatSessionState(str, Enum):
  """Enumeration of possible states for a chat session."""
  startup = "chat_session_state.startup"

@injectable
@dataclass
class ChatSessionContext:
  """Context for a chat session."""
  state: ChatSessionState = ChatSessionState.startup
  user_input: Optional[str] = None
  agent_output: Optional[str] = None
  should_exit: bool = False
  current_date: datetime = datetime.now()
