"""Pipeline orchestration for complex workflows and tool composition."""

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
from rich.progress import BarColumn, Progress, SpinnerColumn, TextColumn
from rich.table import Table

from goldentooth_agent.cli.commands.tools import get_available_tools
from goldentooth_agent.core.flow_agent import FlowIOSchema, FlowTool

app = typer.Typer()

# Type aliases for pipeline system
PipelineStep = dict[str, Any]  # Configuration for a pipeline step
PipelineConfig = dict[str, Any]  # Pipeline configuration
PipelineResult = dict[str, Any]  # Pipeline execution result


class PipelineStepConfig:
    """Configuration for a pipeline step."""

    def __init__(
        self,
        tool_name: str,
        input_mapping: dict[str, str] | None = None,
        static_input: dict[str, Any] | None = None,
        output_key: str | None = None,
    ):
        self.tool_name = tool_name
        self.input_mapping = input_mapping or {}
        self.static_input = static_input or {}
        self.output_key = output_key or tool_name


class Pipeline:
    """Pipeline orchestrator for chaining tools together."""

    def __init__(self, name: str, description: str = ""):
        self.name = name
        self.description = description
        self.steps: list[PipelineStepConfig] = []
        self.tools = get_available_tools()

    def add_step(
        self,
        tool_name: str,
        input_mapping: dict[str, str] | None = None,
        static_input: dict[str, Any] | None = None,
        output_key: str | None = None,
    ) -> Pipeline:
        """Add a step to the pipeline."""
        if tool_name not in self.tools:
            raise ValueError(f"Tool '{tool_name}' not found")

        step = PipelineStepConfig(tool_name, input_mapping, static_input, output_key)
        self.steps.append(step)
        return self

    async def execute(
        self, initial_input: dict[str, Any], console: Console | None = None
    ) -> dict[str, Any]:
        """Execute the pipeline with the given input."""
        if console is None:
            console = Console()

        # Initialize pipeline context with initial input
        context = {"input": initial_input}

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            console=console,
            transient=True,
        ) as progress:

            task = progress.add_task(
                f"Executing pipeline: {self.name}", total=len(self.steps)
            )

            for i, step in enumerate(self.steps):
                # Update progress
                progress.update(
                    task, description=f"Step {i+1}/{len(self.steps)}: {step.tool_name}"
                )

                # Get the tool
                tool = self.tools[step.tool_name]

                # Prepare step input
                step_input = {}

                # Apply static input first
                step_input.update(step.static_input)

                # Apply input mapping
                for target_field, source_path in step.input_mapping.items():
                    value = self._resolve_path(context, source_path)
                    step_input[target_field] = value

                # Execute the tool
                try:
                    result = await self._execute_tool(tool, step_input)

                    # Store result in context
                    context[step.output_key] = result.model_dump()

                except Exception as e:
                    # Store error information
                    context[step.output_key] = {
                        "error": str(e),
                        "success": False,
                        "step": step.tool_name,
                    }

                progress.update(task, advance=1)

        return context

    def _resolve_path(self, context: dict[str, Any], path: str) -> Any:
        """Resolve a dot-notation path in the context."""
        parts = path.split(".")
        current = context

        for part in parts:
            if isinstance(current, dict) and part in current:
                current = current[part]
            else:
                raise ValueError(f"Path '{path}' not found in context")

        return current

    async def _execute_tool(
        self, tool: FlowTool, input_data: dict[str, Any]
    ) -> FlowIOSchema:
        """Execute a single tool with input data."""
        # Validate input
        validated_input = tool.input_schema.model_validate(input_data)

        # Convert tool to flow and execute
        tool_flow = tool.as_flow()

        # Create input stream
        async def input_stream() -> AsyncIterator[FlowIOSchema]:
            yield validated_input

        # Process and collect results
        results = []
        async for output_data in tool_flow(input_stream()):
            results.append(output_data)

        if results:
            return results[-1]
        else:
            raise RuntimeError("Tool produced no output")


