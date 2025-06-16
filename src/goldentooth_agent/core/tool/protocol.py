from typing import Protocol, runtime_checkable

@runtime_checkable
class HasGetInfo(Protocol):
  """Protocol for objects that have a get_info method."""

  def get_info(self) -> str: ...
