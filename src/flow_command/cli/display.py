from __future__ import annotations

from typing import Any

# Console imported via context.console
from rich.panel import Panel
from rich.table import Table

from ..core.context import FlowCommandContext
from ..core.result import FlowCommandResult


class FlowDisplay:
    """Rich display utilities for flow command output."""

    def __init__(self, context: FlowCommandContext) -> None:
        """Initialize display with command context."""
        super().__init__()
        self.context = context
        self.console = context.console

    def show_result(self, result: FlowCommandResult[Any]) -> None:
        """Display a command result with appropriate formatting."""
        if self.context.output_format == "json":
            self._show_json_result(result)
        elif self.context.output_format == "table" and isinstance(result.data, list):
            self._show_table_result(result)
        else:
            self._show_text_result(result)

    def _show_json_result(self, result: FlowCommandResult[Any]) -> None:
        """Display result in JSON format."""
        import json

        self.console.print(json.dumps(result.to_json(), indent=2))

    def _show_table_result(self, result: FlowCommandResult[Any]) -> None:
        """Display list result in table format."""
        if not result.success or not result.data:
            self._show_text_result(result)
            return

        table = Table(title="Flow Results")
        table.add_column("Name", style="cyan")
        table.add_column("Status", style="green")

        for item in result.data:
            item_str = str(item)
            table.add_row(item_str, "Available")

        self.console.print(table)

    def _show_text_result(self, result: FlowCommandResult[Any]) -> None:
        """Display result in text format."""
        if result.success:
            if result.data:
                if isinstance(result.data, list):
                    for (
                        item  # pyright: ignore[reportUnknownVariableType]
                    ) in result.data:  # pyright: ignore[reportUnknownMemberType]
                        self.console.print(
                            f"• {item}"
                        )  # pyright: ignore[reportUnknownMemberType]
                else:
                    self.console.print(str(result.data))
            else:
                self.console.print("No results found.")
        else:
            error_panel = Panel(
                f"[red]Error:[/red] {result.error}",
                title="Command Failed",
                border_style="red",
            )
            self.console.print(error_panel)

    def show_flow_execution(
        self, flow_name: str, result: FlowCommandResult[Any]
    ) -> None:
        """Display flow execution results with enhanced formatting."""
        if result.success:
            success_panel = Panel(
                f"[green]Successfully executed flow:[/green] {flow_name}\n"
                + f"[dim]Execution time: {result.execution_time:.3f}s[/dim]",
                title="Flow Execution Complete",
                border_style="green",
            )
            self.console.print(success_panel)

            if result.data:
                if self.context.output_format == "json":
                    self._show_json_result(result)
                else:
                    self.console.print("\n[bold]Results:[/bold]")
                    for item in result.data:
                        self.console.print(f"  {item}")
        else:
            self._show_text_result(result)
