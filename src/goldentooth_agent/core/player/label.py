from __future__ import annotations
from rich.style import Style
from rich.text import Text

class PlayerLabel:
  """A class to represent a player label."""

  def __init__(self, text: str, color: str) -> None:
    """Initialize the player label with text and color."""
    self.text = text
    self.color = color

  def get_renderable(self) -> Text:
    """Get the renderable text of the label."""
    style = Style(color=self.color, bold=True)
    return Text(self.text, style=style)

  @classmethod
  def from_dict(cls, data: dict) -> PlayerLabel:
    """Create a PlayerLabel from a dictionary."""
    return cls(text=data["text"], color=data["color"])

  def to_dict(self) -> dict:
    """Convert the PlayerLabel to a dictionary."""
    return {
      "text": self.text,
      "color": self.color,
    }

  def __str__(self) -> str:
    """Return a string representation of the PlayerLabel."""
    return self.text

  def __repr__(self) -> str:
    """Return a detailed string representation of the PlayerLabel."""
    return f"PlayerLabel(text={self.text!r}, color={self.color!r})"
