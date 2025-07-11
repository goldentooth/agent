"""Command context and result types for universal command interface."""

# pyright: reportUnknownVariableType=false

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Any, Optional

from rich.console import Console


@dataclass
class CommandContext:
    """Universal command context that works across CLI and chat interfaces.

    This class provides a unified interface for command execution that can
    be used in both CLI and chat contexts.
    """

    # Input data
    input_data: Any = None

    # Output configuration
    output_format: str = "text"  # text, json, auto
    plain_output: bool = False
    no_color: bool = False

    # Interface context
    interactive: bool = True
    user_id: Optional[str] = None
    session_id: Optional[str] = None

    # Recording and demos
    record_svg: bool = False
    svg_output_path: Optional[str] = None

    # Console configuration
    console: Console = field(default_factory=Console)

    def __post_init__(self) -> None:
        """Post-initialization configuration."""
        # Respect NO_COLOR environment variable
        if os.environ.get("NO_COLOR") or self.no_color:
            self.console = Console(color_system=None)

        # Configure console for plain output
        if self.plain_output:
            self.console = Console(
                color_system=None,
                legacy_windows=False,
                force_terminal=False,
                force_jupyter=False,
                force_interactive=False,
            )

    @classmethod
    def from_cli(
        cls,
        input_data: Any = None,
        output_format: str = "text",
        plain: bool = False,
        no_color: bool = False,
        record: bool = False,
        record_path: Optional[str] = None,
    ) -> CommandContext:
        """Create context from CLI parameters."""
        return cls(
            input_data=input_data,
            output_format=output_format,
            plain_output=plain,
            no_color=no_color,
            interactive=True,
            record_svg=record,
            svg_output_path=record_path,
        )

    @classmethod
    def from_chat(
        cls,
        input_data: Any = None,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        output_format: str = "text",
    ) -> CommandContext:
        """Create context from chat interface."""
        return cls(
            input_data=input_data,
            output_format=output_format,
            interactive=True,
            user_id=user_id,
            session_id=session_id,
            plain_output=False,  # Chat interfaces can handle rich output
        )


@dataclass
class CommandResult:
    """Universal command result that can be displayed in any interface."""

    # Core result data
    data: Any = None

    # Status information
    success: bool = True
    error_message: Optional[str] = None
    exit_code: int = 0

    # Display information
    display_data: Any = None
    formatted_output: Optional[str] = None

    # Metadata
    execution_time: Optional[float] = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_json(self) -> dict[str, Any]:
        """Convert result to JSON-serializable format."""
        return {
            "data": self.data,
            "success": self.success,
            "error_message": self.error_message,
            "exit_code": self.exit_code,
            "execution_time": self.execution_time,
            "metadata": self.metadata,
        }

    def to_text(self) -> str:
        """Convert result to plain text format."""
        if self.formatted_output:
            return self.formatted_output

        if not self.success:
            return f"Error: {self.error_message or 'Unknown error'}"

        if isinstance(self.data, str):
            return self.data

        return str(self.data) if self.data is not None else ""
