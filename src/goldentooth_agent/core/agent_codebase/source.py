"""
Simple document source model for codebase introspection.
"""

from typing import Any

from pydantic import BaseModel, Field


class DocumentSource(BaseModel):
    """Source information for documents in the codebase collection."""

    name: str = Field(..., description="Source identifier")
    display_name: str = Field(..., description="Human-readable source name")
    description: str = Field(default="", description="Source description")
    metadata: dict[str, Any] = Field(
        default_factory=dict, description="Additional metadata"
    )
