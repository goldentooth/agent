from __future__ import annotations
from typing import Protocol, runtime_checkable
from .tool import CommandInput

@runtime_checkable
class CommandInputConvertible(Protocol):
  """Protocol for objects that can be converted to a CommandInput."""

  def as_command_input(self) -> CommandInput: ...
