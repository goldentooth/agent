import asyncio
import json
import math
import sys
from collections.abc import AsyncIterator
from typing import Any

import typer
from antidote import inject
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from goldentooth_agent.core.flow_agent import FlowIOSchema, FlowTool

app = typer.Typer()

# Type aliases for CLI flexibility
ToolInputData = Any  # type: ignore[explicit-any]  # Input can be any JSON-serializable data
ToolOutputData = FlowIOSchema  # Tool output is always a FlowIOSchema


# Tool implementations - using the examples as reference
class CalculatorInput(FlowIOSchema):  # type: ignore[explicit-any]
    """Input schema for calculator tool."""

    expression: str


class CalculatorOutput(FlowIOSchema):  # type: ignore[explicit-any]
    """Output schema for calculator tool."""

    result: str
    expression: str


class EchoInput(FlowIOSchema):  # type: ignore[explicit-any]
    """Input schema for echo tool."""

    message: str


class EchoOutput(FlowIOSchema):  # type: ignore[explicit-any]
    """Output schema for echo tool."""

    echoed_message: str


def calculator_implementation(input_data: CalculatorInput) -> CalculatorOutput:
    """Calculate mathematical expressions safely."""
    try:
        # Safe evaluation with limited functions
        allowed_names = {
            "abs": abs,
            "round": round,
            "min": min,
            "max": max,
            "sqrt": math.sqrt,
            "sin": math.sin,
            "cos": math.cos,
            "tan": math.tan,
            "log": math.log,
            "log10": math.log10,
            "exp": math.exp,
            "pow": pow,
            "pi": math.pi,
            "e": math.e,
        }

        result = eval(input_data.expression, {"__builtins__": {}}, allowed_names)
        return CalculatorOutput(result=str(result), expression=input_data.expression)
    except Exception as e:
        return CalculatorOutput(
            result=f"Error: {str(e)}", expression=input_data.expression
        )


def echo_implementation(input_data: EchoInput) -> EchoOutput:
    """Echo back the input message."""
    return EchoOutput(echoed_message=input_data.message)


def get_available_tools() -> dict[str, FlowTool]:
    """Get a registry of available tools."""
    return {
        "calculator": FlowTool(
            name="calculator",
            input_schema=CalculatorInput,
            output_schema=CalculatorOutput,
            implementation=calculator_implementation,
            description="Safe mathematical calculator supporting basic arithmetic, trigonometry, and common functions",
        ),
        "echo": FlowTool(
            name="echo",
            input_schema=EchoInput,
            output_schema=EchoOutput,
            implementation=echo_implementation,
            description="Echo tool that returns the input message",
        ),
    }


@app.command("list")
def list_tools() -> None:
    """List all available tools and their descriptions."""

    @inject
    def handle() -> None:
        """Handle the tool listing logic."""
        console = Console()
        tools = get_available_tools()

        if not tools:
            console.print("[yellow]No tools available[/yellow]")
            return

        # Create a rich table
        table = Table(
            title="Available Tools", show_header=True, header_style="bold magenta"
        )
        table.add_column("Name", style="cyan", no_wrap=True)
        table.add_column("Description", style="green")
        table.add_column("Input Schema", style="blue")
        table.add_column("Output Schema", style="yellow")

        for name, tool in tools.items():
            # Get schema field info
            input_fields = list(tool.input_schema.model_fields.keys())
            output_fields = list(tool.output_schema.model_fields.keys())

            table.add_row(
                name,
                tool.description,
                ", ".join(input_fields),
                ", ".join(output_fields),
            )

        console.print()
        console.print(table)
        console.print()

        # Show usage examples
        console.print(
            Panel.fit(
                "[bold blue]Usage Examples:[/bold blue]\n"
                "• goldentooth-agent tools run calculator --expression '2 + 2'\n"
                "• echo 'Hello World' | goldentooth-agent tools run echo\n"
                '• goldentooth-agent tools run calculator --input \'{"expression": "sqrt(16)"}\' --format json',
                border_style="blue",
                title="🔧 Tool Usage",
            )
        )

    handle()


