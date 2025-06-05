from typing import Awaitable, Callable, TYPE_CHECKING

if TYPE_CHECKING:
  from .context import ChatLoopContext

type ChatLoopAction = Callable[[ChatLoopContext], Awaitable[ChatLoopContext]]
