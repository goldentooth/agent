"""CLI commands for Instructor structured output demonstrations."""

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
from rich.syntax import Syntax
from rich.table import Table

from goldentooth_agent.core.flow_agent import AgentInput, FlowIOSchema
from goldentooth_agent.examples.instructor import (
    CodeAnalysis,
    PersonData,
    Recipe,
    SentimentAnalysis,
    TaskList,
    create_code_reviewer_agent,
    create_data_extractor_agent,
    create_recipe_generator_agent,
    create_sentiment_analyzer_agent,
    create_task_planner_agent,
)

app = typer.Typer()


def get_available_instructor_agents() -> dict[str, Any]:
    """Get available Instructor-powered agents."""
    return {
        "sentiment": {
            "factory": create_sentiment_analyzer_agent,
            "description": "Analyze sentiment with confidence scores and reasoning",
            "example": "I love this new feature! It's absolutely amazing.",
        },
        "extractor": {
            "factory": create_data_extractor_agent,
            "description": "Extract structured person data from text",
            "example": "John Smith is a 30-year-old software engineer from San Francisco. He specializes in Python and machine learning. Contact him at john@example.com.",
        },
        "planner": {
            "factory": create_task_planner_agent,
            "description": "Break down projects into structured task lists",
            "example": "Build a personal blog website with user authentication and a content management system",
        },
        "reviewer": {
            "factory": create_code_reviewer_agent,
            "description": "Perform structured code analysis and review",
            "example": "def factorial(n):\\n    if n == 0:\\n        return 1\\n    return n * factorial(n-1)",
        },
        "chef": {
            "factory": create_recipe_generator_agent,
            "description": "Generate structured recipes with ingredients and instructions",
            "example": "chocolate chip cookies",
        },
    }


@app.command("list")
def list_instructor_agents() -> None:
    """List all available Instructor-powered agents."""

    @inject
    def handle() -> None:
        """Handle agent listing."""
        console = Console()
        agents = get_available_instructor_agents()

        if not agents:
            console.print("[yellow]No Instructor agents available[/yellow]")
            return

        # Create a rich table
        table = Table(
            title="Instructor Agents (Structured Output)",
            show_header=True,
            header_style="bold magenta",
        )
        table.add_column("Agent", style="cyan", no_wrap=True)
        table.add_column("Description", style="green")
        table.add_column("Output Type", style="blue")

        for name, info in agents.items():
            # Get output schema from agent factory
            try:
                agent = info["factory"]()
                output_type = agent.output_schema.__name__
            except Exception:
                output_type = "StructuredOutput"

            table.add_row(name, info["description"], output_type)

        console.print()
        console.print(table)
        console.print()

        # Show usage examples
        console.print(
            Panel.fit(
                "[bold blue]Usage Examples:[/bold blue]\\n"
                "• goldentooth-agent instructor run sentiment --text 'I love this!'\\n"
                "• goldentooth-agent instructor run extractor --text 'John is a developer'\\n"
                "• goldentooth-agent instructor demo sentiment",
                border_style="blue",
                title="🧠 Instructor Usage",
            )
        )

    handle()


@app.command("run")
def run_instructor_agent(
    agent_name: Annotated[
        str, typer.Argument(help="Name of the Instructor agent to run")
    ],
    text: Annotated[
        str | None, typer.Option("--text", help="Input text to analyze")
    ] = None,
    input_data: Annotated[
        str | None, typer.Option("--input", help="JSON input data")
    ] = None,
    format: Annotated[
        str, typer.Option("--format", "-f", help="Output format: json, rich")
    ] = "rich",
) -> None:
    """Run an Instructor agent with structured output."""

    @inject
    def handle() -> None:
        """Handle instructor agent execution."""
        console = Console(file=sys.stderr)  # Error output to stderr
        agents = get_available_instructor_agents()

        if agent_name not in agents:
            console.print(
                f"[red]Error: Instructor agent '{agent_name}' not found[/red]"
            )
            console.print(f"[dim]Available agents: {', '.join(agents.keys())}[/dim]")
            raise typer.Exit(1)

        agent_info = agents[agent_name]

        # Determine input text
        if input_data:
            try:
                input_dict = json.loads(input_data)
                message = input_dict.get("message", "")
            except json.JSONDecodeError as e:
                console.print(f"[red]Error: Invalid JSON input: {e}[/red]")
                raise typer.Exit(1)
        elif text:
            message = text
        else:
            # Try to read from stdin
            try:
                stdin_data = sys.stdin.read().strip()
                if not stdin_data:
                    console.print("[red]Error: No input provided[/red]")
                    raise typer.Exit(1)
                message = stdin_data
            except Exception as e:
                console.print(f"[red]Error reading input: {e}[/red]")
                raise typer.Exit(1)

        # Run the instructor agent
        try:
            result = asyncio.run(
                run_instructor_agent_async(agent_info["factory"](), message, console)
            )

            # Output result in requested format
            if format == "json":
                output = result.model_dump()
                print(json.dumps(output, indent=2))
            else:
                # Rich format - show structured output nicely
                display_structured_result(console, result, agent_name)

        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")
            raise typer.Exit(1)

    handle()


