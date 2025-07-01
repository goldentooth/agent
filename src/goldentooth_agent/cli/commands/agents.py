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

from goldentooth_agent.cli.commands.chat import create_echo_agent
from goldentooth_agent.core.flow_agent import AgentOutput, FlowAgent, FlowIOSchema
from goldentooth_agent.core.llm import create_claude_agent
from goldentooth_agent.examples.instructor import (
    create_data_extractor_agent,
    create_sentiment_analyzer_agent,
)

app = typer.Typer()

# Type aliases for agent management
AgentRegistry = dict[str, FlowAgent]
AgentMetadata = dict[str, Any]  # Agent metadata can be any type


def get_available_agents() -> AgentRegistry:
    """Get a registry of available agents."""
    agents = {
        "echo": create_echo_agent(),
    }

    # Try to add Claude agent if available
    try:
        agents["claude"] = create_claude_agent(
            name="claude",
            system_prompt="You are a helpful AI assistant.",
        )
    except ValueError:
        # Claude not available (missing API key), skip silently
        pass

    # Try to add Instructor agents if available
    try:
        agents["sentiment"] = create_sentiment_analyzer_agent()
        agents["extractor"] = create_data_extractor_agent()
    except ValueError:
        # Instructor agents not available, skip silently
        pass

    return agents


def get_agent_metadata(agent_name: str, agent: FlowAgent) -> AgentMetadata:
    """Get metadata for an agent."""
    return {
        "name": agent_name,
        "type": "FlowAgent",
        "input_schema": agent.input_schema.__name__,
        "output_schema": agent.output_schema.__name__,
        "system_flow": agent.system_flow.name,
        "processing_flow": agent.processing_flow.name,
        "model": getattr(agent, "model", "default"),
        "description": get_agent_description(agent_name),
    }


def get_agent_description(agent_name: str) -> str:
    """Get a human-readable description for an agent."""
    descriptions = {
        "echo": "Simple echo agent that returns user input with metadata",
        "claude": "AI agent powered by Anthropic's Claude models",
        "sentiment": "Structured sentiment analysis with confidence scores",
        "extractor": "Extract structured person data from text",
    }
    return descriptions.get(agent_name, "Custom agent implementation")


@app.command("list")
def list_agents() -> None:
    """List all available agents and their configurations."""

    @inject
    def handle() -> None:
        """Handle agent listing."""
        console = Console()
        agents = get_available_agents()

        if not agents:
            console.print("[yellow]No agents available[/yellow]")
            return

        # Create a rich table
        table = Table(
            title="Available Agents", show_header=True, header_style="bold magenta"
        )
        table.add_column("Name", style="cyan", no_wrap=True)
        table.add_column("Type", style="green")
        table.add_column("Description", style="blue")
        table.add_column("Input/Output", style="yellow")

        for name, agent in agents.items():
            metadata = get_agent_metadata(name, agent)
            io_info = f"{metadata['input_schema']} → {metadata['output_schema']}"

            table.add_row(name, metadata["type"], metadata["description"], io_info)

        console.print()
        console.print(table)
        console.print()

        # Show usage examples
        console.print(
            Panel.fit(
                "[bold blue]Usage Examples:[/bold blue]\n"
                '• goldentooth-agent agents run echo --input \'{"message": "hello"}\'\n'
                '• echo \'{"message": "test"}\' | goldentooth-agent agents run echo\n'
                '• goldentooth-agent agents test echo --input \'{"message": "sample"}\'',
                border_style="blue",
                title="🤖 Agent Usage",
            )
        )

    handle()


@app.command("describe")
def describe_agent(
    agent_name: Annotated[str, typer.Argument(help="Name of the agent to describe")],
) -> None:
    """Show detailed information about a specific agent."""

    @inject
    def handle() -> None:
        """Handle agent description."""
        console = Console()
        agents = get_available_agents()

        if agent_name not in agents:
            console.print(f"[red]Error: Agent '{agent_name}' not found[/red]")
            console.print(f"[dim]Available agents: {', '.join(agents.keys())}[/dim]")
            raise typer.Exit(1)

        agent = agents[agent_name]
        metadata = get_agent_metadata(agent_name, agent)

        # Show agent information
        console.print()
        console.print(
            Panel.fit(
                f"[bold cyan]Agent: {agent_name}[/bold cyan]\n"
                f"[dim]Type: {metadata['type']}[/dim]\n"
                f"[dim]Model: {metadata['model']}[/dim]",
                border_style="cyan",
                title="🤖 Agent Details",
            )
        )

        console.print(
            f"\n[bold blue]Description:[/bold blue] {metadata['description']}"
        )

        console.print("\n[bold blue]Architecture:[/bold blue]")
        console.print(f"  • System Flow: {metadata['system_flow']}")
        console.print(f"  • Processing Flow: {metadata['processing_flow']}")

        console.print("\n[bold blue]Schema Information:[/bold blue]")
        console.print(f"  • Input Schema: {metadata['input_schema']}")
        console.print(f"  • Output Schema: {metadata['output_schema']}")

        # Show sample input/output
        console.print("\n[bold blue]Sample Usage:[/bold blue]")
        if agent_name == "echo":
            console.print('  Input:  {"message": "Hello, world!"}')
            console.print(
                '  Output: {"response": "Echo: Hello, world!", "metadata": {...}}'
            )

        console.print()

    handle()


