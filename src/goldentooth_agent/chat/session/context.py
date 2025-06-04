from antidote import injectable
from dataclasses import dataclass
from datetime import datetime

@injectable
@dataclass
class ChatSessionContext:
  """Context for a chat session."""
  current_date: datetime = datetime.now()
