"""Anthropic Claude client implementation with Instructor integration."""

from __future__ import annotations

import os
from collections.abc import AsyncIterator
from typing import Any, TypeVar, cast

import instructor
from anthropic import AsyncAnthropic

from goldentooth_agent.flow_engine import Flow

from ..context import Context
from ..flow_agent import AgentInput, AgentOutput, FlowAgent, FlowIOSchema
from .base import LLMClient, StreamingResponse

T = TypeVar("T", bound=FlowIOSchema)


class ClaudeStreamingResponse:
    """Wrapper for Claude streaming responses."""

    def __init__(
        self, stream: AsyncIterator[Any], usage_info: dict[str, Any] | None = None
    ) -> None:
        self._stream = stream
        self._usage = usage_info or {}

    async def __aiter__(self) -> AsyncIterator[str]:
        """Iterate over streaming response chunks."""
        async for chunk in self._stream:
            if hasattr(chunk, "delta") and hasattr(chunk.delta, "text"):
                yield chunk.delta.text
            elif hasattr(chunk, "text"):
                yield chunk.text
            elif isinstance(chunk, str):
                yield chunk

    @property
    def usage(self) -> dict[str, Any]:
        """Token usage information."""
        return self._usage


class ClaudeFlowClient(LLMClient):
    """Anthropic Claude client with Flow integration."""

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str | None = None,
        default_model: str = "claude-3-5-sonnet-20241022",
        default_max_tokens: int = 1000,
    ) -> None:
        """Initialize Claude client.

        Args:
            api_key: Anthropic API key (defaults to ANTHROPIC_API_KEY env var)
            base_url: Optional custom API base URL
            default_model: Default model to use
            default_max_tokens: Default max tokens for responses
        """
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError(
                "Anthropic API key is required. Set ANTHROPIC_API_KEY environment variable "
                "or pass api_key parameter."
            )

        # Initialize Anthropic client
        client_kwargs = {"api_key": self.api_key}
        if base_url:
            client_kwargs["base_url"] = base_url

        self._client = AsyncAnthropic(**client_kwargs)  # type: ignore[arg-type]

        # Patch with instructor for structured output
        self._instructor_client = instructor.from_anthropic(self._client)

        self.default_model = default_model
        self.default_max_tokens = default_max_tokens

    async def create_completion(
        self,
        response_model: type[T],
        messages: list[dict[str, Any]],
        model: str | None = None,
        temperature: float = 0.1,
        max_tokens: int | None = None,
        stream: bool = False,
        **kwargs: Any,
    ) -> T | StreamingResponse:
        """Create a completion with structured output using Instructor.

        Args:
            response_model: Pydantic model for response validation
            messages: List of message dictionaries
            model: Model name (defaults to default_model)
            temperature: Sampling temperature
            max_tokens: Maximum tokens (defaults to default_max_tokens)
            stream: Whether to stream response (structured output doesn't support streaming)
            **kwargs: Additional parameters

        Returns:
            Validated response model instance

        Raises:
            ValueError: If streaming is requested (not supported with structured output)
        """
        if stream:
            raise ValueError("Streaming is not supported with structured output")

        model = model or self.default_model
        max_tokens = max_tokens or self.default_max_tokens

        # Use instructor client for structured output
        try:
            response = await self._instructor_client.messages.create(
                model=model,
                messages=messages,  # type: ignore[arg-type]
                response_model=response_model,
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs,
            )
            return response
        except Exception as e:
            raise ValueError(f"Claude completion failed: {e}") from e

    async def create_chat_completion(
        self,
        messages: list[dict[str, Any]],
        model: str = "claude-3-5-sonnet-20241022",
        temperature: float = 0.7,
        max_tokens: int = 1000,
        stream: bool = False,
        **kwargs: Any,
    ) -> str | StreamingResponse:
        """Create a chat completion without structured output.

        Args:
            messages: List of message dictionaries
            model: Model name (defaults to default_model)
            temperature: Sampling temperature
            max_tokens: Maximum tokens (defaults to default_max_tokens)
            stream: Whether to stream the response
            **kwargs: Additional parameters

        Returns:
            Response text or streaming response
        """
        try:
            # Prepare Claude API parameters
            claude_params = {
                "model": model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
                **kwargs,
            }

            # Add system message if provided in kwargs
            system = kwargs.get("system")
            if system:
                claude_params["system"] = system

            if stream:
                # Create streaming response
                claude_params["stream"] = True
                response_stream = await self._client.messages.create(**claude_params)
                return cast(StreamingResponse, ClaudeStreamingResponse(response_stream))
            else:
                # Create non-streaming response
                response = await self._client.messages.create(**claude_params)
                return response.content[0].text  # type: ignore[no-any-return]
        except Exception as e:
            raise ValueError(f"Claude chat completion failed: {e}") from e


