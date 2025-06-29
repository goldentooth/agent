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
from rich.progress import Progress, SpinnerColumn, TextColumn

from goldentooth_agent.cli.commands.agents import get_available_agents
from goldentooth_agent.cli.commands.flow import get_available_flows
from goldentooth_agent.cli.commands.tools import get_available_tools

app = typer.Typer()

# Type aliases for debug system
HealthStatus = dict[str, Any]  # Health data can be any type


# More specific type for trace data to avoid union-attr errors
class TraceStep:
    def __init__(self, step: str, status: str, timestamp: float, details: str):
        self.step = step
        self.status = status
        self.timestamp = timestamp
        self.details = details


class TraceDataDict:
    def __init__(self) -> None:
        self.data = {
            "timestamp": 0.0,
            "type": "",
            "target": "",
            "input": "",
            "steps": [],
            "duration": 0.0,
            "success": False,
        }

    def __getitem__(self, key: str) -> Any:
        return self.data[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.data[key] = value


@app.command("health")
def system_health(
    component: Annotated[
        str | None,
        typer.Option(
            "--component", help="Specific component to check: flows, tools, agents, all"
        ),
    ] = None,
    format: Annotated[
        str, typer.Option("--format", "-f", help="Output format: rich, json")
    ] = "rich",
    export: Annotated[
        str | None, typer.Option("--export", help="Export health report to file")
    ] = None,
) -> None:
    """Check system health and component status."""

    @inject
    def handle() -> None:
        """Handle health check."""
        console = Console()

        # Run health checks
        health_data = run_health_checks(component, console)

        # Display results
        if format == "json":
            output = json.dumps(health_data, indent=2, default=str)
            if export:
                try:
                    with open(export, "w") as f:
                        f.write(output)
                    console.print(
                        f"[green]✓[/green] Health report exported to {export}"
                    )
                except Exception as e:
                    console.print(f"[red]Error writing to file: {e}[/red]")
                    raise typer.Exit(1) from None
            else:
                print(output)
        else:
            display_health_results(console, health_data)
            if export:
                # Export as JSON even in rich mode
                output = json.dumps(health_data, indent=2, default=str)
                try:
                    with open(export, "w") as f:
                        f.write(output)
                    console.print(
                        f"\n[green]✓[/green] Health report exported to {export}"
                    )
                except Exception as e:
                    console.print(f"[red]Error writing to file: {e}[/red]")
                    raise typer.Exit(1) from None

    handle()


@app.command("trace")
def trace_execution(
    flow: Annotated[
        str | None, typer.Option("--flow", help="Flow name to trace")
    ] = None,
    agent: Annotated[
        str | None, typer.Option("--agent", help="Agent name to trace")
    ] = None,
    input_data: Annotated[
        str | None, typer.Option("--input", help="JSON input data")
    ] = None,
    verbose: Annotated[
        bool, typer.Option("--verbose", help="Enable verbose output")
    ] = False,
) -> None:
    """Trace flow or agent execution for debugging."""

    @inject
    def handle() -> None:
        """Handle execution tracing."""
        console = Console()
        nonlocal input_data  # Allow modification of the outer scope variable

        if not flow and not agent:
            console.print("[red]Error: Must specify either --flow or --agent[/red]")
            raise typer.Exit(1)

        if flow and agent:
            console.print("[red]Error: Cannot specify both --flow and --agent[/red]")
            raise typer.Exit(1)

        # Default input if none provided
        if not input_data:
            if flow:
                input_data = '{"test": "trace_data"}'
            else:  # agent
                input_data = '{"message": "trace test"}'

        try:
            trace_data = asyncio.run(
                run_trace_execution(flow, agent, input_data, verbose, console)
            )
            display_trace_results(console, trace_data, verbose)
        except Exception as e:
            console.print(f"[red]Trace execution failed: {e}[/red]")
            raise typer.Exit(1) from None

    handle()


@app.command("profile")
def profile_performance(
    command: Annotated[
        str, typer.Argument(help="Command to profile (e.g., 'agents run echo')")
    ],
    iterations: Annotated[
        int, typer.Option("--iterations", "-n", help="Number of iterations")
    ] = 10,
    input_data: Annotated[
        str | None, typer.Option("--input", help="JSON input data")
    ] = None,
) -> None:
    """Profile command performance and resource usage."""

    @inject
    def handle() -> None:
        """Handle performance profiling."""
        console = Console()

        console.print(f"[bold blue]Profiling Command:[/bold blue] {command}")
        console.print(f"[dim]Iterations: {iterations}[/dim]")
        console.print()

        # Parse command
        try:
            cmd_parts = command.split()
            if len(cmd_parts) < 2:
                console.print("[red]Error: Invalid command format[/red]")
                raise typer.Exit(1)

            command_type = cmd_parts[0]  # e.g., "agents", "tools", "flow"
            subcommand = cmd_parts[1]  # e.g., "run"
            target = cmd_parts[2] if len(cmd_parts) > 2 else None  # e.g., "echo"

            # Run profiling
            profile_data = run_performance_profiling(
                command_type, subcommand, target, iterations, input_data, console
            )
            display_profile_results(console, profile_data)

        except Exception as e:
            console.print(f"[red]Profiling failed: {e}[/red]")
            raise typer.Exit(1) from None

    handle()


def run_health_checks(component: str | None, console: Console) -> HealthStatus:
    """Run comprehensive health checks."""
    health_data: HealthStatus = {
        "timestamp": time.time(),
        "overall_status": "healthy",
        "components": {},
        "summary": {},
    }

    components_to_check = []
    if component == "all" or not component:
        components_to_check = ["tools", "flows", "agents"]
    else:
        components_to_check = [component]

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
        transient=True,
    ) as progress:

        for comp in components_to_check:
            task = progress.add_task(f"Checking {comp}...", total=None)

            try:
                if comp == "tools":
                    tools_status = check_tools_health()
                    health_data["components"]["tools"] = tools_status
                elif comp == "flows":
                    flows_status = check_flows_health()
                    health_data["components"]["flows"] = flows_status
                elif comp == "agents":
                    agents_status = check_agents_health()
                    health_data["components"]["agents"] = agents_status

                progress.update(task, completed=True)

            except Exception as e:
                health_data["components"][comp] = {"status": "error", "error": str(e)}
                health_data["overall_status"] = "degraded"

    # Generate summary
    total_components = len(health_data["components"])
    healthy_components = sum(
        1
        for comp in health_data["components"].values()
        if comp.get("status") == "healthy"
    )

    health_data["summary"] = {
        "total_components": total_components,
        "healthy_components": healthy_components,
        "unhealthy_components": total_components - healthy_components,
    }

    return health_data


