from __future__ import annotations

import asyncio
import json
import time
from collections.abc import AsyncIterator
from typing import Annotated, Any

import typer
from antidote import inject
from rich.console import Console
from rich.panel import Panel
from rich.progress import BarColumn, Progress, TextColumn, TimeElapsedColumn
from rich.prompt import Confirm, Prompt
from rich.table import Table

from goldentooth_agent.cli.commands.agents import get_available_agents
from goldentooth_agent.cli.commands.flow import get_available_flows
from goldentooth_agent.core.context import Context
from goldentooth_agent.core.flow_agent import AgentInput

app = typer.Typer()


@app.command("flows")
def demo_flows(
    scenario: Annotated[
        str | None,
        typer.Option(
            "--scenario",
            help="Specific scenario: stream_processing, error_handling, composition",
        ),
    ] = None,
    interactive: Annotated[
        bool,
        typer.Option("--interactive/--no-interactive", help="Enable interactive mode"),
    ] = True,
) -> None:
    """Interactive demonstration of the flow system."""

    @inject
    def handle() -> None:
        """Handle flow demonstration."""
        console = Console()

        console.print()
        console.print(
            Panel.fit(
                "[bold blue]🔄 Flow System Demonstration[/bold blue]\n"
                "[dim]Learn about the Goldentooth Agent flow architecture through interactive examples[/dim]",
                border_style="blue",
                title="📚 Flow Demo",
            )
        )

        if scenario:
            run_flow_scenario(console, scenario, interactive)
        else:
            run_interactive_flow_tutorial(console, interactive)

    handle()


@app.command("context")
def demo_context(
    scenario: Annotated[
        str | None,
        typer.Option(
            "--scenario",
            help="Specific scenario: time_travel, computed_properties, queries",
        ),
    ] = None,
    interactive: Annotated[
        bool,
        typer.Option("--interactive/--no-interactive", help="Enable interactive mode"),
    ] = True,
) -> None:
    """Interactive demonstration of the context system."""

    @inject
    def handle() -> None:
        """Handle context demonstration."""
        console = Console()

        console.print()
        console.print(
            Panel.fit(
                "[bold blue]🧠 Context System Demonstration[/bold blue]\n"
                "[dim]Explore the sophisticated context management capabilities[/dim]",
                border_style="blue",
                title="📚 Context Demo",
            )
        )

        if scenario:
            run_context_scenario(console, scenario, interactive)
        else:
            run_interactive_context_tutorial(console, interactive)

    handle()


@app.command("agents")
def demo_agents(
    scenario: Annotated[
        str | None,
        typer.Option(
            "--scenario", help="Specific scenario: creation, collaboration, pipelines"
        ),
    ] = None,
    interactive: Annotated[
        bool,
        typer.Option("--interactive/--no-interactive", help="Enable interactive mode"),
    ] = True,
) -> None:
    """Interactive demonstration of the agent system."""

    @inject
    def handle() -> None:
        """Handle agent demonstration."""
        console = Console()

        console.print()
        console.print(
            Panel.fit(
                "[bold blue]🤖 Agent System Demonstration[/bold blue]\n"
                "[dim]Discover how to create and use intelligent agents[/dim]",
                border_style="blue",
                title="📚 Agent Demo",
            )
        )

        if scenario:
            run_agent_scenario(console, scenario, interactive)
        else:
            run_interactive_agent_tutorial(console, interactive)

    handle()


