# metadata.py
from typing import List

class ToolMetadata:
  """Metadata for a tool."""
  name: str
  instructions: List[str]

  @classmethod
  def get_name(cls) -> str:
    """Get the name of the tool."""
    return cls.name

  @classmethod
  def get_instructions(cls) -> str:
    """Get instructions for using the tool."""
    return "\n".join(cls.instructions)