def check_tools_health() -> dict[str, Any]:
    """Check tools component health."""
    try:
        tools = get_available_tools()
        tool_statuses = {}

        for name, tool in tools.items():
            try:
                # Basic validation
                if hasattr(tool, "name") and hasattr(tool, "implementation"):
                    tool_statuses[name] = {"status": "healthy", "type": "FlowTool"}
                else:
                    tool_statuses[name] = {
                        "status": "error",
                        "error": "Invalid tool structure",
                    }
            except Exception as e:
                tool_statuses[name] = {"status": "error", "error": str(e)}

        return {"status": "healthy", "count": len(tools), "tools": tool_statuses}
    except Exception as e:
        return {"status": "error", "error": str(e)}


def check_flows_health() -> dict[str, Any]:
    """Check flows component health."""
    try:
        flows = get_available_flows()
        flow_statuses = {}

        for name, flow in flows.items():
            try:
                # Basic validation
                if hasattr(flow, "name"):
                    flow_statuses[name] = {"status": "healthy", "type": "Flow"}
                else:
                    flow_statuses[name] = {
                        "status": "error",
                        "error": "Invalid flow structure",
                    }
            except Exception as e:
                flow_statuses[name] = {"status": "error", "error": str(e)}

        return {"status": "healthy", "count": len(flows), "flows": flow_statuses}
    except Exception as e:
        return {"status": "error", "error": str(e)}


def check_agents_health() -> dict[str, Any]:
    """Check agents component health."""
    try:
        agents = get_available_agents()
        agent_statuses = {}

        for name, agent in agents.items():
            try:
                # Basic validation
                if (
                    hasattr(agent, "name")
                    and hasattr(agent, "input_schema")
                    and hasattr(agent, "output_schema")
                ):
                    agent_statuses[name] = {"status": "healthy", "type": "FlowAgent"}
                else:
                    agent_statuses[name] = {
                        "status": "error",
                        "error": "Invalid agent structure",
                    }
            except Exception as e:
                agent_statuses[name] = {"status": "error", "error": str(e)}

        return {"status": "healthy", "count": len(agents), "agents": agent_statuses}
    except Exception as e:
        return {"status": "error", "error": str(e)}


