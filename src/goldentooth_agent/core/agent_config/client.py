from __future__ import annotations
from enum import Enum
import anthropic
import instructor
from instructor import Instructor
from functools import cached_property

class AgentConfigClient(Enum):
  """Enum for different client types."""
  ANTHROPIC = "anthropic"

  @cached_property
  def client(self) -> Instructor:
    """Return the Instructor client based on the enum value."""
    if self == AgentConfigClient.ANTHROPIC:
      return instructor.from_anthropic(anthropic.Anthropic())
    raise NotImplementedError(f"No client handler for: {self}")

  def __str__(self):
    """Return the string representation of the enum value."""
    return self.value
