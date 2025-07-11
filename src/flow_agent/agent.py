"""FlowAgent class with pipeline composition."""

from __future__ import annotations

from collections.abc import AsyncGenerator
from typing import Any

from context import Context
from context_flow.schema import ContextFlowSchema
from flow import Flow

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
        input_schema: type[ContextFlowSchema],
        output_schema: type[ContextFlowSchema],
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
        super().__init__()
        self.name = name
        self.input_schema = input_schema
        self.output_schema = output_schema
        self.system_flow = system_flow
        self.processing_flow = processing_flow
        self.client = client
        self.model = model

    async def run(self, input_data: ContextFlowSchema) -> ContextFlowSchema:
        """Run the agent with a single input.

        Args:
            input_data: Input data matching the agent's input schema

        Returns:
            Output data matching the agent's output schema
        """

        # Create a single-item stream
        async def input_stream() -> AsyncGenerator[ContextFlowSchema, None]:
            yield input_data

        # Process through the flow and get the first result
        flow = self.to_flow()
        results: list[ContextFlowSchema] = []
        async for result in flow(input_stream()):
            results.append(result)  # pyright: ignore[reportUnknownMemberType]

        if not results:
            raise ValueError("Agent produced no output")

        return results[0]

    def to_flow(self) -> Flow[ContextFlowSchema, ContextFlowSchema]:
        """Convert agent to a composable flow.

        Returns:
            Flow that implements the complete agent pipeline
        """
        return Flow(self._agent_pipeline, name=f"agent:{self.name}")

    async def _agent_pipeline(
        self, stream: AsyncGenerator[ContextFlowSchema, None]
    ) -> AsyncGenerator[ContextFlowSchema, None]:
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
            async def context_stream(
                ctx: Context = context,
            ) -> AsyncGenerator[Context, None]:
                yield ctx

            # Step 4: Process through system flow
            system_stream = context_stream()
            system_results: list[Context] = []
            async for processed_context in self.system_flow(system_stream):
                system_results.append(
                    processed_context
                )  # pyright: ignore[reportUnknownMemberType]

            # Take the last result from system flow
            if system_results:
                processed_context = system_results[
                    -1
                ]  # pyright: ignore[reportUnknownVariableType]
            else:
                processed_context = context

            # Step 5: Process through main processing flow
            async def processing_stream(
                ctx: Context = processed_context,
            ) -> AsyncGenerator[Context, None]:
                yield ctx

            processing_stream_instance = processing_stream()
            processing_results: list[Context] = []
            async for final_context in self.processing_flow(processing_stream_instance):
                processing_results.append(
                    final_context
                )  # pyright: ignore[reportUnknownMemberType]

            # Take the last result from processing flow
            if processing_results:
                final_context = processing_results[
                    -1
                ]  # pyright: ignore[reportUnknownVariableType]
            else:
                final_context = (
                    processed_context  # pyright: ignore[reportUnknownVariableType]
                )

            # Step 6: Extract output from context
            try:
                output_data = self.output_schema.from_context(
                    final_context
                )  # pyright: ignore[reportUnknownArgumentType]
            except (KeyError, ValueError):
                # If we can't extract the output schema from context,
                # it might be because the processing flow didn't put it there
                # In that case, we need a fallback mechanism
                # Create a minimal instance with default values for required fields
                try:
                    # Try to create with minimal default values
                    field_defaults: dict[str, Any] = {}
                    for (
                        field_name,
                        field_info,
                    ) in self.output_schema.model_fields.items():
                        if field_info.is_required():
                            # Provide sensible defaults for common types
                            annotation_str = str(field_info.annotation)
                            if field_info.annotation is str:
                                field_defaults[field_name] = ""
                            elif field_info.annotation is int:
                                field_defaults[field_name] = 0
                            elif field_info.annotation is float:
                                field_defaults[field_name] = 0.0
                            elif field_info.annotation is bool:
                                field_defaults[field_name] = False
                            elif (
                                "list" in annotation_str.lower()
                                or "List" in annotation_str
                            ):
                                field_defaults[field_name] = []
                            elif (
                                "dict" in annotation_str.lower()
                                or "Dict" in annotation_str
                            ):
                                field_defaults[field_name] = {}
                            else:
                                field_defaults[field_name] = None

                    output_data = self.output_schema(**field_defaults)
                except TypeError:
                    # If schema requires arguments, we can't create a fallback
                    raise ValueError(
                        "Output schema not found in context and cannot create fallback"
                    )

            # Step 7: Validate and yield output
            if not isinstance(output_data, self.output_schema):
                validated_output = self.output_schema.model_validate(output_data)
            else:
                validated_output = output_data

            yield validated_output