def run_interactive_flow_tutorial(console: Console, interactive: bool) -> None:
    """Run the interactive flow tutorial."""
    console.print("\n[bold blue]Available Demo Scenarios:[/bold blue]")
    console.print(
        "1. [cyan]stream_processing[/cyan] - Data flow through processing pipelines"
    )
    console.print("2. [cyan]error_handling[/cyan] - Graceful error handling in flows")
    console.print(
        "3. [cyan]composition[/cyan] - Composing complex flows from simple ones"
    )

    if interactive:
        console.print()
        choice = Prompt.ask(
            "Choose a scenario (1-3) or 'all' for complete tutorial",
            choices=["1", "2", "3", "all"],
            default="all",
        )

        scenario_map = {
            "1": "stream_processing",
            "2": "error_handling",
            "3": "composition",
        }

        if choice == "all":
            for scenario in scenario_map.values():
                run_flow_scenario(console, scenario, interactive)
                if interactive is True and scenario != "composition":  # type: ignore[redundant-expr]
                    if not Confirm.ask("\nContinue to next scenario?"):
                        break
        else:
            run_flow_scenario(console, scenario_map[choice], interactive)
    else:
        # Non-interactive: run all scenarios
        for scenario in ["stream_processing", "error_handling", "composition"]:
            run_flow_scenario(console, scenario, False)


def run_flow_scenario(console: Console, scenario: str, interactive: bool) -> None:
    """Run a specific flow scenario."""
    console.print(
        f"\n[bold blue]Scenario: {scenario.replace('_', ' ').title()}[/bold blue]"
    )

    if scenario == "stream_processing":
        demo_stream_processing(console, interactive)
    elif scenario == "error_handling":
        demo_error_handling(console, interactive)
    elif scenario == "composition":
        demo_flow_composition(console, interactive)
    else:
        console.print(f"[red]Unknown scenario: {scenario}[/red]")


def demo_stream_processing(console: Console, interactive: bool) -> None:
    """Demonstrate stream processing capabilities."""
    console.print(
        "\n[dim]This demo shows how data flows through processing pipelines...[/dim]"
    )

    # Show available flows
    flows = get_available_flows()

    console.print("\n[bold blue]Available Flows:[/bold blue]")
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Flow", style="cyan")
    table.add_column("Purpose", style="green")

    for name, _ in flows.items():
        purpose = {
            "calculator": "Mathematical computations",
            "echo": "Message echoing with metadata",
            "identity": "Pass-through (no transformation)",
            "json-pretty": "JSON formatting and prettification",
        }.get(name, "Custom processing")

        table.add_row(name, purpose)

    console.print(table)

    if interactive:
        console.print("\n[bold blue]Live Demo:[/bold blue]")
        if Confirm.ask("Would you like to see a live stream processing example?"):
            asyncio.run(demo_live_stream_processing(console))


async def demo_live_stream_processing(console: Console) -> None:
    """Demonstrate live stream processing."""
    flows = get_available_flows()
    calculator_flow = flows["calculator"]

    # Demo data
    expressions = ["2+2", "sqrt(16)", "sin(pi/2)", "pow(2,3)", "log(e)"]

    console.print(
        "\n[dim]Processing mathematical expressions through calculator flow...[/dim]"
    )

    with Progress(
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TimeElapsedColumn(),
        console=console,
    ) as progress:

        task = progress.add_task("Processing expressions...", total=len(expressions))

        for expr in expressions:
            # Create input stream (capture expr in closure)
            async def input_stream(
                expression: str = expr,
            ) -> AsyncIterator[dict[str, str]]:
                yield {"expression": expression}

            # Process through flow
            async for result in calculator_flow(input_stream()):
                console.print(f"  {expr} = [green]{result.result}[/green]")
                await asyncio.sleep(0.5)  # Simulate processing time

            progress.update(task, advance=1)


def demo_error_handling(console: Console, interactive: bool) -> None:
    """Demonstrate error handling in flows."""
    console.print("\n[dim]This demo shows how flows handle errors gracefully...[/dim]")

    if interactive:
        console.print("\n[bold blue]Error Handling Demo:[/bold blue]")
        if Confirm.ask("Would you like to see error handling in action?"):
            asyncio.run(demo_live_error_handling(console))