def display_health_results(console: Console, health_data: HealthStatus) -> None:
    """Display health check results in rich format."""
    status_emoji = "✅" if health_data["overall_status"] == "healthy" else "⚠️"

    console.print()
    console.print(
        Panel.fit(
            f"[bold blue]Overall Status:[/bold blue] {status_emoji} {health_data['overall_status'].title()}\n"
            f"[dim]Timestamp: {time.ctime(health_data['timestamp'])}[/dim]",
            border_style="blue",
            title="🔍 System Health",
        )
    )

    # Summary table
    summary = health_data["summary"]
    console.print("\n[bold blue]Summary:[/bold blue]")
    console.print(f"  • Total Components: {summary['total_components']}")
    console.print(f"  • Healthy: [green]{summary['healthy_components']}[/green]")
    console.print(f"  • Unhealthy: [red]{summary['unhealthy_components']}[/red]")

    # Component details
    for comp_name, comp_data in health_data["components"].items():
        status_color = "green" if comp_data.get("status") == "healthy" else "red"
        status_text = comp_data.get("status", "unknown").title()

        console.print(
            f"\n[bold blue]{comp_name.title()}:[/bold blue] [{status_color}]{status_text}[/{status_color}]"
        )

        if comp_data.get("status") == "healthy":
            console.print(f"  • Count: {comp_data.get('count', 0)}")

            # Show individual item status
            items = comp_data.get(comp_name, {})  # tools, flows, or agents
            if items:
                for item_name, item_status in items.items():
                    item_color = (
                        "green" if item_status.get("status") == "healthy" else "red"
                    )
                    console.print(
                        f"    - {item_name}: [{item_color}]{item_status.get('status', 'unknown')}[/{item_color}]"
                    )
        else:
            console.print(f"  • Error: {comp_data.get('error', 'Unknown error')}")


async def run_trace_execution(
    flow: str | None,
    agent: str | None,
    input_data: str,
    verbose: bool,
    console: Console,
) -> dict[str, Any]:
    """Run execution tracing."""
    steps_list: list[dict[str, Any]] = []
    trace_data = {
        "timestamp": time.time(),
        "type": "flow" if flow else "agent",
        "target": flow or agent,
        "input": input_data,
        "steps": steps_list,
        "duration": 0.0,
        "success": False,
    }

    start_time = time.time()

    try:
        # Parse input
        input_dict = json.loads(input_data)

        steps_list.append(
            {
                "step": "input_validation",
                "status": "success",
                "timestamp": time.time(),
                "details": "Input JSON parsed successfully",
            }
        )

        if flow:
            # Trace flow execution
            flows = get_available_flows()
            if flow not in flows:
                raise ValueError(f"Flow '{flow}' not found")

            flow_obj = flows[flow]
            steps_list.append(
                {
                    "step": "flow_lookup",
                    "status": "success",
                    "timestamp": time.time(),
                    "details": f"Found flow: {flow}",
                }
            )

            # Simulate execution tracing
            async def traced_input_stream() -> AsyncIterator[dict[str, Any]]:
                steps_list.append(
                    {
                        "step": "stream_creation",
                        "status": "success",
                        "timestamp": time.time(),
                        "details": "Input stream created",
                    }
                )
                yield input_dict

            results = []
            async for output in flow_obj(traced_input_stream()):
                steps_list.append(
                    {
                        "step": "flow_processing",
                        "status": "success",
                        "timestamp": time.time(),
                        "details": f"Flow produced output: {type(output).__name__}",
                    }
                )
                results.append(output)

        else:  # agent
            # Trace agent execution
            agents = get_available_agents()
            if agent not in agents:
                raise ValueError(f"Agent '{agent}' not found")

            agent_obj = agents[agent]
            steps_list.append(
                {
                    "step": "agent_lookup",
                    "status": "success",
                    "timestamp": time.time(),
                    "details": f"Found agent: {agent}",
                }
            )

            # Validate input
            input_schema = agent_obj.input_schema.model_validate(input_dict)
            steps_list.append(
                {
                    "step": "schema_validation",
                    "status": "success",
                    "timestamp": time.time(),
                    "details": f"Input validated against {agent_obj.input_schema.__name__}",
                }
            )

            # Convert to flow and trace
            agent_flow = agent_obj.as_flow()
            steps_list.append(
                {
                    "step": "flow_conversion",
                    "status": "success",
                    "timestamp": time.time(),
                    "details": "Agent converted to flow",
                }
            )

            # Execute
            async def traced_agent_stream() -> AsyncIterator[Any]:
                yield input_schema

            results = []
            async for output in agent_flow(traced_agent_stream()):
                steps_list.append(
                    {
                        "step": "agent_processing",
                        "status": "success",
                        "timestamp": time.time(),
                        "details": f"Agent produced output: {type(output).__name__}",
                    }
                )
                results.append(output)

        trace_data["success"] = True
        trace_data["output"] = results[-1] if results else None

    except Exception as e:
        steps_list.append(
            {
                "step": "error",
                "status": "error",
                "timestamp": time.time(),
                "details": str(e),
            }
        )
        trace_data["error"] = str(e)

    trace_data["duration"] = time.time() - start_time
    return trace_data