def create_sample_pipelines() -> dict[str, Pipeline]:
    """Create sample pipeline configurations."""
    pipelines = {}

    # Web scraping + text analysis pipeline
    web_analysis = Pipeline(
        "web_analysis", "Scrape web content and analyze its text characteristics"
    )
    web_analysis.add_step(
        "web_scrape",
        input_mapping={"url": "input.url"},
        static_input={"extract_text": True, "extract_links": False},
        output_key="scrape_result",
    ).add_step(
        "text_analysis",
        input_mapping={"text": "scrape_result.text_content"},
        static_input={"include_sentiment": True, "include_keywords": True},
        output_key="analysis_result",
    )
    pipelines["web_analysis"] = web_analysis

    # File processing pipeline
    file_process = Pipeline(
        "file_process", "Read a file, process it as JSON, and analyze extracted text"
    )
    file_process.add_step(
        "file_read",
        input_mapping={"file_path": "input.file_path"},
        output_key="file_content",
    ).add_step(
        "json_process",
        input_mapping={"json_data": "file_content.content"},
        static_input={"operation": "parse"},
        output_key="parsed_json",
    ).add_step(
        "text_analysis",
        input_mapping={"text": "parsed_json.result_data.description"},
        output_key="text_stats",
    )
    pipelines["file_process"] = file_process

    # System monitoring pipeline
    system_monitor = Pipeline(
        "system_monitor", "Collect system information and save to file"
    )
    system_monitor.add_step(
        "system_info",
        static_input={"include_cpu": True, "include_memory": True},
        output_key="system_data",
    ).add_step(
        "json_process",
        input_mapping={"data_object": "system_data"},
        static_input={"operation": "stringify", "pretty_print": True},
        output_key="formatted_json",
    ).add_step(
        "file_write",
        input_mapping={
            "content": "formatted_json.result_json",
            "file_path": "input.output_file",
        },
        output_key="write_result",
    )
    pipelines["system_monitor"] = system_monitor

    return pipelines


@app.command("list")
def list_pipelines() -> None:
    """List all available pipeline configurations."""

    @inject
    def handle() -> None:
        """Handle pipeline listing."""
        console = Console()
        pipelines = create_sample_pipelines()

        if not pipelines:
            console.print("[yellow]No pipelines available[/yellow]")
            return

        # Create a rich table
        table = Table(
            title="Available Pipelines", show_header=True, header_style="bold magenta"
        )
        table.add_column("Name", style="cyan", no_wrap=True)
        table.add_column("Description", style="green")
        table.add_column("Steps", style="blue")

        for name, pipeline in pipelines.items():
            steps_info = " → ".join([step.tool_name for step in pipeline.steps])
            table.add_row(name, pipeline.description, steps_info)

        console.print()
        console.print(table)
        console.print()

        # Show usage examples
        console.print(
            Panel.fit(
                "[bold blue]Usage Examples:[/bold blue]\\n"
                '• goldentooth-agent pipeline run web_analysis --input \'{"url": "https://example.com"}\'\\n'
                '• goldentooth-agent pipeline run system_monitor --input \'{"output_file": "/tmp/system.json"}\'\\n'
                "• goldentooth-agent pipeline describe web_analysis",
                border_style="blue",
                title="🔧 Pipeline Usage",
            )
        )

    handle()


@app.command("describe")
def describe_pipeline(
    pipeline_name: Annotated[
        str, typer.Argument(help="Name of the pipeline to describe")
    ],
) -> None:
    """Show detailed information about a specific pipeline."""

    @inject
    def handle() -> None:
        """Handle pipeline description."""
        console = Console()
        pipelines = create_sample_pipelines()

        if pipeline_name not in pipelines:
            console.print(f"[red]Error: Pipeline '{pipeline_name}' not found[/red]")
            console.print(
                f"[dim]Available pipelines: {', '.join(pipelines.keys())}[/dim]"
            )
            raise typer.Exit(1)

        pipeline = pipelines[pipeline_name]

        # Show pipeline information
        console.print()
        console.print(
            Panel.fit(
                f"[bold cyan]Pipeline: {pipeline_name}[/bold cyan]\\n"
                f"[dim]{pipeline.description}[/dim]",
                border_style="cyan",
                title="🔧 Pipeline Details",
            )
        )

        console.print("\\n[bold blue]Execution Steps:[/bold blue]")
        for i, step in enumerate(pipeline.steps, 1):
            console.print(f"  {i}. [cyan]{step.tool_name}[/cyan]")

            if step.input_mapping:
                console.print("     [dim]Input mapping:[/dim]")
                for target, source in step.input_mapping.items():
                    console.print(f"       • {target} ← {source}")

            if step.static_input:
                console.print("     [dim]Static input:[/dim]")
                for key, value in step.static_input.items():
                    console.print(f"       • {key}: {value}")

            console.print(f"     [dim]Output key: {step.output_key}[/dim]")
            console.print()

    handle()


