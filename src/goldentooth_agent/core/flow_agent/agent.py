"""FlowAgent class with pipeline composition."""

from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Any

from goldentooth_agent.flow_engine import Flow

from ..context import Context
from .schema import FlowIOSchema

# Type alias for agent system
LLMClient = Any  # Various LLM clients (OpenAI, Anthropic, etc.)


class FlowAgent:
    """Flow-based agent using functional composition.

    FlowAgent implements a complete agent pipeline that:
    1. Validates input schemas
    2. Converts input to context
    3. Runs system flow (prompt generation, memory, etc.)
    4. Runs processing flow (LLM calls, tool execution, etc.)
    5. Extracts and validates output schemas
    """

    def __init__(
        self,
        name: str,
        input_schema: type[FlowIOSchema],
        output_schema: type[FlowIOSchema],
        system_flow: Flow[Context, Context],
        processing_flow: Flow[Context, Context],
        client: LLMClient = None,
        model: str = "gpt-4",
    ) -> None:
        """Initialize a FlowAgent.

        Args:
            name: Name of the agent
            input_schema: Pydantic schema class for input validation
            output_schema: Pydantic schema class for output validation
            system_flow: Flow for system-level processing (prompts, memory, etc.)
            processing_flow: Flow for main processing (LLM calls, tool execution, etc.)
            client: Optional LLM client
            model: Model name to use
        """
        self.name = name
        self.input_schema = input_schema
        self.output_schema = output_schema
        self.system_flow = system_flow
        self.processing_flow = processing_flow
        self.client = client
        self.model = model

    def as_flow(self) -> Flow[FlowIOSchema, FlowIOSchema]:
        """Convert agent to a composable flow.

        Returns:
            Flow that implements the complete agent pipeline
        """
        return Flow(self._agent_pipeline, name=f"agent:{self.name}")

    async def _agent_pipeline(
        self, stream: AsyncIterator[FlowIOSchema]
    ) -> AsyncIterator[FlowIOSchema]:
        """Complete agent processing pipeline."""
        async for input_data in stream:
            # Step 1: Validate input
            if not isinstance(input_data, self.input_schema):
                validated_input = self.input_schema.model_validate(input_data)
            else:
                validated_input = input_data

            # Step 2: Convert to context
            context = Context()
            context = validated_input.to_context(context)

            # Step 3: Create single-item stream for system flow
            async def context_stream(ctx: Context = context) -> AsyncIterator[Context]:
                yield ctx

            # Step 4: Process through system flow
            system_stream = context_stream()
            system_results = []
            async for processed_context in self.system_flow(system_stream):
                system_results.append(processed_context)

            # Take the last result from system flow
            if system_results:
                processed_context = system_results[-1]
            else:
                processed_context = context

            # Step 5: Process through main processing flow
            async def processing_stream(
                ctx: Context = processed_context,
            ) -> AsyncIterator[Context]:
                yield ctx

            processing_stream_instance = processing_stream()
            processing_results = []
            async for final_context in self.processing_flow(processing_stream_instance):
                processing_results.append(final_context)

            # Take the last result from processing flow
            if processing_results:
                final_context = processing_results[-1]
            else:
                final_context = processed_context

            # Step 6: Extract output from context
            try:
                output_data = self.output_schema.from_context(final_context)
            except (KeyError, ValueError):
                # If we can't extract the output schema from context,
                # it might be because the processing flow didn't put it there
                # In that case, we need a fallback mechanism
                # For now, let's create a basic output
                try:
                    # Try to create with common fields like 'response'
                    output_data = self.output_schema(response="No response generated")  # type: ignore[call-arg]
                except TypeError:
                    # If that fails, try with no arguments
                    output_data = self.output_schema()

            # Step 7: Validate and yield output
            if not isinstance(output_data, self.output_schema):
                validated_output = self.output_schema.model_validate(output_data)
            else:
                validated_output = output_data

            yield validated_output