async def demo_live_error_handling(console: Console) -> None:
    """Demonstrate live error handling."""
    flows = get_available_flows()
    calculator_flow = flows["calculator"]

    # Demo data with intentional errors
    expressions = ["2+2", "invalid_expr", "1/0", "sqrt(-1)", "normal_calc"]

    console.print(
        "\n[dim]Testing calculator flow with various inputs (including errors)...[/dim]"
    )

    for expr in expressions:
        try:

            async def input_stream(
                expression: str = expr,
            ) -> AsyncIterator[dict[str, str]]:
                yield {"expression": expression}

            console.print(f"\n[blue]Input:[/blue] {expr}")

            async for result in calculator_flow(input_stream()):
                if "Error:" in result.result:
                    console.print(f"[red]Result: {result.result}[/red]")
                else:
                    console.print(f"[green]Result: {result.result}[/green]")

            await asyncio.sleep(0.3)

        except Exception as e:
            console.print(f"[red]Exception: {e}[/red]")


def demo_flow_composition(console: Console, interactive: bool) -> None:
    """Demonstrate flow composition."""
    console.print(
        "\n[dim]This demo shows how to compose complex workflows from simple flows...[/dim]"
    )

    if interactive:
        console.print("\n[bold blue]Flow Composition Demo:[/bold blue]")
        if Confirm.ask("Would you like to see flow composition in action?"):
            asyncio.run(demo_live_composition(console))


async def demo_live_composition(console: Console) -> None:
    """Demonstrate live flow composition."""
    flows = get_available_flows()

    console.print("\n[dim]Composing: Calculator → JSON Pretty Printer...[/dim]")

    # Simulate composed pipeline
    input_data = {"expression": "sqrt(pow(3,2) + pow(4,2))"}

    console.print(f"\n[blue]1. Input:[/blue] {json.dumps(input_data)}")

    # Step 1: Calculator
    async def calc_stream() -> AsyncIterator[dict[str, str]]:
        yield input_data

    calc_results = []
    async for result in flows["calculator"](calc_stream()):
        calc_results.append(result)
        console.print(f"[blue]2. Calculator Output:[/blue] {result.model_dump()}")

    await asyncio.sleep(0.5)

    # Step 2: JSON Pretty
    async def pretty_stream() -> AsyncIterator[dict[str, Any]]:
        yield calc_results[0].model_dump()

    async for result in flows["json-pretty"](pretty_stream()):
        console.print("[blue]3. Pretty JSON Output:[/blue]")
        console.print(result)


def run_interactive_context_tutorial(console: Console, interactive: bool) -> None:
    """Run the interactive context tutorial."""
    console.print("\n[bold blue]Context System Features:[/bold blue]")
    console.print("• Key-value storage with type safety")
    console.print("• Computed properties and transformations")
    console.print("• History tracking and snapshots")
    console.print("• Event-driven updates")
    console.print("• Query capabilities")

    demo_basic_context_operations(console, interactive)


def demo_basic_context_operations(console: Console, interactive: bool) -> None:
    """Demonstrate basic context operations."""
    console.print("\n[bold blue]Basic Context Operations:[/bold blue]")

    # Create and populate a context
    context = Context()

    console.print("\n[dim]Creating and populating a context...[/dim]")

    operations = [
        ("Setting user data", lambda: context.set("user_name", "Alice")),
        ("Setting session info", lambda: context.set("session_id", "demo_123")),
        (
            "Setting config",
            lambda: context.set("config", {"theme": "dark", "lang": "en"}),
        ),
        ("Setting counter", lambda: context.set("message_count", 0)),
    ]

    for desc, operation in operations:
        console.print(f"  • {desc}")
        operation()  # type: ignore[no-untyped-call]  # Lambda operations are simple
        if interactive:
            time.sleep(0.3)

    # Show context contents
    console.print("\n[bold blue]Context Contents:[/bold blue]")
    for key in context.keys():
        value = context.get(key)
        console.print(f"  • [cyan]{key}[/cyan]: {value} ({type(value).__name__})")

    if interactive:
        console.print("\n[bold blue]Context Queries:[/bold blue]")
        console.print(f"  • Total keys: {len(list(context.keys()))}")
        console.print(
            f"  • Has user_name: {'user_name' in context.keys()}"
        )  # Context doesn't have 'has' method
        console.print(f"  • User name: {context.get('user_name', 'Unknown')}")