@app.command("run")
def run_agent(
    agent_name: Annotated[str, typer.Argument(help="Name of the agent to run")],
    input_data: Annotated[
        str | None, typer.Option("--input", help="JSON input data")
    ] = None,
    format: Annotated[
        str, typer.Option("--format", "-f", help="Output format: text, json")
    ] = "text",
    # Agent-specific options
    message: Annotated[
        str | None,
        typer.Option("--message", help="Message to send (for message-based agents)"),
    ] = None,
) -> None:
    """Run a specific agent with input data."""

    @inject
    def handle() -> None:
        """Handle agent execution."""
        console = Console(file=sys.stderr)  # Error output to stderr
        agents = get_available_agents()

        if agent_name not in agents:
            console.print(f"[red]Error: Agent '{agent_name}' not found[/red]")
            console.print(f"[dim]Available agents: {', '.join(agents.keys())}[/dim]")
            raise typer.Exit(1)

        agent = agents[agent_name]

        # Determine input data
        if input_data:
            # Use provided JSON input
            try:
                input_dict = json.loads(input_data)
            except json.JSONDecodeError as e:
                console.print(f"[red]Error: Invalid JSON input: {e}[/red]")
                raise typer.Exit(1) from None
        elif message:
            # Message shortcut
            input_dict = {"message": message}
        else:
            # Try to read from stdin
            try:
                stdin_data = sys.stdin.read().strip()
                if not stdin_data:
                    console.print("[red]Error: No input provided[/red]")
                    raise typer.Exit(1)

                # Try to parse as JSON first, fall back to message
                try:
                    input_dict = json.loads(stdin_data)
                except json.JSONDecodeError:
                    # Handle plain text input
                    input_dict = {"message": stdin_data}
            except Exception as e:
                console.print(f"[red]Error reading input: {e}[/red]")
                raise typer.Exit(1) from None

        # Run the agent
        try:
            result = asyncio.run(run_agent_async(agent, input_dict, console))

            # Output result in requested format
            if format == "json":
                output = result.model_dump()
                print(json.dumps(output))
            else:
                # Text output
                print(result.response)

        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")
            raise typer.Exit(1) from None

    handle()


@app.command("test")
def test_agent(
    agent_name: Annotated[str, typer.Argument(help="Name of the agent to test")],
    input_data: Annotated[
        str | None,
        typer.Option("--input", help="JSON input data (uses default if not provided)"),
    ] = None,
) -> None:
    """Test an agent with sample input to verify it's working correctly."""

    @inject
    def handle() -> None:
        """Handle agent testing."""
        console = Console()
        agents = get_available_agents()

        if agent_name not in agents:
            console.print(f"[red]Error: Agent '{agent_name}' not found[/red]")
            console.print(f"[dim]Available agents: {', '.join(agents.keys())}[/dim]")
            raise typer.Exit(1)

        agent = agents[agent_name]

        # Use provided input or create default test input
        if input_data:
            try:
                test_input = json.loads(input_data)
            except json.JSONDecodeError as e:
                console.print(f"[red]Error: Invalid JSON input: {e}[/red]")
                raise typer.Exit(1) from None
        else:
            # Default test inputs for different agents
            if agent_name == "echo":
                test_input = {"message": "Test message for echo agent"}
            else:
                test_input = {"message": "Default test message"}

        console.print(f"[bold blue]Testing Agent: {agent_name}[/bold blue]")
        console.print(f"[dim]Input: {json.dumps(test_input)}[/dim]")
        console.print()

        # Run the test
        try:
            with console.status("[dim]🔄 Running agent test...[/dim]"):
                result = asyncio.run(run_agent_async(agent, test_input, console))

            # Display results
            console.print("[bold green]✓ Test Successful[/bold green]")
            console.print(f"[bold blue]Response:[/bold blue] {result.response}")

            if result.metadata:
                console.print("[bold blue]Metadata:[/bold blue]")
                for key, value in result.metadata.items():
                    console.print(f"  • {key}: {value}")

        except Exception as e:
            console.print("[bold red]✗ Test Failed[/bold red]")
            console.print(f"[red]Error: {e}[/red]")
            raise typer.Exit(1) from None

    handle()


async def run_agent_async(
    agent: FlowAgent, input_dict: dict[str, Any], console: Console
) -> AgentOutput:
    """Run an agent asynchronously."""
    try:
        # Validate and create input
        input_data = agent.input_schema.model_validate(input_dict)

        # Convert agent to flow and execute
        agent_flow = agent.as_flow()

        # Create input stream
        async def input_stream() -> AsyncIterator[FlowIOSchema]:
            yield input_data

        # Process and collect results
        results = []
        async for output_data in agent_flow(input_stream()):
            results.append(output_data)

        if results:
            # Cast to AgentOutput since FlowAgent guarantees this type
            result = results[-1]
            if isinstance(result, AgentOutput):
                return result
            else:
                # This shouldn't happen with standard agents, but handle gracefully
                raise RuntimeError(f"Agent returned unexpected type: {type(result)}")
        else:
            raise RuntimeError("Agent produced no output")

    except Exception as e:
        raise RuntimeError(f"Agent execution failed: {e}") from e
