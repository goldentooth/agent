from __future__ import annotations

import asyncio
import json
import sys
from collections.abc import AsyncIterator
from typing import Annotated, Any

import typer
from antidote import inject
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from goldentooth_agent.cli.commands.tools import get_available_tools
from goldentooth_agent.core.flow import Flow

app = typer.Typer()

# Type aliases for flow system flexibility
FlowType = Flow[Any, Any]  # type: ignore[explicit-any]  # Flows can handle any input/output types
StreamData = Any  # type: ignore[explicit-any]  # Stream data can be any type
InputData = dict[str, Any]  # type: ignore[explicit-any]  # JSON input data


def get_available_flows() -> dict[str, FlowType]:
    """Get a registry of available flows."""
    # Convert tools to flows for execution
    flows = {}
    tools = get_available_tools()

    for tool_name, tool in tools.items():
        flows[tool_name] = tool.as_flow()

    # Add some built-in flows
    async def identity_flow(
        stream: AsyncIterator[StreamData],
    ) -> AsyncIterator[StreamData]:
        """Identity flow that passes data through unchanged."""
        async for item in stream:
            yield item

    async def json_pretty_flow(stream: AsyncIterator[StreamData]) -> AsyncIterator[str]:
        """Flow that pretty-prints JSON data."""
        async for item in stream:
            if hasattr(item, "model_dump"):
                # Pydantic model
                yield json.dumps(item.model_dump(), indent=2)
            elif isinstance(item, dict):
                yield json.dumps(item, indent=2)
            else:
                yield str(item)

    flows["identity"] = Flow(identity_flow, name="identity")
    flows["json-pretty"] = Flow(json_pretty_flow, name="json-pretty")

    return flows


@app.command("list")
def list_flows() -> None:
    """List all available flows."""

    @inject
    def handle() -> None:
        """Handle the flow listing logic."""
        console = Console()
        flows = get_available_flows()

        if not flows:
            console.print("[yellow]No flows available[/yellow]")
            return

        # Create a rich table
        table = Table(
            title="Available Flows", show_header=True, header_style="bold magenta"
        )
        table.add_column("Name", style="cyan", no_wrap=True)
        table.add_column("Type", style="green")
        table.add_column("Description", style="blue")

        for name, flow in flows.items():
            if name in ["calculator", "echo"]:
                flow_type = "Tool Flow"
                description = f"Flow version of {name} tool"
            elif name == "identity":
                flow_type = "Built-in"
                description = "Identity flow that passes data through unchanged"
            elif name == "json-pretty":
                flow_type = "Built-in"
                description = "Pretty-prints JSON data"
            else:
                flow_type = "Custom"
                description = "Custom flow implementation"

            table.add_row(name, flow_type, description)

        console.print()
        console.print(table)
        console.print()

        # Show usage examples
        console.print(
            Panel.fit(
                "[bold blue]Usage Examples:[/bold blue]\n"
                '• echo \'{"expression": "2+2"}\' | goldentooth-agent flow exec calculator\n'
                '• goldentooth-agent flow exec identity --input \'{"test": "data"}\'\n'
                '• echo \'{"message": "hello"}\' | goldentooth-agent flow exec echo | goldentooth-agent flow exec json-pretty',
                border_style="blue",
                title="🔄 Flow Usage",
            )
        )

    handle()


