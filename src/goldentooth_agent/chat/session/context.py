from antidote import injectable
from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from ...pipeline import Pipeline

@injectable
@dataclass
class ChatSessionContext:
  """Context for a chat session."""
  user_input: Optional[str] = None
  agent_output: Optional[str] = None
  should_exit: bool = False
  current_date: datetime = datetime.now()
  next_pipeline: Optional[Pipeline] = None
