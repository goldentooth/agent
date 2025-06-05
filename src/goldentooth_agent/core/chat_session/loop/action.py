from typing import Awaitable, Callable, TYPE_CHECKING

if TYPE_CHECKING:
  from .context import ChatSessionLoopContext

type ChatSessionLoopAction = Callable[[ChatSessionLoopContext], Awaitable[ChatSessionLoopContext]]