def run_context_scenario(console: Console, scenario: str, interactive: bool) -> None:
    """Run a specific context scenario."""
    console.print(
        f"\n[bold blue]Context Scenario: {scenario.replace('_', ' ').title()}[/bold blue]"
    )

    if scenario == "time_travel":
        console.print(
            "[yellow]Time travel debugging not yet implemented in this demo[/yellow]"
        )
    elif scenario == "computed_properties":
        console.print(
            "[yellow]Computed properties not yet implemented in this demo[/yellow]"
        )
    elif scenario == "queries":
        demo_basic_context_operations(console, interactive)
    else:
        console.print(f"[red]Unknown scenario: {scenario}[/red]")


def run_interactive_agent_tutorial(console: Console, interactive: bool) -> None:
    """Run the interactive agent tutorial."""
    console.print("\n[bold blue]Agent System Overview:[/bold blue]")
    console.print("• Flow-based architecture")
    console.print("• Schema-driven input/output")
    console.print("• Composable system and processing flows")
    console.print("• Context integration")

    demo_agent_basics(console, interactive)


def demo_agent_basics(console: Console, interactive: bool) -> None:
    """Demonstrate basic agent operations."""
    agents = get_available_agents()

    console.print("\n[bold blue]Available Agents:[/bold blue]")
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Agent", style="cyan")
    table.add_column("Type", style="green")
    table.add_column("Description", style="blue")

    for name, _ in agents.items():
        table.add_row(
            name, "FlowAgent", "Simple echo agent that returns user input with metadata"
        )

    console.print(table)

    if interactive:
        console.print("\n[bold blue]Agent Interaction Demo:[/bold blue]")
        if Confirm.ask("Would you like to interact with an agent?"):
            asyncio.run(demo_agent_interaction(console))


async def demo_agent_interaction(console: Console) -> None:
    """Demonstrate agent interaction."""
    agents = get_available_agents()
    echo_agent = agents["echo"]

    messages = [
        "Hello, agent!",
        "How are you today?",
        "Can you echo this message?",
        "Testing agent capabilities",
    ]

    console.print("\n[dim]Interacting with echo agent...[/dim]")

    for i, message in enumerate(messages, 1):
        console.print(f"\n[blue]Message {i}:[/blue] {message}")

        # Create input using the agent's input schema
        agent_input_data = echo_agent.input_schema.model_validate(
            {"message": message, "context_data": {}}
        )
        agent_input = AgentInput.model_validate(agent_input_data.model_dump())

        # Process through agent
        agent_flow = echo_agent.as_flow()

        async def input_stream(
            input_data: AgentInput = agent_input,
        ) -> AsyncIterator[AgentInput]:
            yield input_data

        async for result in agent_flow(input_stream()):
            # Cast result to AgentOutput for type safety
            if hasattr(result, "response"):
                console.print(f"[green]Response:[/green] {result.response}")
            if hasattr(result, "metadata") and result.metadata:
                metadata_str = " | ".join(
                    [f"{k}: {v}" for k, v in result.metadata.items()]
                )
                console.print(f"[dim]Metadata: {metadata_str}[/dim]")

        await asyncio.sleep(0.5)


def run_agent_scenario(console: Console, scenario: str, interactive: bool) -> None:
    """Run a specific agent scenario."""
    console.print(
        f"\n[bold blue]Agent Scenario: {scenario.replace('_', ' ').title()}[/bold blue]"
    )

    if scenario == "creation":
        demo_agent_basics(console, interactive)
    elif scenario == "collaboration":
        console.print(
            "[yellow]Multi-agent collaboration not yet implemented in this demo[/yellow]"
        )
    elif scenario == "pipelines":
        console.print(
            "[yellow]Agent pipelines not yet implemented in this demo[/yellow]"
        )
    else:
        console.print(f"[red]Unknown scenario: {scenario}[/red]")
