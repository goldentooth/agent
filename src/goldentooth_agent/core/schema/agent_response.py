"""Standardized agent response schema for consistent handling across the system."""

from typing import Any

from pydantic import BaseModel, Field


class AgentResponse(BaseModel):
    """Standardized agent response schema.

    This provides a consistent interface for all agent responses,
    ensuring type safety and preventing the dictionary/object access confusion.
    """

    response: str = Field(..., description="The main response text from the agent")
    sources: list[dict[str, Any]] = Field(
        default_factory=list,
        description="Source documents or references used in the response",
    )
    confidence: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Confidence score of the response (0-1)",
    )
    suggestions: list[str] = Field(
        default_factory=list, description="Follow-up suggestions or related queries"
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict, description="Additional metadata about the response"
    )

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "AgentResponse":
        """Create AgentResponse from dictionary with validation.

        Args:
            data: Dictionary containing response data

        Returns:
            Validated AgentResponse instance
        """
        return cls(**data)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization.

        Returns:
            Dictionary representation of the response
        """
        return self.model_dump()

    model_config = {
        "validate_assignment": True,
        "extra": "forbid",  # Prevent extra fields
    }
