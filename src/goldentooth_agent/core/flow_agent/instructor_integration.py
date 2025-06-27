"""Instructor integration for structured LLM output with FlowAgent system."""

from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Any, TypeVar

from ..context import Context, ContextKey
from ..flow import Flow
from .schema import FlowIOSchema

T = TypeVar("T", bound=FlowIOSchema)
R = TypeVar("R", bound=FlowIOSchema)


class MockLLMClient:
    """Mock LLM client for testing purposes.

    This client simulates LLM responses for testing the Instructor integration
    without requiring actual API calls.
    """

    def __init__(self, mock_responses: dict[type[FlowIOSchema], Any] | None = None):
        """Initialize the mock client.

        Args:
            mock_responses: Optional dict mapping output schema types to mock responses
        """
        self.mock_responses = mock_responses or {}

    async def create_completion(
        self,
        response_model: type[R],
        messages: list[dict[str, Any]],
        model: str = "gpt-4",
        **kwargs: Any,
    ) -> R:
        """Mock completion creation that returns predefined responses.

        Args:
            response_model: The Pydantic model class for the response
            messages: List of message dictionaries
            model: Model name (ignored in mock)
            **kwargs: Additional arguments (ignored in mock)

        Returns:
            Mock response of the specified type

        Raises:
            ValueError: If no mock response is configured for the response model
        """
        if response_model in self.mock_responses:
            return self.mock_responses[response_model]  # type: ignore[no-any-return]

        # Try to create a default instance if possible
        try:
            # For testing, return a basic instance with minimal valid data
            if hasattr(response_model, "model_fields"):
                # Create with minimal required fields
                field_defaults: dict[str, Any] = {}
                for field_name, field_info in response_model.model_fields.items():
                    if field_info.is_required():
                        annotation_str = str(field_info.annotation)
                        if field_info.annotation is str:
                            field_defaults[field_name] = f"mock_{field_name}"
                        elif field_info.annotation is int:
                            field_defaults[field_name] = 0
                        elif field_info.annotation is float:
                            field_defaults[field_name] = 0.0
                        elif field_info.annotation is bool:
                            field_defaults[field_name] = True
                        elif (
                            "list" in annotation_str.lower() or "List" in annotation_str
                        ):
                            field_defaults[field_name] = []
                        else:
                            field_defaults[field_name] = None

                return response_model(**field_defaults)
            else:
                return response_model()
        except Exception as e:
            raise ValueError(
                f"No mock response configured for {response_model.__name__}"
            ) from e


class InstructorFlow:
    """Flow-based wrapper for Instructor-powered structured LLM output.

    InstructorFlow integrates with the FlowAgent system to provide structured
    LLM output using Instructor's validation and parsing capabilities.
    """

    def __init__(
        self,
        client: Any,  # LLM client (OpenAI, Anthropic, etc.)
        model: str,
        input_schema: type[T],
        output_schema: type[R],
        system_prompt: str | None = None,
        max_retries: int = 3,
        temperature: float = 0.1,
    ):
        """Initialize an InstructorFlow.

        Args:
            client: LLM client instance (should be instructor-patched)
            model: Model name to use for completions
            input_schema: Pydantic schema class for input validation
            output_schema: Pydantic schema class for output validation
            system_prompt: Optional system prompt to prepend to conversations
            max_retries: Maximum number of retries for failed completions
            temperature: Temperature for LLM completions
        """
        self.client = client
        self.model = model
        self.input_schema = input_schema
        self.output_schema = output_schema
        self.system_prompt = system_prompt
        self.max_retries = max_retries
        self.temperature = temperature

    def as_flow(self) -> Flow[Context, Context]:
        """Convert InstructorFlow to a composable Flow.

        Returns:
            Flow that processes contexts through structured LLM completion
        """
        return Flow(self._instructor_pipeline, name=f"instructor:{self.model}")

    async def _instructor_pipeline(
        self, stream: AsyncIterator[Context]
    ) -> AsyncIterator[Context]:
        """Implementation of the instructor pipeline.

        This pipeline:
        1. Extracts input schema from context
        2. Converts to messages format
        3. Calls LLM with Instructor for structured output
        4. Adds output schema back to context
        """
        async for context in stream:
            try:
                # Step 1: Extract input from context
                input_data = self._extract_input_from_context(context)

                # Step 2: Convert to messages format
                messages = self._build_messages(input_data)

                # Step 3: Call LLM with structured output
                output_data = await self._call_llm_with_instructor(messages)

                # Step 4: Add output to context and yield
                updated_context = output_data.to_context(context)
                yield updated_context

            except Exception as e:
                # For now, re-raise errors
                # In a production system, we might want more sophisticated error handling
                raise e

    def _extract_input_from_context(self, context: Context) -> FlowIOSchema:
        """Extract input schema from context.

        Args:
            context: Context containing input data

        Returns:
            Validated input schema instance

        Raises:
            ValueError: If input cannot be extracted or validated
        """
        try:
            return self.input_schema.from_context(context)
        except (KeyError, ValueError) as e:
            raise ValueError(
                f"Failed to extract {self.input_schema.__name__} from context: {e}"
            ) from e

    def _build_messages(self, input_data: T) -> list[dict[str, Any]]:
        """Build messages list for LLM completion.

        Args:
            input_data: Validated input schema instance

        Returns:
            List of message dictionaries for LLM completion
        """
        messages = []

        # Add system prompt if provided
        if self.system_prompt:
            messages.append({"role": "system", "content": self.system_prompt})

        # Convert input data to user message
        # This is a simple implementation - in practice, you might want
        # more sophisticated prompt templating
        user_content = self._format_input_as_prompt(input_data)
        messages.append({"role": "user", "content": user_content})

        return messages

    def _format_input_as_prompt(self, input_data: T) -> str:
        """Format input data as a prompt string.

        Args:
            input_data: Validated input schema instance

        Returns:
            Formatted prompt string
        """
        # Simple implementation - just use the model's JSON representation
        # In practice, you might want custom prompt templates per schema type
        data_dict = input_data.model_dump()

        # Create a basic prompt from the input fields
        prompt_parts = []
        for field_name, value in data_dict.items():
            if value and field_name != "context_data":  # Skip empty and context fields
                prompt_parts.append(f"{field_name.replace('_', ' ').title()}: {value}")

        return "\n".join(prompt_parts)

    async def _call_llm_with_instructor(
        self, messages: list[dict[str, Any]]
    ) -> FlowIOSchema:
        """Call LLM with Instructor for structured output.

        Args:
            messages: List of message dictionaries

        Returns:
            Validated output schema instance
        """
        try:
            # Make the instructor-powered completion call
            response = await self.client.create_completion(
                response_model=self.output_schema,
                messages=messages,
                model=self.model,
                temperature=self.temperature,
                max_retries=self.max_retries,
            )

            return response  # type: ignore[no-any-return]

        except Exception as e:
            raise ValueError(f"LLM completion failed: {e}") from e