@app.command("run")
def run_pipeline(
    pipeline_name: Annotated[str, typer.Argument(help="Name of the pipeline to run")],
    input_data: Annotated[
        str | None, typer.Option("--input", help="JSON input data")
    ] = None,
    format: Annotated[
        str, typer.Option("--format", "-f", help="Output format: summary, json, full")
    ] = "summary",
) -> None:
    """Execute a pipeline with input data."""

    @inject
    def handle() -> None:
        """Handle pipeline execution."""
        console = Console()
        pipelines = create_sample_pipelines()

        if pipeline_name not in pipelines:
            console.print(f"[red]Error: Pipeline '{pipeline_name}' not found[/red]")
            console.print(
                f"[dim]Available pipelines: {', '.join(pipelines.keys())}[/dim]"
            )
            raise typer.Exit(1)

        pipeline = pipelines[pipeline_name]

        # Parse input data
        if input_data:
            try:
                input_dict = json.loads(input_data)
            except json.JSONDecodeError as e:
                console.print(f"[red]Error: Invalid JSON input: {e}[/red]")
                raise typer.Exit(1)
        else:
            # Default inputs for different pipelines
            if pipeline_name == "web_analysis":
                input_dict = {"url": "https://httpbin.org/html"}
            elif pipeline_name == "system_monitor":
                input_dict = {"output_file": "/tmp/system_info.json"}
            else:
                input_dict = {}

        # Execute pipeline
        try:
            console.print(f"[bold blue]Executing Pipeline: {pipeline_name}[/bold blue]")
            start_time = time.time()

            result = asyncio.run(pipeline.execute(input_dict, console))

            execution_time = time.time() - start_time

            # Display results based on format
            if format == "json":
                print(json.dumps(result, indent=2, default=str))
            elif format == "full":
                console.print("\\n[bold blue]Full Pipeline Results:[/bold blue]")
                for key, value in result.items():
                    console.print(f"\\n[cyan]{key}:[/cyan]")
                    if isinstance(value, dict):
                        for sub_key, sub_value in value.items():
                            console.print(f"  • {sub_key}: {sub_value}")
                    else:
                        console.print(f"  {value}")
            else:  # summary
                console.print("\\n[bold blue]Pipeline Summary:[/bold blue]")
                console.print(f"  • Execution time: {execution_time:.2f}s")
                console.print(f"  • Steps completed: {len(pipeline.steps)}")

                # Show key results
                for key, value in result.items():
                    if key != "input" and isinstance(value, dict):
                        success = value.get("success", True)
                        status = "[green]✓[/green]" if success else "[red]✗[/red]"
                        console.print(f"  • {key}: {status}")

                        if not success and "error" in value:
                            console.print(f"    [red]Error: {value['error']}[/red]")

        except Exception as e:
            console.print(f"[red]Pipeline execution failed: {e}[/red]")
            raise typer.Exit(1)

    handle()


@app.command("create")
def create_pipeline(
    name: Annotated[str, typer.Argument(help="Name for the new pipeline")],
    config_file: Annotated[
        str | None, typer.Option("--config", help="JSON config file path")
    ] = None,
) -> None:
    """Create a new pipeline from configuration."""

    @inject
    def handle() -> None:
        """Handle pipeline creation."""
        console = Console()

        console.print(
            "[yellow]Pipeline creation from config not yet implemented[/yellow]"
        )
        console.print(f"[dim]Requested pipeline: {name}[/dim]")
        if config_file:
            console.print(f"[dim]Config file: {config_file}[/dim]")

        # Future implementation would:
        # 1. Load pipeline config from JSON file
        # 2. Validate tool names and connections
        # 3. Save pipeline to a registry
        # 4. Allow custom pipelines to be loaded

    handle()
