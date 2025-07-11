from __future__ import annotations

from pathlib import Path
from typing import Any

from ..async_bridge.execution import run_flow_sync
from ..core.context import FlowCommandContext
from ..core.exceptions import FlowCommandError
from ..core.result import FlowCommandResult

# FlowMetadata not currently used but available for future enhancements


def flow_list_implementation(
    category: str | None = None,
    tag: str | None = None,
    context: FlowCommandContext | None = None,
) -> FlowCommandResult[list[str]]:
    """List available flows with optional filtering."""
    if context is None:
        context = FlowCommandContext.from_test()

    try:
        registry = context.flow_registry

        # Get all flows
        flows = registry.list(category=category)

        # Tag filtering is not directly supported by the registry API
        # For now, we'll return flows based on category filter only
        # TODO: Implement tag filtering by inspecting flow metadata

        return FlowCommandResult[list[str]].success_result(flows)
    except Exception as e:
        return FlowCommandResult[list[str]].error_result(f"Failed to list flows: {e}")


def flow_search_implementation(
    query: str,
    context: FlowCommandContext | None = None,
) -> FlowCommandResult[list[str]]:
    """Search flows by name or metadata."""
    if context is None:
        context = FlowCommandContext.from_test()

    try:
        registry = context.flow_registry
        results = registry.search(query)
        return FlowCommandResult[list[str]].success_result(results)
    except Exception as e:
        return FlowCommandResult[list[str]].error_result(f"Failed to search flows: {e}")


def flow_run_implementation(
    flow_name: str,
    input_file: Path | None = None,
    input_data: Any = None,
    context: FlowCommandContext | None = None,
) -> FlowCommandResult[list[Any]]:
    """Execute a flow with input data."""
    if context is None:
        context = FlowCommandContext.from_test()

    try:
        registry = context.flow_registry

        # Get the flow
        flow = registry.get(flow_name)
        if flow is None:
            raise FlowCommandError(f"Flow '{flow_name}' not found")

        # Prepare input data
        input_items: list[Any]
        if input_file and input_file.exists():
            # Load data from file
            if input_file.suffix == ".json":
                import json

                with open(input_file) as f:
                    file_data: Any = json.load(f)
                if isinstance(file_data, list):
                    input_items = (  # pyright: ignore[reportUnknownVariableType]
                        file_data
                    )
                else:
                    input_items = [file_data]
            else:
                with open(input_file) as f:
                    file_data = f.read().strip().split("\n")
                input_items = file_data
        elif input_data is not None:
            # Use provided data
            if isinstance(input_data, list):
                input_items = input_data  # pyright: ignore[reportUnknownVariableType]
            else:
                input_items = [input_data]
        else:
            # Default empty input
            input_items = []

        # Execute the flow
        result = run_flow_sync(flow, input_items, context)
        return result

    except Exception as e:
        return FlowCommandResult[list[Any]].error_result(f"Failed to run flow: {e}")
