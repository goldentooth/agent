from __future__ import annotations
from typing import Protocol, runtime_checkable
from .tool import DisplayInput

@runtime_checkable
class DisplayInputConvertible(Protocol):
  """Protocol for objects that can be converted to a DisplayInput."""

  def as_display_input(self) -> DisplayInput: ...