def create_claude_agent(
    name: str = "claude_agent",
    model: str = "claude-3-5-sonnet-20241022",
    system_prompt: str | None = None,
    temperature: float = 0.7,
    max_tokens: int = 1000,
    api_key: str | None = None,
) -> FlowAgent:
    """Create a Claude-powered FlowAgent.

    Args:
        name: Agent name
        model: Claude model to use
        system_prompt: Optional system prompt
        temperature: Sampling temperature
        max_tokens: Maximum tokens per response
        api_key: Anthropic API key (defaults to env var)

    Returns:
        FlowAgent powered by Claude
    """
    # Initialize Claude client
    claude_client = ClaudeFlowClient(
        api_key=api_key,
        default_model=model,
        default_max_tokens=max_tokens,
    )

    # Create system flow that adds Claude configuration
    async def claude_system_flow(
        stream: AsyncIterator[Context],
    ) -> AsyncIterator[Context]:
        """System flow that configures Claude settings."""
        async for context in stream:
            context.set("model_name", model)
            context.set("temperature", temperature)
            context.set("max_tokens", max_tokens)
            if system_prompt:
                context.set("system_prompt", system_prompt)
            yield context

    # Create processing flow that uses Claude
    async def claude_processing_flow(
        stream: AsyncIterator[Context],
    ) -> AsyncIterator[Context]:
        """Processing flow that sends messages to Claude."""
        async for context in stream:
            try:
                # Extract input
                input_data = AgentInput.from_context(context)

                # Build messages for Claude (system message handled separately)
                messages = [{"role": "user", "content": input_data.message}]

                # Get system prompt if present
                system_msg = context.get("system_prompt", default=None)

                # Get response from Claude
                claude_kwargs: dict[str, Any] = {}
                if system_msg:
                    claude_kwargs["system"] = system_msg  # type: ignore[unreachable]

                response_text = await claude_client.create_chat_completion(
                    messages=messages,
                    model=model,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    **claude_kwargs,
                )

                # Create output
                if isinstance(response_text, str):
                    output_data = AgentOutput(
                        response=response_text,
                        metadata={
                            "model": model,
                            "temperature": temperature,
                            "agent": name,
                        },
                    )
                else:
                    # Handle streaming case (for future streaming support)
                    output_data = AgentOutput(
                        response="Streaming response not yet supported",
                        metadata={"error": "Streaming not implemented"},
                    )

                # Add output to context and yield
                yield output_data.to_context(context)

            except Exception as e:
                # Create error response
                error_output = AgentOutput(
                    response=f"Error: {str(e)}",
                    metadata={
                        "error": True,
                        "error_type": type(e).__name__,
                        "model": model,
                        "agent": name,
                    },
                )
                yield error_output.to_context(context)

    return FlowAgent(
        name=name,
        input_schema=AgentInput,
        output_schema=AgentOutput,
        system_flow=Flow(claude_system_flow, name=f"{name}_system"),
        processing_flow=Flow(claude_processing_flow, name=f"{name}_processing"),
    )