@app.command("run")
def run_tool(
    tool_name: str = typer.Argument(..., help="Name of the tool to run"),
    input_data: str | None = typer.Option(None, "--input", help="JSON input data"),
    format: str = typer.Option(
        "text", "--format", "-f", help="Output format: text, json"
    ),
    # Tool-specific options
    expression: str | None = typer.Option(
        None, "--expression", help="Mathematical expression (for calculator)"
    ),
    message: str | None = typer.Option(
        None, "--message", help="Message to echo (for echo tool)"
    ),
) -> None:
    """Run a specific tool with input data."""

    @inject
    def handle() -> None:
        """Handle tool execution."""
        console = Console(file=sys.stderr)  # Error output to stderr
        tools = get_available_tools()

        if tool_name not in tools:
            console.print(f"[red]Error: Tool '{tool_name}' not found[/red]")
            console.print(f"[dim]Available tools: {', '.join(tools.keys())}[/dim]")
            raise typer.Exit(1)

        tool = tools[tool_name]

        # Determine input data
        if input_data:
            # Use provided JSON input
            try:
                input_dict = json.loads(input_data)
            except json.JSONDecodeError as e:
                console.print(f"[red]Error: Invalid JSON input: {e}[/red]")
                raise typer.Exit(1)
        elif tool_name == "calculator" and expression:
            # Calculator-specific shortcut
            input_dict = {"expression": expression}
        elif tool_name == "echo" and message:
            # Echo-specific shortcut
            input_dict = {"message": message}
        else:
            # Try to read from stdin
            try:
                stdin_data = sys.stdin.read().strip()
                if not stdin_data:
                    console.print("[red]Error: No input provided[/red]")
                    raise typer.Exit(1)

                # Try to parse as JSON first, fall back to tool-specific handling
                try:
                    input_dict = json.loads(stdin_data)
                except json.JSONDecodeError:
                    # Handle plain text input for specific tools
                    if tool_name == "calculator":
                        input_dict = {"expression": stdin_data}
                    elif tool_name == "echo":
                        input_dict = {"message": stdin_data}
                    else:
                        console.print(
                            f"[red]Error: Invalid input format for tool '{tool_name}'[/red]"
                        )
                        raise typer.Exit(1)
            except Exception as e:
                console.print(f"[red]Error reading input: {e}[/red]")
                raise typer.Exit(1)

        # Run the tool
        try:
            result = asyncio.run(run_tool_async(tool, input_dict, console))

            # Output result in requested format
            if format == "json":
                output = result.model_dump()
                print(json.dumps(output))
            else:
                # Tool-specific text output
                if tool_name == "calculator":
                    calculator_result = result
                    print(calculator_result.result)  # type: ignore[attr-defined]  # CalculatorOutput has result
                elif tool_name == "echo":
                    echo_result = result
                    print(echo_result.echoed_message)  # type: ignore[attr-defined]  # EchoOutput has echoed_message
                else:
                    # Generic output - print all fields
                    for field, value in result.model_dump().items():
                        if field != "context_data":  # Skip internal fields
                            print(f"{field}: {value}")

        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")
            raise typer.Exit(1)

    handle()


async def run_tool_async(
    tool: FlowTool, input_dict: dict[str, ToolInputData], console: Console
) -> ToolOutputData:
    """Run a tool asynchronously."""
    try:
        # Validate input
        input_data = tool.input_schema.model_validate(input_dict)

        # Convert tool to flow and execute
        tool_flow = tool.as_flow()

        # Create input stream
        async def input_stream() -> AsyncIterator[FlowIOSchema]:
            yield input_data

        # Process and collect results
        results = []
        async for output_data in tool_flow(input_stream()):
            results.append(output_data)

        if results:
            return results[-1]  # type: ignore[no-any-return]  # FlowTool guarantees FlowIOSchema output
        else:
            raise RuntimeError("Tool produced no output")

    except Exception as e:
        raise RuntimeError(f"Tool execution failed: {e}") from e
