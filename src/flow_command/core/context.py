from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal

from rich.console import Console

from flow.registry import FlowRegistry, flow_registry


@dataclass
class FlowCommandContext:
    """Universal context for flow commands across CLI and chat interfaces."""

    # Input/Output configuration
    input_data: Any = None
    output_format: Literal["text", "json", "table"] = "text"

    # Display configuration
    plain_output: bool = False
    interactive: bool = True
    record_svg: bool = False
    console: Console = field(default_factory=Console)

    # Flow-specific configuration
    flow_registry: FlowRegistry = field(default_factory=lambda: flow_registry)
    execution_timeout: float = 30.0

    # Context identification
    source: Literal["cli", "chat", "test"] = "cli"
    user_id: str | None = None

    @classmethod
    def from_cli(
        cls,
        input_data: Any = None,
        output_format: Literal["text", "json", "table"] = "text",
        plain_output: bool = False,
        interactive: bool = True,
        record_svg: bool = False,
        execution_timeout: float = 30.0,
        **kwargs: Any,
    ) -> FlowCommandContext:
        """Create context from CLI parameters."""
        return FlowCommandContext(
            input_data=input_data,
            output_format=output_format,
            plain_output=plain_output,
            interactive=interactive,
            record_svg=record_svg,
            execution_timeout=execution_timeout,
            source="cli",
            **kwargs,
        )

    @classmethod
    def from_chat(
        cls,
        input_data: Any = None,
        output_format: Literal["text", "json", "table"] = "text",
        user_id: str | None = None,
        execution_timeout: float = 30.0,
        **kwargs: Any,
    ) -> FlowCommandContext:
        """Create context from chat interface."""
        return FlowCommandContext(
            input_data=input_data,
            output_format=output_format,
            plain_output=False,
            interactive=True,
            record_svg=False,
            execution_timeout=execution_timeout,
            source="chat",
            user_id=user_id,
            **kwargs,
        )

    @classmethod
    def from_test(
        cls,
        input_data: Any = None,
        output_format: Literal["text", "json", "table"] = "text",
        execution_timeout: float = 5.0,
        **kwargs: Any,
    ) -> FlowCommandContext:
        """Create context for testing."""
        return FlowCommandContext(
            input_data=input_data,
            output_format=output_format,
            plain_output=True,
            interactive=False,
            record_svg=False,
            execution_timeout=execution_timeout,
            source="test",
            **kwargs,
        )