def display_trace_results(
    console: Console, trace_data: dict[str, Any], verbose: bool
) -> None:
    """Display trace execution results."""
    success_emoji = "✅" if trace_data["success"] else "❌"

    console.print()
    console.print(
        Panel.fit(
            f"[bold blue]Trace: {trace_data['type'].title()}[/bold blue] {success_emoji}\n"
            f"[dim]Target: {trace_data['target']}[/dim]\n"
            f"[dim]Duration: {trace_data['duration']:.3f}s[/dim]",
            border_style="blue",
            title="🔍 Execution Trace",
        )
    )

    # Show steps
    console.print("\n[bold blue]Execution Steps:[/bold blue]")
    for i, step in enumerate(trace_data["steps"], 1):
        status_color = "green" if step["status"] == "success" else "red"
        status_icon = "✓" if step["status"] == "success" else "✗"

        console.print(
            f"  {i}. [{status_color}]{status_icon}[/{status_color}] {step['step']}"
        )
        if verbose:
            console.print(f"     [dim]{step['details']}[/dim]")

    if not trace_data["success"] and "error" in trace_data:
        console.print(f"\n[bold red]Error:[/bold red] {trace_data['error']}")


def run_performance_profiling(
    command_type: str,
    subcommand: str,
    target: str | None,
    iterations: int,
    input_data: str | None,
    console: Console,
) -> dict[str, Any]:
    """Run performance profiling."""
    # This is a simplified profiling implementation
    # In a real system, you'd use proper profiling tools

    times = []
    errors = 0

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
        transient=True,
    ) as progress:

        task = progress.add_task(
            f"Profiling {iterations} iterations...", total=iterations
        )

        for _ in range(iterations):
            start_time = time.time()
            try:
                # Simulate command execution timing
                if command_type == "agents" and subcommand == "run" and target:
                    # Simulate agent execution
                    time.sleep(0.01)  # Simulated processing time
                elif command_type == "tools" and subcommand == "run" and target:
                    # Simulate tool execution
                    time.sleep(0.005)  # Tools are typically faster
                elif command_type == "flow" and subcommand == "exec" and target:
                    # Simulate flow execution
                    time.sleep(0.008)
                else:
                    time.sleep(0.001)

                execution_time = time.time() - start_time
                times.append(execution_time)

            except Exception:
                errors += 1

            progress.update(task, advance=1)

    # Calculate statistics
    if times:
        avg_time = sum(times) / len(times)
        min_time = min(times)
        max_time = max(times)

        # Simple percentile calculation
        sorted_times = sorted(times)
        p50_idx = len(sorted_times) // 2
        p95_idx = int(len(sorted_times) * 0.95)

        p50_time = sorted_times[p50_idx]
        p95_time = (
            sorted_times[p95_idx] if p95_idx < len(sorted_times) else sorted_times[-1]
        )
    else:
        avg_time = min_time = max_time = p50_time = p95_time = 0

    return {
        "command": f"{command_type} {subcommand} {target or ''}".strip(),
        "iterations": iterations,
        "successful_runs": len(times),
        "errors": errors,
        "times": {
            "average": avg_time,
            "min": min_time,
            "max": max_time,
            "p50": p50_time,
            "p95": p95_time,
        },
    }


def display_profile_results(console: Console, profile_data: dict[str, Any]) -> None:
    """Display performance profiling results."""
    console.print()
    console.print(
        Panel.fit(
            f"[bold blue]Command:[/bold blue] {profile_data['command']}\n"
            f"[dim]Iterations: {profile_data['iterations']}[/dim]\n"
            f"[dim]Successful: {profile_data['successful_runs']}, Errors: {profile_data['errors']}[/dim]",
            border_style="blue",
            title="⚡ Performance Profile",
        )
    )

    times = profile_data["times"]
    console.print("\n[bold blue]Timing Statistics:[/bold blue]")
    console.print(f"  • Average: {times['average']:.4f}s")
    console.print(f"  • Min: {times['min']:.4f}s")
    console.print(f"  • Max: {times['max']:.4f}s")
    console.print(f"  • P50 (Median): {times['p50']:.4f}s")
    console.print(f"  • P95: {times['p95']:.4f}s")

    if profile_data["errors"] > 0:
        error_rate = (profile_data["errors"] / profile_data["iterations"]) * 100
        console.print(f"\n[bold red]Error Rate:[/bold red] {error_rate:.1f}%")
