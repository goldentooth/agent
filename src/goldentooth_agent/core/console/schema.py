from __future__ import annotations
from typing import Protocol, runtime_checkable
from .tool import ConsoleOutput

@runtime_checkable
class ConsoleOutputConvertible(Protocol):
  """Protocol for objects that can be converted to a ConsoleOutput."""

  def as_console_output(self) -> ConsoleOutput: ...