# Context keys for common LLM operation data
SYSTEM_PROMPT_KEY = ContextKey[str]("system_prompt")
MODEL_NAME_KEY = ContextKey[str]("model_name")
TEMPERATURE_KEY = ContextKey[float]("temperature")
MAX_TOKENS_KEY = ContextKey[int]("max_tokens")
COMPLETION_METADATA_KEY = ContextKey[dict[str, Any]]("completion_metadata")


def create_instructor_flow(
    client: Any,
    model: str,
    input_schema: type[T],
    output_schema: type[R],
    system_prompt: str | None = None,
    **kwargs: Any,
) -> Flow[Context, Context]:
    """Factory function to create an InstructorFlow as a Flow.

    Args:
        client: LLM client instance
        model: Model name
        input_schema: Input schema type
        output_schema: Output schema type
        system_prompt: Optional system prompt
        **kwargs: Additional arguments passed to InstructorFlow

    Returns:
        Flow that performs structured LLM completion
    """
    instructor_flow = InstructorFlow(
        client=client,
        model=model,
        input_schema=input_schema,
        output_schema=output_schema,
        system_prompt=system_prompt,
        **kwargs,
    )

    return instructor_flow.as_flow()


# Utility function for creating system flows that add LLM configuration to context
def create_system_prompt_flow(prompt: str) -> Flow[Context, Context]:
    """Create a flow that adds a system prompt to the context.

    Args:
        prompt: System prompt text

    Returns:
        Flow that adds the system prompt to context
    """

    async def add_system_prompt(
        stream: AsyncIterator[Context],
    ) -> AsyncIterator[Context]:
        async for context in stream:
            context.set(SYSTEM_PROMPT_KEY.path, prompt)
            yield context

    return Flow(add_system_prompt, name="system_prompt")


def create_model_config_flow(
    model: str,
    temperature: float = 0.1,
    max_tokens: int | None = None,
) -> Flow[Context, Context]:
    """Create a flow that adds model configuration to the context.

    Args:
        model: Model name
        temperature: Temperature setting
        max_tokens: Optional maximum tokens

    Returns:
        Flow that adds model configuration to context
    """

    async def add_model_config(
        stream: AsyncIterator[Context],
    ) -> AsyncIterator[Context]:
        async for context in stream:
            context.set(MODEL_NAME_KEY.path, model)
            context.set(TEMPERATURE_KEY.path, temperature)

            if max_tokens is not None:
                context.set(MAX_TOKENS_KEY.path, max_tokens)

            yield context

    return Flow(add_model_config, name="model_config")