@app.command("demo")
def demo_instructor_agent(
    agent_name: Annotated[
        str | None, typer.Argument(help="Agent to demo (or 'all' for all agents)")
    ] = None,
) -> None:
    """Run demonstration of Instructor agents with example inputs."""

    @inject
    def handle() -> None:
        """Handle instructor demonstration."""
        console = Console()
        agents = get_available_instructor_agents()

        if agent_name and agent_name not in agents and agent_name != "all":
            console.print(f"[red]Error: Agent '{agent_name}' not found[/red]")
            console.print(f"[dim]Available agents: {', '.join(agents.keys())}[/dim]")
            raise typer.Exit(1)

        # Show intro
        console.print()
        console.print(
            Panel.fit(
                "[bold blue]🧠 Instructor Structured Output Demo[/bold blue]\\n"
                "[dim]Demonstrating Claude + Instructor for structured AI responses[/dim]",
                border_style="blue",
                title="📚 Structured AI",
            )
        )

        agents_to_demo = (
            [agent_name] if agent_name and agent_name != "all" else list(agents.keys())
        )

        for i, name in enumerate(agents_to_demo):
            if i > 0:
                console.print("\\n" + "─" * 80 + "\\n")

            try:
                agent_info = agents[name]
                console.print(f"[bold blue]🤖 {name.title()} Agent[/bold blue]")
                console.print(f"[dim]{agent_info['description']}[/dim]")

                console.print(f"\\n[bold]Example Input:[/bold] {agent_info['example']}")

                with console.status(f"[dim]Running {name} agent...[/dim]"):
                    result = asyncio.run(
                        run_instructor_agent_async(
                            agent_info["factory"](), agent_info["example"], console
                        )
                    )

                console.print("\\n[bold]Structured Output:[/bold]")
                display_structured_result(console, result, name)

            except Exception as e:
                console.print(f"[red]Error with {name} agent: {e}[/red]")

        console.print("\\n[green]✓ Instructor demonstration complete![/green]")

    handle()


async def run_instructor_agent_async(
    agent: Any, message: str, console: Console
) -> FlowIOSchema:
    """Run an instructor agent asynchronously."""
    try:
        # Create input
        input_data = AgentInput(message=message, context_data={"instructor_demo": True})

        # Convert agent to flow and execute
        agent_flow = agent.as_flow()

        # Create input stream
        async def input_stream() -> AsyncIterator[AgentInput]:
            yield input_data

        # Process and collect results
        results = []
        async for output_data in agent_flow(input_stream()):
            results.append(output_data)

        if results:
            return results[-1]  # type: ignore[return-value]
        else:
            raise RuntimeError("Instructor agent produced no output")

    except Exception as e:
        raise RuntimeError(f"Instructor agent execution failed: {e}") from e


def display_structured_result(
    console: Console, result: FlowIOSchema, agent_type: str
) -> None:
    """Display structured result in a nice format."""
    try:
        data = result.model_dump()

        # Remove context_data for cleaner display
        if "context_data" in data:
            del data["context_data"]

        # Create JSON syntax highlighting
        json_str = json.dumps(data, indent=2)
        syntax = Syntax(json_str, "json", theme="monokai", line_numbers=False)

        console.print(syntax)

        # Show specific highlights based on agent type
        if agent_type == "sentiment" and isinstance(result, SentimentAnalysis):
            sentiment_color = {
                "positive": "green",
                "negative": "red",
                "neutral": "yellow",
            }.get(result.sentiment, "white")
            console.print(
                f"\\n[bold]Quick Summary:[/bold] [{sentiment_color}]{result.sentiment.upper()}[/{sentiment_color}] "
                f"(confidence: {result.confidence:.1%})"
            )

        elif agent_type == "planner" and isinstance(result, TaskList):
            console.print(
                f"\\n[bold]Quick Summary:[/bold] {len(result.tasks)} tasks planned"
            )

        elif agent_type == "reviewer" and isinstance(result, CodeAnalysis):
            quality_color = (
                "green"
                if result.overall_quality >= 7
                else "yellow" if result.overall_quality >= 4 else "red"
            )
            console.print(
                f"\\n[bold]Quick Summary:[/bold] Quality score [{quality_color}]{result.overall_quality}/10[/{quality_color}]"
            )

        elif agent_type == "extractor" and isinstance(result, PersonData):
            console.print(
                f"\\n[bold]Quick Summary:[/bold] Extracted data for {result.name}"
            )

        elif agent_type == "chef" and isinstance(result, Recipe):
            console.print(
                f"\\n[bold]Quick Summary:[/bold] {result.name} ({result.servings} servings, {result.difficulty})"
            )

    except Exception as e:
        # Fallback to simple display
        console.print(f"[yellow]Display error: {e}[/yellow]")
        console.print(str(result))
