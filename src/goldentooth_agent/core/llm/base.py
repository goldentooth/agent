"""Base LLM client interface and types."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import AsyncIterator
from typing import Any, Protocol, TypeVar

from ..flow_agent import FlowIOSchema

T = TypeVar("T", bound=FlowIOSchema)


class StreamingResponse(Protocol):
    """Protocol for streaming LLM responses."""

    async def __aiter__(self) -> AsyncIterator[str]:
        """Async iterator for streaming response chunks."""
        ...

    @property
    def usage(self) -> dict[str, Any]:
        """Token usage information."""
        ...


class LLMClient(ABC):
    """Abstract base class for LLM clients."""

    @abstractmethod
    async def create_completion(
        self,
        response_model: type[T],
        messages: list[dict[str, Any]],
        model: str = "claude-3-5-sonnet-20241022",
        temperature: float = 0.1,
        max_tokens: int = 1000,
        stream: bool = False,
        **kwargs: Any,
    ) -> T | StreamingResponse:
        """Create a completion with structured output.

        Args:
            response_model: Pydantic model for response validation
            messages: List of message dictionaries
            model: Model name to use
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            stream: Whether to stream the response
            **kwargs: Additional model-specific parameters

        Returns:
            Validated response model instance or streaming response
        """
        ...

    @abstractmethod
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
            model: Model name to use
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            stream: Whether to stream the response
            **kwargs: Additional model-specific parameters

        Returns:
            Response text or streaming response
        """
        ...
