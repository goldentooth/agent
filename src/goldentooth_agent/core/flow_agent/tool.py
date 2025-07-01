"""FlowTool class with flow conversion and agent compatibility."""

from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator, Callable
from typing import Any, TypeVar

from goldentooth_agent.flow_engine import Flow

from .schema import FlowIOSchema

# Type aliases for tool system
AnyFlow = Flow[Any, Any]  # Flexible flow types for tool conversion
AnyAgent = Any  # Agent type (avoid forward reference)
AnyInput = Any  # Flexible input for tool pipeline
AnyOutput = Any  # Flexible output for tool pipeline

T = TypeVar("T", bound=FlowIOSchema)
R = TypeVar("R", bound=FlowIOSchema)


class FlowTool:
    """Flow-based tool with agent-like interface.

    FlowTool provides a unified interface for tools that can be used as flows
    or converted to agent-compatible interfaces.
    """

    def __init__(
        self,
        name: str,
        input_schema: type[T],
        output_schema: type[R],
        implementation: Callable[[T], R] | Callable[[T], asyncio.Future[R]],
        description: str = "",
    ) -> None:
        """Initialize a FlowTool.

        Args:
            name: Name of the tool
            input_schema: Pydantic schema class for input validation
            output_schema: Pydantic schema class for output validation
            implementation: Function that implements the tool logic
            description: Human-readable description of the tool
        """
        self.name = name
        self.input_schema = input_schema
        self.output_schema = output_schema
        self.implementation = implementation
        self.description = description

    def as_flow(self) -> AnyFlow:
        """Convert tool to a composable flow.

        Returns:
            Flow that validates input, runs implementation, and validates output
        """
        return Flow(self._tool_pipeline, name=f"tool:{self.name}")

    def as_agent(self) -> AnyAgent:  # Use Any to avoid forward reference issues
        """Convert tool to an agent-compatible interface.

        Returns:
            FlowAgent that wraps this tool with agent-like behavior
        """
        # Import here to avoid circular dependency
        from .agent import FlowAgent

        return FlowAgent(
            name=f"agent:{self.name}",
            input_schema=self.input_schema,
            output_schema=self.output_schema,
            system_flow=Flow(self._passthrough, name="tool_system"),
            processing_flow=self.as_flow(),
        )

    async def _tool_pipeline(
        self, stream: AsyncIterator[AnyInput]  # Use Any for flexibility
    ) -> AsyncIterator[AnyOutput]:  # Use Any for flexibility
        """Implementation of the tool pipeline."""
        async for input_data in stream:
            # Validate input
            if isinstance(input_data, self.input_schema):
                validated_input = input_data
            else:
                # Try to convert
                validated_input = self.input_schema.model_validate(input_data)

            # Run implementation
            result = self.implementation(validated_input)

            # Handle async results
            if asyncio.iscoroutine(result):
                result = await result  # type: ignore[unreachable]

            # Validate output
            if isinstance(result, self.output_schema):
                validated_output = result
            else:
                # Try to convert
                validated_output = self.output_schema.model_validate(result)

            yield validated_output

    async def _passthrough(
        self, stream: AsyncIterator[AnyInput]
    ) -> AsyncIterator[AnyOutput]:
        """Passthrough flow for system processing (used when tool acts as agent)."""
        async for item in stream:
            yield item