@app.command("exec")
def exec_flow(
    flow_name: Annotated[str, typer.Argument(help="Name of the flow to execute")],
    input_data: Annotated[
        str | None, typer.Option("--input", help="JSON input data")
    ] = None,
    format: Annotated[
        str, typer.Option("--format", "-f", help="Output format: auto, json, text")
    ] = "auto",
) -> None:
    """Execute a flow with input data."""

    @inject
    def handle() -> None:
        """Handle flow execution."""
        console = Console(file=sys.stderr)  # Error output to stderr
        flows = get_available_flows()

        if flow_name not in flows:
            console.print(f"[red]Error: Flow '{flow_name}' not found[/red]")
            console.print(f"[dim]Available flows: {', '.join(flows.keys())}[/dim]")
            raise typer.Exit(1)

        flow = flows[flow_name]

        # Determine input data
        if input_data:
            # Use provided JSON input
            try:
                input_dict = json.loads(input_data)
            except json.JSONDecodeError as e:
                console.print(f"[red]Error: Invalid JSON input: {e}[/red]")
                raise typer.Exit(1)
        else:
            # Try to read from stdin
            try:
                stdin_data = sys.stdin.read().strip()
                if not stdin_data:
                    console.print("[red]Error: No input provided[/red]")
                    raise typer.Exit(1)

                # Try to parse as JSON
                try:
                    input_dict = json.loads(stdin_data)
                except json.JSONDecodeError as e:
                    console.print(f"[red]Error: Invalid JSON input: {e}[/red]")
                    raise typer.Exit(1)
            except Exception as e:
                console.print(f"[red]Error reading input: {e}[/red]")
                raise typer.Exit(1)

        # Run the flow
        try:
            result = asyncio.run(run_flow_async(flow, input_dict, console))

            # Output result in requested format
            if format == "json" or (format == "auto" and isinstance(result, dict)):
                if hasattr(result, "model_dump"):
                    # Pydantic model
                    output = result.model_dump()
                else:
                    output = result
                print(json.dumps(output))
            elif format == "text" or format == "auto":
                # Auto-format based on result type
                if hasattr(result, "model_dump"):
                    # Pydantic model - print key fields
                    data = result.model_dump()
                    for key, value in data.items():
                        if key not in ["context_data"]:  # Skip internal fields
                            print(f"{key}: {value}")
                elif isinstance(result, dict):
                    # Dictionary - print as JSON or key-value
                    if len(result) == 1:
                        print(list(result.values())[0])
                    else:
                        for key, value in result.items():
                            print(f"{key}: {value}")
                else:
                    print(str(result))
            else:
                console.print(f"[red]Error: Unknown format '{format}'[/red]")
                raise typer.Exit(1)

        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")
            raise typer.Exit(1)

    handle()


async def run_flow_async(
    flow: FlowType, input_dict: InputData, console: Console
) -> StreamData:
    """Run a flow asynchronously."""
    try:
        # Create input stream
        async def input_stream() -> AsyncIterator[InputData]:
            yield input_dict

        # Process and collect results
        results = []
        async for output_data in flow(input_stream()):
            results.append(output_data)

        if results:
            return results[-1]
        else:
            raise RuntimeError("Flow produced no output")

    except Exception as e:
        raise RuntimeError(f"Flow execution failed: {e}") from e


@app.command("describe")
def describe_flow(
    flow_name: Annotated[str, typer.Argument(help="Name of the flow to describe")],
) -> None:
    """Show detailed information about a flow."""

    @inject
    def handle() -> None:
        """Handle flow description."""
        console = Console()
        flows = get_available_flows()

        if flow_name not in flows:
            console.print(f"[red]Error: Flow '{flow_name}' not found[/red]")
            console.print(f"[dim]Available flows: {', '.join(flows.keys())}[/dim]")
            raise typer.Exit(1)

        flow = flows[flow_name]

        # Show flow information
        console.print()
        console.print(
            Panel.fit(
                f"[bold cyan]Flow: {flow_name}[/bold cyan]\n"
                f"[dim]Name: {flow.name}[/dim]",
                border_style="cyan",
                title="📋 Flow Details",
            )
        )

        # If it's a tool flow, show schema information
        tools = get_available_tools()
        if flow_name in tools:
            tool = tools[flow_name]

            console.print("\n[bold blue]Input Schema:[/bold blue]")
            for field_name, field_info in tool.input_schema.model_fields.items():
                field_type = field_info.annotation
                console.print(f"  • {field_name}: {field_type}")

            console.print("\n[bold blue]Output Schema:[/bold blue]")
            for field_name, field_info in tool.output_schema.model_fields.items():
                field_type = field_info.annotation
                console.print(f"  • {field_name}: {field_type}")

            console.print(f"\n[bold blue]Description:[/bold blue] {tool.description}")

        console.print()

    handle()
