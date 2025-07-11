from __future__ import annotations

from pathlib import Path
from typing import Annotated, Any, Literal, cast

import typer

from ..core.context import FlowCommandContext
from ..operations import (
    flow_list_implementation,
    flow_run_implementation,
    flow_search_implementation,
)
from .display import FlowDisplay


def flow_list_cli(
    category: Annotated[
        str | None, typer.Option("--category", "-c", help="Filter by category")
    ] = None,
    tag: Annotated[
        str | None, typer.Option("--tag", "-t", help="Filter by tag")
    ] = None,
    output_format: Annotated[
        str, typer.Option("--format", "-f", help="Output format (text, json, table)")
    ] = "text",
    plain: Annotated[
        bool, typer.Option("--plain", "-p", help="Plain text output")
    ] = False,
) -> None:
    """List available flows with optional filtering."""
    # Create context
    context = FlowCommandContext.from_cli(
        output_format=cast(Literal["text", "json", "table"], output_format),
        plain_output=plain,
    )

    # Execute implementation
    result = flow_list_implementation(category, tag, context)

    # Handle display and exit
    display = FlowDisplay(context)
    display.show_result(result)
    if not result.success:
        raise typer.Exit(1)


def flow_search_cli(
    query: Annotated[
        str, typer.Argument(help="Search query for flow names or metadata")
    ],
    output_format: Annotated[
        str, typer.Option("--format", "-f", help="Output format (text, json, table)")
    ] = "text",
    plain: Annotated[
        bool, typer.Option("--plain", "-p", help="Plain text output")
    ] = False,
) -> None:
    """Search flows by name or metadata."""
    # Create context
    context = FlowCommandContext.from_cli(
        output_format=cast(Literal["text", "json", "table"], output_format),
        plain_output=plain,
    )

    # Execute implementation
    result = flow_search_implementation(query, context)

    # Handle display and exit
    display = FlowDisplay(context)
    display.show_result(result)
    if not result.success:
        raise typer.Exit(1)


def flow_run_cli(
    flow_name: Annotated[str, typer.Argument(help="Name of flow to execute")],
    input_file: Annotated[
        Path | None, typer.Option("--input", "-i", help="Input file path")
    ] = None,
    input_data: Annotated[
        str | None, typer.Option("--data", "-d", help="Input data (JSON or text)")
    ] = None,
    output_format: Annotated[
        str, typer.Option("--format", "-f", help="Output format (text, json, table)")
    ] = "text",
    timeout: Annotated[
        float, typer.Option("--timeout", "-t", help="Execution timeout in seconds")
    ] = 30.0,
    plain: Annotated[
        bool, typer.Option("--plain", "-p", help="Plain text output")
    ] = False,
) -> None:
    """Execute a flow with input data."""
    # Parse input data if provided as string
    parsed_data: Any = None
    if input_data:
        import json

        try:
            parsed_data = json.loads(input_data)
        except json.JSONDecodeError:
            # Treat as plain text
            parsed_data = input_data

    # Create context
    context = FlowCommandContext.from_cli(
        output_format=cast(Literal["text", "json", "table"], output_format),
        plain_output=plain,
        execution_timeout=timeout,
    )

    # Execute implementation
    result = flow_run_implementation(flow_name, input_file, parsed_data, context)

    # Handle display and exit
    display = FlowDisplay(context)
    display.show_flow_execution(flow_name, result)
    if not result.success:
        raise typer.Exit(1)
